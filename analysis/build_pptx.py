"""
PC26 Obj 1.1C — Stimulation Candidates presentation (12 slides, LAYOUT_WIDE,
navy + oil palette, Georgia/Calibri pairing).

Renders matplotlib charts to PNGs in qa/charts/ and assembles the deck.
"""
from __future__ import annotations
from pathlib import Path
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from analysis.constants import (
    ALL_WELLS, FINAL_FIVE, BACKUP, DEFERRED, PALETTE, WELL_META,
    KEY_FINDINGS, RESERVOIR_CONTEXT, EXEC_SUMMARY_BULLETS, DATA_GAPS,
    CONCLUSIONS, CONFIRMED_EVENTS, PRES_SURVEYS,
)
from analysis import pipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables"
CHARTS = ROOT / "qa" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# --- palette (RGB tuples for matplotlib / pptx) --------------------------
NAVY = "#0A2540"; OIL = "#F59E0B"
INK = "#111827"; MUTED = "#6B7280"; PAPER = "#FFFFFF"
LINE_COLOR = "#E5E7EB"
CONF = PALETTE["confirmed"]; INFER = PALETTE["inferred"]
FINAL_FILL = "#F0FDF4"; BACKUP_FILL = "#FEF3C7"; DEFER_FILL = "#FEE2E2"


def rgb(hex_: str) -> RGBColor:
    h = hex_.lstrip("#")
    return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Matplotlib chart renderers (→ PNG for pptx.add_picture)
# ---------------------------------------------------------------------------
def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(alpha=0.25, color=LINE_COLOR)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))


def _add_events(ax, well: str, events: pd.DataFrame):
    sub = events[events["well"] == well]
    for _, e in sub.iterrows():
        is_conf = e["confidence"] == "confirmed"
        ax.axvline(e["date"], color=CONF if is_conf else INFER,
                   linestyle="-" if is_conf else "--", lw=1.2, alpha=0.85)


def chart_injector_pressure(well: str, events: pd.DataFrame, path: Path) -> None:
    """Alternate chart for water injectors / wells with no R1 test data:
    plot only the formal Pres survey anchors + event markers."""
    anchors = PRES_SURVEYS.get(well, [])
    fig, ax = plt.subplots(figsize=(6.3, 4.6))
    if anchors:
        xs = [pd.Timestamp(a[0]) for a in anchors]
        ys = [a[1] for a in anchors]
        labels = [a[2] for a in anchors]
        ax.plot(xs, ys, "-o", color=OIL, lw=1.8, ms=10, mec=NAVY, mew=1)
        # y-room so annotations below markers don't run off
        ymin, ymax = min(ys), max(ys)
        pad = (ymax - ymin) * 0.28 if ymax != ymin else 50
        ax.set_ylim(ymin - pad, ymax + pad * 0.5)
        # widen x-range so the latest annotation doesn't clip the right edge
        span = (xs[-1] - xs[0]).days or 30
        ax.set_xlim(xs[0] - pd.Timedelta(days=span * 0.10),
                     xs[-1] + pd.Timedelta(days=span * 0.30))
        for i, (x, y, lab) in enumerate(zip(xs, ys, labels)):
            # alternate above/below so labels don't stack
            dy = 20 if i % 2 == 0 else -40
            ax.annotate(f"{lab}\n{y:.0f} psi", xy=(x, y),
                        xytext=(10, dy), textcoords="offset points",
                        fontsize=9, color=INK,
                        bbox=dict(boxstyle="round,pad=0.3", fc=FINAL_FILL,
                                  ec=LINE_COLOR),
                        arrowprops=dict(arrowstyle="-", color=LINE_COLOR, lw=0.8))
        if len(ys) >= 2:
            delta = ys[-1] - ys[0]
            ax.annotate(f"Δ = {delta:+.0f} psi\nover {(xs[-1]-xs[0]).days} d",
                        xy=(0.97, 0.93), xycoords="axes fraction",
                        ha="right", va="top", fontsize=11, color=NAVY,
                        fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7",
                                  ec=OIL, lw=1))
    _add_events(ax, well, events)
    _style_axes(ax)
    ax.set_title(f"{well} — pressure anchors  (no production-test data in R1)",
                 fontsize=11, color=NAVY, loc="left", fontfamily="serif",
                 pad=14)
    ax.set_ylabel("Pres @ datum 3900 ft (psi)", color=INK, fontsize=10)
    fig.subplots_adjust(top=0.88)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=PAPER)
    plt.close(fig)


