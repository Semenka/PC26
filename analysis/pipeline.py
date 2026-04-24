"""
PC26 Obj 1.1C — analytical pipeline.

Reads R1 production-test workbook, computes per-well PI using BHFP = PIP + Δ
and Pres from linearly-interpolated formal survey anchors, fits log-linear
decline, detects confirmed + inferred events, and persists intermediates to
analysis/out for the HTML/XLSX/PPTX renderers.
"""
from __future__ import annotations
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from analysis.constants import (
    ALL_WELLS, WELL_ALIAS, BHFP_DELTA, BHFP_DELTA_DEFAULT,
    DRAWDOWN_MIN, DRAWDOWN_MAX, PRES_EXTRAP_CAP_DAYS,
    PRES_SURVEYS, CONFIRMED_EVENTS,
    STEP_UP_PCT, STEP_UP_WINDOW, STEP_UP_MIN_GAP_DAYS,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "out"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_r1(path: Path) -> pd.DataFrame:
    """Read the R1 production-test workbook → normalised dataframe."""
    raw = pd.read_excel(path, sheet_name="Sheet1", header=1, engine="openpyxl")
    # strip column whitespace
    raw.columns = [str(c).replace("\n", " ").strip() for c in raw.columns]
    # R1 has a leading blank column
    cols = {
        "Well/ String":                     "well_raw",
        "Reservoir Name":                   "reservoir",
        "Test Date & Time":                 "date",
        "Station":                          "station",
        "Test Type":                        "test_type",
        "Choke Size (1/64\")":              "choke",
        "Freq (Hz)":                        "freq_hz",
        "Intake Press. (PSIG)":             "pip_psig",
        "Discharge Press. (PSIG)":          "pdp_psig",
        "Sep. Press. (PSIG)":               "psep_psig",
        "Oil Net (Bbl/D)":                  "qo_bopd",
        "Net Water Rate (Stb/d)":           "qw_bwpd",
        "Water % (Net Oil)   (% Vol.)":     "wc_pct",
        "GOR (Net Oil) (SCF /Bbl)":         "gor_scfbbl",
        "Total Form. Gas Rate (MSCF/D)":    "qg_mscfd",
    }
    df = raw[[c for c in cols if c in raw.columns]].rename(columns=cols).copy()
    df = df.dropna(subset=["well_raw", "date"])
    df["well"] = df["well_raw"].map(WELL_ALIAS).fillna(df["well_raw"])
    df = df[df["well"].isin(ALL_WELLS)].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    for c in ("qo_bopd", "qw_bwpd", "wc_pct", "gor_scfbbl", "qg_mscfd",
             "pip_psig", "pdp_psig", "psep_psig", "freq_hz", "choke"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # daily production tests only
    df = df[df["test_type"].astype(str).str.upper().isin(
        {"TP", "TC", "MR", "U", "OP"})].copy()
    df = df.sort_values(["well", "date"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Pres interpolation
# ---------------------------------------------------------------------------
def pres_series(well: str, test_dates: pd.Series) -> pd.Series:
    """Piece-wise-linear Pres at each test date, capped ±365 d extrapolation."""
    anchors = PRES_SURVEYS.get(well, [])
    if not anchors:
        return pd.Series(np.nan, index=test_dates.index)
    xs = np.array([(d - date(2000, 1, 1)).days for d, _, _ in anchors], dtype=float)
    ys = np.array([p for _, p, _ in anchors], dtype=float)
    ts = np.array([(d.date() - date(2000, 1, 1)).days for d in test_dates], dtype=float)

    out = np.full_like(ts, np.nan, dtype=float)
    if len(xs) == 1:
        mask = np.abs(ts - xs[0]) <= PRES_EXTRAP_CAP_DAYS
        out[mask] = ys[0]
        return pd.Series(out, index=test_dates.index)

    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    # within span: interpolate; outside span: capped extrapolation of nearest slope
    in_span = (ts >= xs[0]) & (ts <= xs[-1])
    out[in_span] = np.interp(ts[in_span], xs, ys)
    # left extrap
    left = ts < xs[0]
    if left.any():
        slope = (ys[1] - ys[0]) / (xs[1] - xs[0]) if len(xs) >= 2 else 0.0
        extrap = ys[0] + slope * (ts[left] - xs[0])
        out[left] = np.where(xs[0] - ts[left] <= PRES_EXTRAP_CAP_DAYS, extrap, np.nan)
    # right extrap
    right = ts > xs[-1]
    if right.any():
        slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) if len(xs) >= 2 else 0.0
        extrap = ys[-1] + slope * (ts[right] - xs[-1])
        out[right] = np.where(ts[right] - xs[-1] <= PRES_EXTRAP_CAP_DAYS, extrap, np.nan)
    return pd.Series(out, index=test_dates.index)


# ---------------------------------------------------------------------------
# PI per test
# ---------------------------------------------------------------------------
def compute_pi(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for well, g in df.groupby("well", sort=False):
        g = g.copy()
        delta = BHFP_DELTA.get(well, BHFP_DELTA_DEFAULT)
        g["bhfp_delta"] = delta
        g["bhfp_psi"] = g["pip_psig"] + delta
        g["pres_psi"] = pres_series(well, g["date"])
        g["drawdown_psi"] = g["pres_psi"] - g["bhfp_psi"]
        valid = (
            g["qo_bopd"].gt(0)
            & g["bhfp_psi"].gt(0)
            & g["pres_psi"].notna()
            & g["drawdown_psi"].ge(DRAWDOWN_MIN)
            & g["drawdown_psi"].le(DRAWDOWN_MAX)
        )
        g["pi_valid"] = valid
        g["pi_bopd_psi"] = np.where(valid, g["qo_bopd"] / g["drawdown_psi"], np.nan)
        out.append(g)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------------------
# Log-linear decline fit (per well)
# ---------------------------------------------------------------------------
def fit_decline(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for well, g in df.groupby("well", sort=False):
        v = g[g["pi_valid"] & g["pi_bopd_psi"].gt(0)].copy()
        if len(v) < 3:
            rows.append(dict(well=well, n_points=len(v),
                             pi_first=np.nan, pi_last=np.nan,
                             date_first=pd.NaT, date_last=pd.NaT,
                             slope=np.nan, intercept=np.nan, r2=np.nan,
                             d_pct_yr=np.nan, valid=False,
                             note="insufficient valid PI points"))
            continue
        v["t_yr"] = (v["date"] - v["date"].min()).dt.total_seconds() / (365.25 * 86400)
        ln_pi = np.log(v["pi_bopd_psi"].to_numpy())
        fit = stats.linregress(v["t_yr"].to_numpy(), ln_pi)
        d_pct_yr = (1 - np.exp(fit.slope)) * 100  # positive = decline
        rows.append(dict(
            well=well,
            n_points=len(v),
            pi_first=float(v.iloc[0]["pi_bopd_psi"]),
            pi_last=float(v.iloc[-1]["pi_bopd_psi"]),
            date_first=v.iloc[0]["date"],
            date_last=v.iloc[-1]["date"],
            slope=float(fit.slope),
            intercept=float(fit.intercept),
            r2=float(fit.rvalue ** 2),
            d_pct_yr=float(d_pct_yr),
            valid=True,
            note="",
        ))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Event detection
# ---------------------------------------------------------------------------
def detect_events(df: pd.DataFrame) -> pd.DataFrame:
    """Confirmed events from constants + Qo step-up inferred events."""
    rows = []
    for well, dates in CONFIRMED_EVENTS.items():
        for d, label in dates:
            rows.append(dict(well=well, date=pd.Timestamp(d),
                             label=label, confidence="confirmed"))

    for well, g in df.groupby("well", sort=False):
        g = g.sort_values("date")
        qo = g["qo_bopd"].astype(float).to_numpy()
        dts = g["date"].to_numpy()
        if len(qo) < STEP_UP_WINDOW + 3:
            continue
        rolling = pd.Series(qo).rolling(window=5, min_periods=3).median().to_numpy()
        last_event: np.datetime64 | None = None
        for i in range(3, len(qo) - STEP_UP_WINDOW):
            base = rolling[i - 1]
            if not np.isfinite(base) or base <= 0:
                continue
            window = qo[i : i + STEP_UP_WINDOW]
            if not np.all(np.isfinite(window)):
                continue
            if np.all(window >= base * (1 + STEP_UP_PCT)):
                if (last_event is not None and
                        (dts[i] - last_event) / np.timedelta64(1, "D") < STEP_UP_MIN_GAP_DAYS):
                    continue
                # skip if within ±30 d of a confirmed event
                too_close = False
                for cd, _ in CONFIRMED_EVENTS.get(well, []):
                    if abs((pd.Timestamp(dts[i]) - pd.Timestamp(cd)).days) < 30:
                        too_close = True
                        break
                if too_close:
                    continue
                rows.append(dict(
                    well=well, date=pd.Timestamp(dts[i]),
                    label=f"Qo step-up +{(window.mean() / base - 1) * 100:.0f}%",
                    confidence="inferred",
                ))
                last_event = dts[i]
    ev = pd.DataFrame(rows).sort_values(["well", "date"]).reset_index(drop=True)
    return ev


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def build_summary(tests: pd.DataFrame, decline: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for well in ALL_WELLS:
        g = tests[tests["well"] == well]
        d = decline[decline["well"] == well]
        d = d.iloc[0].to_dict() if len(d) else {}
        if g.empty:
            rows.append(dict(well=well, tests_n=0))
            continue
        rows.append(dict(
            well=well,
            tests_n=len(g),
            date_first=g["date"].min(),
            date_last=g["date"].max(),
            qo_first=float(g.iloc[0]["qo_bopd"]) if pd.notna(g.iloc[0]["qo_bopd"]) else np.nan,
            qo_best=float(g["qo_bopd"].max()) if g["qo_bopd"].notna().any() else np.nan,
            qo_best_date=g.loc[g["qo_bopd"].idxmax(), "date"] if g["qo_bopd"].notna().any() else pd.NaT,
            qo_last=float(g.iloc[-1]["qo_bopd"]) if pd.notna(g.iloc[-1]["qo_bopd"]) else np.nan,
            wc_last=float(g.iloc[-1]["wc_pct"]) if pd.notna(g.iloc[-1]["wc_pct"]) else np.nan,
            pip_last=float(g.iloc[-1]["pip_psig"]) if pd.notna(g.iloc[-1]["pip_psig"]) else np.nan,
            pi_first=d.get("pi_first", np.nan),
            pi_last=d.get("pi_last", np.nan),
            d_pct_yr=d.get("d_pct_yr", np.nan),
            r2=d.get("r2", np.nan),
            pi_n=d.get("n_points", 0),
            pi_valid=d.get("valid", False),
            note=d.get("note", ""),
        ))
    return pd.DataFrame(rows)


def classify(row) -> str:
    """Assign candidate status per approved logic."""
    from analysis.constants import FINAL_FIVE, BACKUP, DEFERRED
    w = row["well"]
    if w in FINAL_FIVE:
        return "Final"
    if w in BACKUP:
        return "Backup"
    if w in DEFERRED:
        return "Defer"
    return "—"


def pi_change_pct(row) -> float:
    f, l = row.get("pi_first"), row.get("pi_last")
    if pd.isna(f) or pd.isna(l) or f == 0:
        return np.nan
    return (l / f - 1) * 100


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run(r1_path: Path = ROOT / "data" / "raw" / "R1_well_candidates.xlsx",
        write: bool = True) -> dict:
    tests = load_r1(r1_path)
    pi_df = compute_pi(tests)
    decline = fit_decline(pi_df)
    events = detect_events(pi_df)
    summary = build_summary(pi_df, decline)
    summary["status"] = summary.apply(classify, axis=1)
    summary["pi_change_pct"] = summary.apply(pi_change_pct, axis=1)

    if write:
        pi_df.to_pickle(OUT / "tests.pkl")
        pi_df.to_csv(OUT / "tests.csv", index=False)
        decline.to_csv(OUT / "pi_ranking.csv", index=False)
        events.to_csv(OUT / "events.csv", index=False)
        summary.to_csv(OUT / "summary.csv", index=False)
        with open(OUT / "pres_surveys.json", "w") as f:
            json.dump({k: [(d.isoformat(), p, t) for d, p, t in v]
                       for k, v in PRES_SURVEYS.items()}, f, indent=2)
    return dict(tests=pi_df, decline=decline, events=events, summary=summary)


def print_verification(res: dict) -> None:
    s = res["summary"].copy()
    s["pi_first"] = s["pi_first"].round(2)
    s["pi_last"] = s["pi_last"].round(2)
    s["d_pct_yr"] = s["d_pct_yr"].round(1)
    s["r2"] = s["r2"].round(3)
    s["pi_change_pct"] = s["pi_change_pct"].round(1)
    cols = ["well", "status", "tests_n", "pi_n", "pi_first", "pi_last",
            "pi_change_pct", "d_pct_yr", "r2", "qo_best", "qo_last",
            "wc_last", "note"]
    with pd.option_context("display.max_colwidth", 60, "display.width", 200):
        print(s[cols].to_string(index=False))
    print(f"\nEvents detected: confirmed={sum(res['events']['confidence']=='confirmed')}, "
          f"inferred={sum(res['events']['confidence']=='inferred')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    res = run()
    if args.verify:
        print_verification(res)
