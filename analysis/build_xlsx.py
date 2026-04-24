"""
PC26 Obj 1.1C — companion data workbook v2.

Reads intermediates from analysis/out and writes an openpyxl workbook with:
  Cover, Summary (with PI columns + conditional formatting),
  PI_Analysis (methodology + ranking + findings),
  one sheet per well (performance / completion / pressure / RM / stim / events / tests).
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule

from analysis.constants import (
    ALL_WELLS, FINAL_FIVE, BACKUP, DEFERRED, WELL_META, KEY_FINDINGS,
    RESERVOIR_CONTEXT, BHFP_DELTA, BHFP_DELTA_DEFAULT, PRES_SURVEYS,
    CONFIRMED_EVENTS, EXEC_SUMMARY_BULLETS, DATA_GAPS, CONCLUSIONS,
)
from analysis import pipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables"

NAVY = "FF0A2540"; OIL = "FFF59E0B"; PAPER = "FFFFFFFF"
INK = "FF111827"; SUB = "FF6B7280"; LINE = "FFE5E7EB"
OK_FILL  = PatternFill("solid", fgColor="FFD1FADF")  # soft green
WARN_FILL = PatternFill("solid", fgColor="FFFFF4D6") # soft amber
BAD_FILL  = PatternFill("solid", fgColor="FFFEE2E2") # soft red
TITLE = Font(name="Georgia", size=16, bold=True, color=NAVY)
SECTION = Font(name="Calibri", size=11, bold=True, color=OIL)
HEADER = Font(name="Calibri", size=10, bold=True, color=PAPER)
BODY = Font(name="Calibri", size=10, color=INK)
MUTED = Font(name="Calibri", size=9, italic=True, color=SUB)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
BAND = PatternFill("solid", fgColor="FFF3F4F6")
THIN = Side(border_style="thin", color="FFD1D5DB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)


def _autosize(ws, cols: dict[int, int]) -> None:
    for c, w in cols.items():
        ws.column_dimensions[get_column_letter(c)].width = w


def _write_cover(ws) -> None:
    ws.title = "Cover"
    ws.sheet_view.showGridLines = False
    ws["B2"] = "PC26 — Obj 1.1C"
    ws["B2"].font = Font(name="Georgia", size=22, bold=True, color=NAVY)
    ws["B3"] = "Shah SIMSIMA R1 · Stimulation Roadmap — Well Performance Data v2"
    ws["B3"].font = Font(name="Georgia", size=14, color=INK)
    ws["B4"] = "TotalEnergies ALSG × ADNOC Onshore · Issued 23-Apr-2026"
    ws["B4"].font = MUTED

    ws["B6"] = "WORKBOOK CONTENTS"
    ws["B6"].font = SECTION
    contents = [
        ("Cover", "This sheet"),
        ("Summary", "Cross-well table with PI, decline, and candidate status"),
        ("PI_Analysis", "Methodology, ranking, key findings"),
    ] + [(w, f"{WELL_META.get(w,{}).get('category','')}") for w in ALL_WELLS]
    for i, (k, v) in enumerate(contents, start=7):
        ws.cell(row=i, column=2, value=k).font = Font(bold=True, color=NAVY, name="Calibri", size=10)
        ws.cell(row=i, column=3, value=v).font = BODY

    # context
    r0 = 7 + len(contents) + 2
    ws.cell(row=r0, column=2, value="SHAH SIMSIMA R1 — RESERVOIR CONTEXT").font = SECTION
    for j, (k, v) in enumerate(RESERVOIR_CONTEXT.items(), start=r0 + 1):
        ws.cell(row=j, column=2, value=k).font = Font(bold=True, color=SUB, name="Calibri", size=10)
        ws.cell(row=j, column=3, value=v).font = BODY

    _autosize(ws, {2: 30, 3: 72})


def _write_summary(ws, summary: pd.DataFrame) -> None:
    ws.title = "Summary"
    ws["A1"] = "Summary — stimulation candidates"
    ws["A1"].font = TITLE
    ws["A2"] = ("Computed PI (BOPD/psi) with BHFP = PIP + Δ per well; "
                "Pres interpolated from formal surveys (± 365 d cap). "
                "D (%/yr) from log-linear fit of valid PI points.")
    ws["A2"].font = MUTED
    ws.merge_cells("A2:M2")

    headers = ["Well", "Category", "Status", "Tests", "PI pts",
               "Date first", "Date last", "Qo best (BOPD)", "Qo last (BOPD)",
               "PI first", "PI last", "PI Δ (%)", "D (%/yr)", "R²", "Note"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = HEADER; cell.fill = HEADER_FILL; cell.alignment = CENTRE
        cell.border = BORDER

    statcol = {"Final": OK_FILL, "Backup": WARN_FILL, "Defer": BAD_FILL}
    for i, (_, r) in enumerate(summary.iterrows(), start=5):
        row = [
            r["well"], WELL_META.get(r["well"], {}).get("category", ""),
            r["status"], int(r["tests_n"] or 0),
            int(r["pi_n"]) if pd.notna(r.get("pi_n", np.nan)) else 0,
            r.get("date_first"), r.get("date_last"),
            float(r["qo_best"]) if pd.notna(r.get("qo_best")) else None,
            float(r["qo_last"]) if pd.notna(r.get("qo_last")) else None,
            float(r["pi_first"]) if pd.notna(r.get("pi_first")) else None,
            float(r["pi_last"])  if pd.notna(r.get("pi_last"))  else None,
            float(r["pi_change_pct"]) if pd.notna(r.get("pi_change_pct")) else None,
            float(r["d_pct_yr"]) if pd.notna(r.get("d_pct_yr")) else None,
            float(r["r2"]) if pd.notna(r.get("r2")) else None,
            r.get("note", ""),
        ]
        for c, v in enumerate(row, start=1):
            cell = ws.cell(row=4 + i - 4, column=c, value=v)  # continue
            cell.font = BODY; cell.border = BORDER
            cell.alignment = CENTRE if c in (3, 4, 5) else LEFT
        # status pill
        fill = statcol.get(r["status"])
        if fill is not None:
            ws.cell(row=4 + i - 4, column=3).fill = fill
        # number format
        for nc, nf in ((6, "yyyy-mm-dd"), (7, "yyyy-mm-dd"),
                       (8, "0"), (9, "0"), (10, "0.00"), (11, "0.00"),
                       (12, "+0.0;-0.0"), (13, "+0.0;-0.0"), (14, "0.00")):
            ws.cell(row=4 + i - 4, column=nc).number_format = nf

    n_rows = len(summary)
    # conditional formatting on D (%/yr) — col 13
    col_d = get_column_letter(13)
    rng = f"{col_d}5:{col_d}{4+n_rows}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual",
        formula=["40"], fill=PatternFill("solid", fgColor="FFFCA5A5")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="between",
        formula=["15","40"], fill=PatternFill("solid", fgColor="FFFDE68A")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan",
        formula=["15"], fill=PatternFill("solid", fgColor="FFBBF7D0")))

    ws.freeze_panes = "A5"
    _autosize(ws, {1:10, 2:44, 3:10, 4:7, 5:7, 6:12, 7:12,
                    8:12, 9:12, 10:9, 11:9, 12:10, 13:10, 14:7, 15:40})


def _write_pi_analysis(ws, summary: pd.DataFrame, decline: pd.DataFrame) -> None:
    ws.title = "PI_Analysis"
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Productivity Index — methodology, ranking, key findings"
    ws["A1"].font = TITLE

    ws["A3"] = "1. METHODOLOGY"
    ws["A3"].font = SECTION
    lines = [
        ("PI definition", "PI = Qo / (Pres − BHFP)   [BOPD/psi]"),
        ("BHFP", "BHFP = PIP + Δ_well, where Δ is a per-well calibration (psi) taken from the Q2-2026 Allowable workbook."),
        ("Pres", "Piece-wise-linear interpolation between formal downhole surveys (BHCIP / GRAD). Extrapolation capped at ±365 days beyond the nearest survey."),
        ("Drop filter", "Tests where drawdown < 30 psi or > 2,500 psi are treated as unphysical and excluded."),
        ("Decline fit", "Log-linear fit  ln(PI) = a + b · t   (years) → D_%/yr = (1 − exp(b))·100.  Full valid window per well."),
    ]
    for i, (k, v) in enumerate(lines, start=4):
        ws.cell(row=i, column=1, value=k).font = Font(bold=True, color=NAVY, name="Calibri", size=10)
        ws.cell(row=i, column=2, value=v).font = BODY

    r = 4 + len(lines) + 2
    ws.cell(row=r, column=1, value="BHFP calibration Δ (psi)").font = SECTION
    r += 1
    ws.cell(row=r, column=1, value="Well").font = HEADER
    ws.cell(row=r, column=1).fill = HEADER_FILL
    ws.cell(row=r, column=2, value="Δ (psi)").font = HEADER
    ws.cell(row=r, column=2).fill = HEADER_FILL
    for i, (w, d) in enumerate(BHFP_DELTA.items(), start=r + 1):
        ws.cell(row=i, column=1, value=w).font = BODY
        ws.cell(row=i, column=2, value=d).font = BODY
    ws.cell(row=r + len(BHFP_DELTA) + 1, column=1, value="Default (unlisted wells)").font = BODY
    ws.cell(row=r + len(BHFP_DELTA) + 1, column=2, value=BHFP_DELTA_DEFAULT).font = BODY

    r2 = r + len(BHFP_DELTA) + 3
    ws.cell(row=r2, column=1, value="2. RANKING  (by D %/yr, descending)").font = SECTION
    head = ["Rank", "Well", "D (%/yr)", "R²", "PI first", "PI last", "PI Δ (%)", "Status"]
    for c, h in enumerate(head, start=1):
        cell = ws.cell(row=r2 + 1, column=c, value=h)
        cell.font = HEADER; cell.fill = HEADER_FILL; cell.alignment = CENTRE
    s = summary.sort_values("d_pct_yr", ascending=False, na_position="last").reset_index(drop=True)
    for i, (_, row) in enumerate(s.iterrows(), start=r2 + 2):
        ws.cell(row=i, column=1, value=i - (r2 + 1)).font = BODY
        ws.cell(row=i, column=2, value=row["well"]).font = BODY
        ws.cell(row=i, column=3,
                value=float(row["d_pct_yr"]) if pd.notna(row.get("d_pct_yr")) else None).number_format = "+0.0;-0.0"
        ws.cell(row=i, column=4,
                value=float(row["r2"]) if pd.notna(row.get("r2")) else None).number_format = "0.00"
        ws.cell(row=i, column=5,
                value=float(row["pi_first"]) if pd.notna(row.get("pi_first")) else None).number_format = "0.00"
        ws.cell(row=i, column=6,
                value=float(row["pi_last"]) if pd.notna(row.get("pi_last")) else None).number_format = "0.00"
        ws.cell(row=i, column=7,
                value=float(row["pi_change_pct"]) if pd.notna(row.get("pi_change_pct")) else None).number_format = "+0.0;-0.0"
        ws.cell(row=i, column=8, value=row["status"]).font = BODY

    r3 = r2 + 2 + len(s) + 2
    ws.cell(row=r3, column=1, value="3. KEY FINDINGS  (verbatim)").font = SECTION
    for i, w in enumerate(ALL_WELLS, start=r3 + 1):
        ws.cell(row=i, column=1, value=w).font = Font(bold=True, color=NAVY, name="Calibri", size=10)
        ws.cell(row=i, column=2, value=KEY_FINDINGS.get(w, "")).font = BODY
        ws.cell(row=i, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[i].height = 48

    _autosize(ws, {1: 22, 2: 110, 3: 11, 4: 7, 5: 10, 6: 10, 7: 10, 8: 10})


def _write_well_sheet(ws, well: str, tests: pd.DataFrame, decline: pd.DataFrame,
                      events: pd.DataFrame, summary: pd.DataFrame) -> None:
    ws.title = well
    ws.sheet_view.showGridLines = False
    meta = WELL_META.get(well, {})
    s = summary[summary["well"] == well].iloc[0]
    d = decline[decline["well"] == well]
    d = d.iloc[0] if len(d) else {}

    ws["A1"] = f"{well} — {meta.get('reservoir','')} {meta.get('type','')}"
    ws["A1"].font = TITLE
    ws["A2"] = (f"Category: {meta.get('category','')} · Station: {meta.get('station','')} "
                f"· Completion: {meta.get('completion','')}")
    ws["A2"].font = MUTED

    # 1. Performance snapshot
    r = 4
    ws.cell(row=r, column=1, value="1. PERFORMANCE SNAPSHOT").font = SECTION
    snap = [
        ("Allowable rate", f"{meta.get('allowable','')} BOPD"),
        ("Technical rate (TR)", f"{meta.get('tr','')} BOPD"),
        ("SH guideline cap", f"{meta.get('sh_cap','')} BOPD"),
        ("Tests on record", s["tests_n"]),
        ("Valid PI points", int(s["pi_n"]) if pd.notna(s.get("pi_n", np.nan)) else 0),
        ("Date range", f"{s['date_first'].date() if pd.notna(s.get('date_first')) else '—'} → "
                       f"{s['date_last'].date() if pd.notna(s.get('date_last')) else '—'}"),
        ("Qo first (BOPD)",  f"{s['qo_first']:.0f}" if pd.notna(s.get('qo_first'))  else "—"),
        ("Qo best (BOPD)",   f"{s['qo_best']:.0f}"  if pd.notna(s.get('qo_best'))   else "—"),
        ("Qo last (BOPD)",   f"{s['qo_last']:.0f}"  if pd.notna(s.get('qo_last'))   else "—"),
        ("WC last (%)",      f"{s['wc_last']:.1f}"  if pd.notna(s.get('wc_last'))   else "—"),
        ("PIP last (psig)",  f"{s['pip_last']:.0f}" if pd.notna(s.get('pip_last'))  else "—"),
        ("PI first",         f"{s['pi_first']:.2f} BOPD/psi" if pd.notna(s.get('pi_first')) else "not computable"),
        ("PI last",          f"{s['pi_last']:.2f} BOPD/psi"  if pd.notna(s.get('pi_last'))  else "not computable"),
        ("PI Δ (%)",         f"{s['pi_change_pct']:+.1f}%"   if pd.notna(s.get('pi_change_pct')) else "—"),
        ("D (%/yr)",         f"{s['d_pct_yr']:+.1f} %/yr (R²={s['r2']:.2f})" if pd.notna(s.get('d_pct_yr')) else "—"),
    ]
    for i, (k, v) in enumerate(snap, start=r + 1):
        ws.cell(row=i, column=1, value=k).font = Font(bold=True, color=SUB, name="Calibri", size=10)
        ws.cell(row=i, column=2, value=v).font = BODY
    r = r + 1 + len(snap) + 1

    # 2. Pressure surveys
    ws.cell(row=r, column=1, value="2. FORMAL PRESSURE SURVEYS (Pres @ 3900 ft)").font = SECTION
    r += 1
    for c, h in enumerate(["Date", "Test type", "Pres @ datum (psi)"], start=1):
        ws.cell(row=r, column=c, value=h).font = HEADER
        ws.cell(row=r, column=c).fill = HEADER_FILL
    for i, (dte, p, lbl) in enumerate(PRES_SURVEYS.get(well, []), start=r + 1):
        ws.cell(row=i, column=1, value=dte).number_format = "yyyy-mm-dd"
        ws.cell(row=i, column=2, value=lbl).font = BODY
        ws.cell(row=i, column=3, value=p).number_format = "0.0"
    r = r + 1 + max(1, len(PRES_SURVEYS.get(well, []))) + 1

    # 3. Events
    ws.cell(row=r, column=1, value="3. EVENTS").font = SECTION
    r += 1
    for c, h in enumerate(["Date", "Type", "Confidence"], start=1):
        ws.cell(row=r, column=c, value=h).font = HEADER
        ws.cell(row=r, column=c).fill = HEADER_FILL
    sub = events[events["well"] == well].sort_values("date")
    for i, (_, e) in enumerate(sub.iterrows(), start=r + 1):
        ws.cell(row=i, column=1, value=e["date"].date()).number_format = "yyyy-mm-dd"
        ws.cell(row=i, column=2, value=e["label"]).font = BODY
        ws.cell(row=i, column=3, value=e["confidence"]).font = BODY
    r = r + 1 + max(1, len(sub)) + 1

    # 4. RM comment + key finding (verbatim)
    ws.cell(row=r, column=1, value="4. RESERVOIR-ENGINEERING COMMENT / KEY FINDING").font = SECTION
    ws.cell(row=r + 1, column=1, value="Key finding").font = Font(bold=True, color=SUB, name="Calibri", size=10)
    ws.cell(row=r + 1, column=2, value=KEY_FINDINGS.get(well, "")).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r + 1].height = 80
    r += 3

    # 5. Full test history
    ws.cell(row=r, column=1, value=f"5. FULL TEST HISTORY ({int(s['tests_n'])} tests)").font = SECTION
    r += 1
    cols = ["Date", "Qo (BOPD)", "Qw (BWPD)", "WC (%)", "GOR (scf/bbl)", "Qg (MSCF/d)",
            "PIP (psig)", "BHFP (psi)", "Pres (psi)", "Drawdown (psi)",
            "PI (BOPD/psi)", "Freq (Hz)", "Choke (1/64)"]
    for c, h in enumerate(cols, start=1):
        ws.cell(row=r, column=c, value=h).font = HEADER
        ws.cell(row=r, column=c).fill = HEADER_FILL
    g = tests[tests["well"] == well].sort_values("date").reset_index(drop=True)
    for i, (_, row) in enumerate(g.iterrows(), start=r + 1):
        vals = [
            row["date"].date() if pd.notna(row["date"]) else None,
            row.get("qo_bopd"), row.get("qw_bwpd"), row.get("wc_pct"),
            row.get("gor_scfbbl"), row.get("qg_mscfd"),
            row.get("pip_psig"),
            row.get("bhfp_psi"),
            row.get("pres_psi"),
            row.get("drawdown_psi"),
            row.get("pi_bopd_psi") if row.get("pi_valid") else None,
            row.get("freq_hz"), row.get("choke"),
        ]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=i, column=c,
                           value=float(v) if isinstance(v, (int, float, np.floating)) and pd.notna(v) else v)
            cell.font = BODY
        ws.cell(row=i, column=1).number_format = "yyyy-mm-dd"
        for cc, fmt in ((2, "0.0"), (3, "0.0"), (4, "0.0"), (5, "0"), (6, "0.00"),
                        (7, "0"), (8, "0"), (9, "0"), (10, "0"), (11, "0.000"),
                        (12, "0"), (13, "0")):
            ws.cell(row=i, column=cc).number_format = fmt
        if i % 2 == 0:
            for c in range(1, len(cols) + 1):
                ws.cell(row=i, column=c).fill = BAND

    ws.freeze_panes = ws.cell(row=r + 1, column=1)
    _autosize(ws, {1: 13, 2: 10, 3: 10, 4: 8, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10,
                    10: 11, 11: 13, 12: 9, 13: 9})


def build_xlsx() -> None:
    res = pipeline.run()
    tests = res["tests"]; decline = res["decline"]
    events = res["events"]; summary = res["summary"]

    wb = Workbook()
    _write_cover(wb.active)
    _write_summary(wb.create_sheet("Summary"), summary)
    _write_pi_analysis(wb.create_sheet("PI_Analysis"), summary, decline)
    for w in ALL_WELLS:
        _write_well_sheet(wb.create_sheet(w), w, tests, decline, events, summary)

    path = OUT / "PC26_1.1C_Well_Performance_Data_v2.xlsx"
    wb.save(path)
    print(f"Wrote {path} ({path.stat().st_size/1024:.0f} KB, {len(wb.sheetnames)} sheets)")


if __name__ == "__main__":
    build_xlsx()