def chart_production_pi(well: str, tests: pd.DataFrame, decline: pd.DataFrame,
                        events: pd.DataFrame, path: Path) -> None:
    g = tests[tests["well"] == well].sort_values("date")
    if g.empty:
        chart_injector_pressure(well, events, path)
        return
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.3, 4.6),
                                   gridspec_kw=dict(height_ratios=[1, 1]),
                                   sharex=True)
    ax.plot(g["date"], g["qo_bopd"], "-o", color=OIL, lw=1.3, ms=3.5, label="Qo (BOPD)")
    ax.set_ylabel("Qo (BOPD)", color=INK, fontsize=10)
    axw = ax.twinx()
    axw.plot(g["date"], g["wc_pct"], ":", color="#2563EB", lw=1, label="WC (%)")
    axw.set_ylabel("WC (%)", color="#2563EB", fontsize=9)
    axw.set_ylim(0, 100)
    axw.tick_params(colors="#2563EB", labelsize=8)
    _add_events(ax, well, events)
    _style_axes(ax)
    ax.set_title(f"{well} — production", fontsize=11, color=NAVY, loc="left",
                 fontfamily="serif")

    v = g[g["pi_valid"]]
    if not v.empty:
        ax2.semilogy(v["date"], v["pi_bopd_psi"], "o", color=OIL, ms=4, alpha=0.85,
                     label="PI points")
        dd = decline[decline["well"] == well]
        if len(dd) and dd.iloc[0]["valid"]:
            d = dd.iloc[0]
            t0 = v["date"].min()
            tyr = (v["date"] - t0).dt.total_seconds() / (365.25 * 86400)
            ax2.plot(v["date"], np.exp(d["intercept"] + d["slope"] * tyr),
                     "-", color=CONF if d["d_pct_yr"] > 0 else "#818CF8", lw=2,
                     label=f"Fit: D={d['d_pct_yr']:+.0f} %/yr, R²={d['r2']:.2f}")
        ax2.legend(loc="best", fontsize=8, frameon=False)
    else:
        ax2.text(0.5, 0.5, "PI NOT COMPUTABLE", transform=ax2.transAxes,
                 ha="center", va="center", color=OIL, fontsize=13,
                 fontweight="bold")
    _add_events(ax2, well, events)
    _style_axes(ax2)
    ax2.set_ylabel("PI (BOPD/psi)")
    ax2.set_title("Productivity Index + fit", fontsize=11, color=NAVY, loc="left",
                  fontfamily="serif")
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=PAPER)
    plt.close(fig)


def chart_pi_ranking(summary: pd.DataFrame, path: Path) -> None:
    s = summary.copy()
    s = s.sort_values("d_pct_yr", ascending=True, na_position="first")
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    vals = s["d_pct_yr"].fillna(0).to_numpy()
    colors = [CONF if v > 15 else OIL if v > 0 else "#818CF8" for v in vals]
    bars = ax.barh(s["well"], vals, color=colors, edgecolor=NAVY, linewidth=0.6)
    # extend x-range so negative-bar annotations never crowd the category axis
    xmin = min(vals.min(), 0) - 18
    xmax = max(vals.max(), 0) + 14
    ax.set_xlim(xmin, xmax)
    for b, v, n_points, d_raw in zip(bars, vals, s["pi_n"].fillna(0), s["d_pct_yr"]):
        if pd.isna(d_raw):
            label = f"n/a  (n={int(n_points)})"
            ax.text(0 + 1, b.get_y() + b.get_height() / 2, label,
                    va="center", ha="left", fontsize=9, color=MUTED, style="italic")
        else:
            label = f"{v:+.1f} %/yr (n={int(n_points)})"
            # always annotate to the RIGHT of the bar tip (for negative bars that's inside the negative span)
            ax.text(v + 1, b.get_y() + b.get_height() / 2, label,
                    va="center", ha="left", fontsize=9, color=INK)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlabel("D (%/yr) — positive = PI declining", color=INK, fontsize=10)
    ax.set_title("Candidate ranking by PI decline rate",
                 color=NAVY, fontsize=13, loc="left", fontfamily="serif",
                 fontweight="bold")
    _style_axes(ax)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:+.0f}"))
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=PAPER)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Slide helpers
# ---------------------------------------------------------------------------
SLIDE_W = Inches(13.333); SLIDE_H = Inches(7.5)
TITLE_SIZE = Pt(30); BODY_SIZE = Pt(16); BULLET_SIZE = Pt(14); SUB_SIZE = Pt(11)
FOOTER = "PC26 · Obj 1.1C · Shah Field · TotalEnergies ALSG × ADNOC Onshore · 2026-04-23"


def _blank(prs) -> object:
    return prs.slides.add_slide(prs.slide_layouts[6])  # blank


def _rect(slide, x, y, w, h, fill_rgb, line_rgb=None) -> object:
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill_rgb)
    if line_rgb is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line_rgb); shp.line.width = Pt(0.75)
    shp.shadow.inherit = False
    return shp


def _text(slide, x, y, w, h, text, *, size=BODY_SIZE, bold=False, color=INK,
          font="Calibri", align=PP_ALIGN.LEFT, v_anchor=MSO_ANCHOR.TOP) -> object:
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = v_anchor
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run(); r.text = text
    r.font.name = font; r.font.size = size; r.font.bold = bold
    r.font.color.rgb = rgb(color)
    return tb


def _bullets(slide, x, y, w, h, items, *, size=BULLET_SIZE, color=INK,
             font="Calibri", bullet_color=OIL) -> object:
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(4)
        r0 = p.add_run(); r0.text = "▸ "
        r0.font.name = font; r0.font.size = size; r0.font.bold = True
        r0.font.color.rgb = rgb(bullet_color)
        r = p.add_run(); r.text = item
        r.font.name = font; r.font.size = size; r.font.color.rgb = rgb(color)
    return tb


def _footer(slide) -> None:
    _text(slide, Inches(0.3), Inches(7.1), Inches(12.7), Inches(0.3),
          FOOTER, size=Pt(9), color=MUTED, font="Calibri",
          align=PP_ALIGN.LEFT)


def _title_bar(slide, title: str, subtitle: str = "") -> None:
    _rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.6), NAVY)
    _rect(slide, Inches(0), Inches(0.6), SLIDE_W, Inches(0.05), OIL)
    _text(slide, Inches(0.4), Inches(0.05), Inches(12.5), Inches(0.5),
          title, size=Pt(22), bold=True, color=PAPER, font="Georgia",
          align=PP_ALIGN.LEFT, v_anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        _text(slide, Inches(0.4), Inches(0.75), Inches(12.5), Inches(0.3),
              subtitle, size=Pt(11), color=MUTED, font="Calibri",
              align=PP_ALIGN.LEFT)


# ---------------------------------------------------------------------------
# Individual slide builders
# ---------------------------------------------------------------------------
def slide_title(prs):
    s = _blank(prs)
    # background
    _rect(s, Inches(0), Inches(0), SLIDE_W, SLIDE_H, NAVY)
    # accent bar
    _rect(s, Inches(0), Inches(6.0), SLIDE_W, Inches(0.08), OIL)
    _text(s, Inches(0.7), Inches(2.1), Inches(11.9), Inches(1.2),
          "PC26 — Objective 1.1C",
          size=Pt(44), bold=True, color=PAPER, font="Georgia")
    _text(s, Inches(0.7), Inches(3.3), Inches(11.9), Inches(0.9),
          "Shah SIMSIMA R1 — Stimulation Candidates Roadmap",
          size=Pt(26), color="#FDE68A", font="Georgia")
    _text(s, Inches(0.7), Inches(4.5), Inches(11.9), Inches(0.6),
          "PI decline ranking · 5 candidates · final-5 defers SY-131, SY-133 backup",
          size=Pt(14), color="#E5E7EB", font="Calibri")
    _text(s, Inches(0.7), Inches(6.3), Inches(11.9), Inches(0.5),
          "TotalEnergies ALSG  ×  ADNOC Onshore    ·    Issued 23-Apr-2026",
          size=Pt(13), color=PAPER, font="Calibri")
    _text(s, Inches(0.7), Inches(6.8), Inches(11.9), Inches(0.4),
          "Confidential — internal decision support only",
          size=Pt(10), color="#94A3B8", font="Calibri")


def slide_exec(prs):
    s = _blank(prs)
    _title_bar(s, "Executive summary", "Five stimulation candidates selected from seven-well screen")
    _bullets(s, Inches(0.6), Inches(1.2), Inches(12.2), Inches(5.8),
             EXEC_SUMMARY_BULLETS, size=Pt(16))
    _footer(s)


def slide_context(prs):
    s = _blank(prs)
    _title_bar(s, "Reservoir context — Shah SIMSIMA R1",
               "Dual-media fractured carbonate; only one in ADNOC Onshore")
    # two-column KV
    items = list(RESERVOIR_CONTEXT.items())
    left = items[:len(items)//2]; right = items[len(items)//2:]
    def kv(col_x, col_items):
        y = Inches(1.3)
        for k, v in col_items:
            _text(s, col_x, y, Inches(2.6), Inches(0.35), k, size=Pt(12),
                  bold=True, color=MUTED)
            _text(s, col_x + Inches(2.6), y, Inches(3.4), Inches(0.35), v,
                  size=Pt(12), color=INK)
            y += Inches(0.45)
    kv(Inches(0.6), left)
    kv(Inches(6.9), right)
    _rect(s, Inches(6.5), Inches(1.25), Inches(0.02), Inches(5.3), MUTED)
    _footer(s)


def slide_overview_table(prs, summary: pd.DataFrame):
    s = _blank(prs)
    _title_bar(s, "Candidate overview",
               "All seven wells · D %/yr is log-linear fit of valid PI points")

    cols = ["Well", "Category", "Status", "Tests", "PI pts",
            "PI first → last", "PI Δ %", "D %/yr", "R²", "Qo last"]
    widths = [0.85, 3.6, 0.9, 0.7, 0.7, 1.7, 0.9, 0.85, 0.7, 0.9]  # inches
    row_h = 0.45
    x0 = Inches(0.5); y0 = Inches(1.3)

    # header
    x = x0
    for c, (h, w) in enumerate(zip(cols, widths)):
        cell = _rect(s, x, y0, Inches(w), Inches(row_h), NAVY)
        _text(s, x, y0, Inches(w), Inches(row_h), h,
              size=Pt(11), bold=True, color=PAPER, font="Calibri",
              align=PP_ALIGN.CENTER, v_anchor=MSO_ANCHOR.MIDDLE)
        x += Inches(w)

    statcol = {"Final": FINAL_FILL, "Backup": BACKUP_FILL, "Defer": DEFER_FILL, "—": PAPER}
    # sort: Final first, then Backup, Defer; within each group by D desc
    order = (["Final"] * 1 + ["Backup"] * 1 + ["Defer"] * 1)
    def key(r):
        return (["Final", "Backup", "Defer", "—"].index(r["status"]),
                -(r["d_pct_yr"] if pd.notna(r["d_pct_yr"]) else -9999))
    rows = sorted(summary.to_dict("records"), key=key)
    y = y0 + Inches(row_h)
    for r in rows:
        x = x0
        pi_first = f"{r['pi_first']:.2f}" if pd.notna(r.get("pi_first")) else "—"
        pi_last = f"{r['pi_last']:.2f}" if pd.notna(r.get("pi_last")) else "—"
        pi_fl = f"{pi_first} → {pi_last}"
        pi_chg = f"{r['pi_change_pct']:+.0f}%" if pd.notna(r.get("pi_change_pct")) else "—"
        d_val = f"{r['d_pct_yr']:+.1f}" if pd.notna(r.get("d_pct_yr")) else "—"
        r2 = f"{r['r2']:.2f}" if pd.notna(r.get("r2")) else "—"
        qo_last = f"{r['qo_last']:.0f}" if pd.notna(r.get("qo_last")) else "—"
        vals = [r["well"], WELL_META.get(r["well"], {}).get("category", ""),
                r["status"], str(int(r["tests_n"] or 0)),
                (str(int(r["pi_n"])) if pd.notna(r.get("pi_n")) else "—"),
                pi_fl, pi_chg, d_val, r2, qo_last]
        fill = statcol.get(r["status"], PAPER)
        for c, (v, w) in enumerate(zip(vals, widths)):
            _rect(s, x, y, Inches(w), Inches(row_h), fill, line_rgb=LINE_COLOR)
            bold = (c == 0) or (c == 2)
            _text(s, x + Emu(20000), y, Inches(w) - Emu(40000), Inches(row_h), v,
                  size=Pt(10), bold=bold, color=INK, font="Calibri",
                  align=PP_ALIGN.CENTER if c != 1 else PP_ALIGN.LEFT,
                  v_anchor=MSO_ANCHOR.MIDDLE)
            x += Inches(w)
        y += Inches(row_h)
    _footer(s)


def slide_pi_ranking(prs, summary: pd.DataFrame):
    s = _blank(prs)
    _title_bar(s, "PI decline ranking",
               "Log-linear fit of valid PI points (BHFP = PIP + Δ per well)")
    png = CHARTS / "pi_ranking.png"
    chart_pi_ranking(summary, png)
    s.shapes.add_picture(str(png), Inches(0.6), Inches(1.3),
                          width=Inches(8.8), height=Inches(4.8))
    # legend / interpretation box
    _rect(s, Inches(9.7), Inches(1.3), Inches(3.3), Inches(4.8), FINAL_FILL,
          line_rgb=LINE_COLOR)
    _text(s, Inches(9.9), Inches(1.4), Inches(3.0), Inches(0.35),
          "Interpretation",
          size=Pt(12), bold=True, color=NAVY, font="Georgia")
    _bullets(s, Inches(9.9), Inches(1.8), Inches(3.2), Inches(4.2), [
        "Green bars: D ≥ 15 %/yr — active PI degradation",
        "Amber bars: 0-15 %/yr — mild decline",
        "Blue bars: D < 0 — PI actually increased (not a stim case)",
        "SY-074 not rendered — insufficient PI points",
        "SY-146 not rendered — water-injector, no oil PI",
    ], size=Pt(11))
    _footer(s)


def slide_well_story(prs, well: str, tests, decline, events):
    s = _blank(prs)
    meta = WELL_META.get(well, {})
    _title_bar(s, f"{well} — {meta.get('category','')}",
               f"{meta.get('reservoir','')} · {meta.get('type','')} · completion {meta.get('completion','')}")
    # left: chart
    png = CHARTS / f"well_{well}.png"
    chart_production_pi(well, tests, decline, events, png)
    s.shapes.add_picture(str(png), Inches(0.4), Inches(1.2),
                          width=Inches(7.3), height=Inches(5.5))

    # right: narrative box + "why now"
    _rect(s, Inches(8.0), Inches(1.2), Inches(4.9), Inches(3.6), FINAL_FILL,
          line_rgb=LINE_COLOR)
    _text(s, Inches(8.2), Inches(1.3), Inches(4.6), Inches(0.4),
          "Key finding", size=Pt(13), bold=True, color=NAVY, font="Georgia")
    _text(s, Inches(8.2), Inches(1.75), Inches(4.6), Inches(2.9),
          KEY_FINDINGS.get(well, "—"), size=Pt(12), color=INK, font="Calibri")

    _rect(s, Inches(8.0), Inches(5.0), Inches(4.9), Inches(1.7), NAVY,
          line_rgb=NAVY)
    _text(s, Inches(8.2), Inches(5.1), Inches(4.6), Inches(0.4),
          "Why now", size=Pt(13), bold=True, color=OIL, font="Georgia")
    why_now = {
        "SY-110": "Longest, most severe decline; stable Pres — skin-driven; scale-dissolver pre-flush + HCl.",
        "SY-069": "135-test history ideal for bench-marking; decline accelerating; HCl + naphtha 2-stage baseline.",
        "SY-074": "New ST2 lateral (Aug-2024) never stimulated; mud-cake damage likely; PBU + PLT pre-job mandatory.",
        "SY-120": "Sustain-play — avoid over-drawdown (Pb=392); dolomite-tailored acid; Y-tool allows CT-conveyed treatment.",
        "SY-146": "Injectivity stim — naphtha pre-flush + HCl main; Hall-plot analysis pre/post; recent completion requires baseline.",
    }.get(well, "—")
    _text(s, Inches(8.2), Inches(5.55), Inches(4.6), Inches(1.3),
          why_now, size=Pt(11), color=PAPER, font="Calibri")
    _footer(s)


def slide_data_gaps(prs):
    s = _blank(prs)
    _title_bar(s, "Data gaps & caveats",
               "Interpretation risks the rig schedule must acknowledge")
    _bullets(s, Inches(0.6), Inches(1.3), Inches(12.2), Inches(5.8),
             DATA_GAPS, size=Pt(14))
    _footer(s)


def slide_conclusions(prs):
    s = _blank(prs)
    _title_bar(s, "Conclusions & next steps",
               "Stimulation sequence, pre-job acquisition, and gating checklist")
    _bullets(s, Inches(0.6), Inches(1.3), Inches(12.2), Inches(5.8),
             CONCLUSIONS, size=Pt(14))
    _footer(s)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def build_pptx() -> None:
    res = pipeline.run()
    tests = res["tests"]; decline = res["decline"]
    events = res["events"]; summary = res["summary"]

    prs = Presentation()
    prs.slide_width = SLIDE_W; prs.slide_height = SLIDE_H

    slide_title(prs)
    slide_exec(prs)
    slide_context(prs)
    slide_overview_table(prs, summary)
    slide_pi_ranking(prs, summary)
    for w in FINAL_FIVE:       # 5 story slides
        slide_well_story(prs, w, tests, decline, events)
    slide_data_gaps(prs)
    slide_conclusions(prs)

    path = OUT / "PC26_1.1C_Stimulation_Candidates.pptx"
    prs.save(path)
    print(f"Wrote {path} ({path.stat().st_size/1024:.0f} KB, {len(prs.slides)} slides)")


if __name__ == "__main__":
    build_pptx()
