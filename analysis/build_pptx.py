"""
PC26 Obj 1.1C — Stimulation-Candidates presentation built on the
TotalEnergies / ADNOC "AA - Bleu" template:
  data/raw template => 06102025_HighLevel_AON_Upstream.pptx (committed to repo root)
  master 0 layouts: 3 = cover (Option N°1 Ouverture de chapitre)
                    14 = Title and Content
                    18 = Blank

Theme colours (from template theme XML):
  primary blue  #009CEA  (titles, accents)
  body text     #374649  (dark slate)
  white         #FFFFFF
The TE + ADNOC logos and the bottom footer / page number are inherited
from the master, so the only thing we draw is title text, body content,
and chart images.
"""
from __future__ import annotations
from pathlib import Path
from copy import deepcopy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np
import pandas as pd

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

from analysis.constants import (
    ALL_WELLS, FINAL_FIVE, WELL_META, KEY_FINDINGS, RESERVOIR_CONTEXT,
    EXEC_SUMMARY_BULLETS, DATA_GAPS, CONCLUSIONS, CONFIRMED_EVENTS,
    PRES_SURVEYS, PALETTE,
)
from analysis import pipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables"
CHARTS = ROOT / "qa" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)
TEMPLATE = ROOT / "06102025_HighLevel_AON_Upstream.pptx"

# TotalEnergies-AA-Bleu palette
TE_BLUE      = "#009CEA"
TE_DARK_BLUE = "#0061A2"
INK          = "#374649"
MUTED        = "#7F8C92"
PAPER        = "#FFFFFF"
ACCENT_GREEN = "#40A900"
ACCENT_RED   = "#ED0000"
ACCENT_ORG   = "#F66A00"
LINE_COLOR   = "#D8DEE3"
SOFT_BLUE    = "#E8F4FB"
SOFT_GREY    = "#F5F7F8"

CONF  = PALETTE["confirmed"]
INFER = PALETTE["inferred"]

FOOTER_TEXT = "ADNOC Upstream  -  TotalEnergies  -  2026-04-23"


def rgb(hex_: str) -> RGBColor:
    h = hex_.lstrip("#")
    return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Template housekeeping
# ---------------------------------------------------------------------------
def _strip_slides(prs: Presentation) -> None:
    """Remove every slide that comes with the template."""
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = sldId.get(qn("r:id"))
        prs.part.drop_rel(rId)
        sldIdLst.remove(sldId)


def _layout(prs: Presentation, name: str):
    for lay in prs.slide_masters[0].slide_layouts:
        if lay.name == name:
            return lay
    raise KeyError(f"layout not found: {name}")


def _kill_placeholders(slide, keep_idx: set[int] | None = None) -> None:
    """Remove every placeholder except those whose `idx` is in keep_idx."""
    keep_idx = keep_idx or set()
    drop = []
    for shp in slide.placeholders:
        if shp.placeholder_format.idx not in keep_idx:
            drop.append(shp)
    for shp in drop:
        sp = shp._element
        sp.getparent().remove(sp)


def _set_title(slide, text: str, *, size: int = 26, color: str = TE_BLUE,
               bold: bool = False) -> None:
    if slide.shapes.title is None:
        return
    tf = slide.shapes.title.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = rgb(color)
    r.font.bold = bold
    r.font.name = "Arial"


# ---------------------------------------------------------------------------
# Generic content widgets
# ---------------------------------------------------------------------------
def _rect(slide, x, y, w, h, fill, line=None, *, shape=MSO_SHAPE.RECTANGLE,
          line_w: float = 0.75):
    shp = slide.shapes.add_shape(shape, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp


def _textbox(slide, x, y, w, h, *, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Emu(20000); tf.margin_right = Emu(20000)
    tf.margin_top = Emu(10000);  tf.margin_bottom = Emu(10000)
    return tb


def _run(p, text: str, *, size: int = 12, color: str = INK,
         bold: bool = False, font: str = "Arial"):
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = rgb(color)
    return r


def _bullets(slide, x, y, w, h, items, *, size: int = 14, color: str = INK,
             bullet_color: str = TE_BLUE, leading: float = 1.15):
    """Filled-square bullets — matches the template style."""
    tb = _textbox(slide, x, y, w, h)
    tf = tb.text_frame
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        p.line_spacing = leading
        _run(p, "▪ ", size=size, color=bullet_color, bold=True)
        _run(p, item, size=size, color=color)
    return tb


def _callout_banner(slide, text: str) -> None:
    """Blue rounded-rectangle banner at the bottom — matches template."""
    bar = _rect(slide, Inches(0.6), Inches(6.05), Inches(12.1), Inches(0.6),
                TE_BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = bar.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Emu(80000); tf.margin_right = Emu(80000)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _run(p, text, size=13, color=PAPER, bold=True)


def _force_footer(slide, page_num: int) -> None:
    """Draw the footer text + page number as plain textboxes positioned where
    the template layout shows them. We do this manually because the master's
    FOOTER and SLIDE_NUMBER placeholders aren't instantiated on most slides,
    so simply setting `slide.placeholders` text doesn't reach the renderer.
    The master shows a literal '|' separator between the two slots."""
    # page number (left of the "|")
    pn = _textbox(slide, Inches(0.24), Inches(7.05), Inches(0.5), Inches(0.28),
                  anchor=MSO_ANCHOR.MIDDLE)
    p = pn.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    _run(p, str(page_num), size=9, color=INK)
    # footer text (right of the "|")
    ft = _textbox(slide, Inches(0.94), Inches(7.05), Inches(6.0), Inches(0.28),
                  anchor=MSO_ANCHOR.MIDDLE)
    p = ft.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    _run(p, FOOTER_TEXT, size=9, color=INK)


# ---------------------------------------------------------------------------
# Matplotlib chart renderers (saved as PNGs, embedded via add_picture)
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


def chart_production_pi(well: str, tests: pd.DataFrame, decline: pd.DataFrame,
                        events: pd.DataFrame, path: Path) -> None:
    g = tests[tests["well"] == well].sort_values("date")
    if g.empty:
        chart_injector_pressure(well, events, path); return

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.6, 4.7),
                                   gridspec_kw=dict(height_ratios=[1, 1]),
                                   sharex=True)
    ax.plot(g["date"], g["qo_bopd"], "-o", color=TE_BLUE, lw=1.4, ms=3.5,
            label="Qo (BOPD)")
    ax.set_ylabel("Qo (BOPD)", color=INK, fontsize=10)
    axw = ax.twinx()
    axw.plot(g["date"], g["wc_pct"], ":", color=ACCENT_RED, lw=1, label="WC (%)")
    axw.set_ylabel("WC (%)", color=ACCENT_RED, fontsize=9)
    axw.set_ylim(0, 100); axw.tick_params(colors=ACCENT_RED, labelsize=8)
    _add_events(ax, well, events); _style_axes(ax)
    ax.set_title(f"{well} — production", fontsize=11, color=TE_BLUE,
                 loc="left", fontweight="bold")

    v = g[g["pi_valid"]]
    if not v.empty:
        ax2.semilogy(v["date"], v["pi_bopd_psi"], "o", color=TE_BLUE, ms=4,
                     alpha=0.85, label="PI points")
        dd = decline[decline["well"] == well]
        if len(dd) and dd.iloc[0]["valid"]:
            d = dd.iloc[0]
            t0 = v["date"].min()
            tyr = (v["date"] - t0).dt.total_seconds() / (365.25 * 86400)
            ax2.plot(v["date"], np.exp(d["intercept"] + d["slope"] * tyr),
                     "-",
                     color=ACCENT_GREEN if d["d_pct_yr"] > 0 else TE_DARK_BLUE,
                     lw=2,
                     label=f"Fit: D={d['d_pct_yr']:+.0f} %/yr, R²={d['r2']:.2f}")
        ax2.legend(loc="best", fontsize=8, frameon=False)
    else:
        ax2.text(0.5, 0.5, "PI NOT COMPUTABLE", transform=ax2.transAxes,
                 ha="center", va="center", color=ACCENT_ORG, fontsize=13,
                 fontweight="bold")
    _add_events(ax2, well, events); _style_axes(ax2)
    ax2.set_ylabel("PI (BOPD/psi)")
    ax2.set_title("Productivity Index + fit", fontsize=11, color=TE_BLUE,
                  loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER); plt.close(fig)


def chart_injector_pressure(well: str, events: pd.DataFrame, path: Path) -> None:
    anchors = PRES_SURVEYS.get(well, [])
    fig, ax = plt.subplots(figsize=(6.6, 4.7))
    if anchors:
        xs = [pd.Timestamp(a[0]) for a in anchors]
        ys = [a[1] for a in anchors]; labels = [a[2] for a in anchors]
        ax.plot(xs, ys, "-o", color=TE_BLUE, lw=1.8, ms=10,
                mec=TE_DARK_BLUE, mew=1)
        ymin, ymax = min(ys), max(ys)
        pad = (ymax - ymin) * 0.28 if ymax != ymin else 50
        ax.set_ylim(ymin - pad, ymax + pad * 0.5)
        span = (xs[-1] - xs[0]).days or 30
        ax.set_xlim(xs[0] - pd.Timedelta(days=span * 0.10),
                     xs[-1] + pd.Timedelta(days=span * 0.30))
        for i, (x, y, lab) in enumerate(zip(xs, ys, labels)):
            dy = 20 if i % 2 == 0 else -40
            ax.annotate(f"{lab}\n{y:.0f} psi", xy=(x, y),
                        xytext=(10, dy), textcoords="offset points",
                        fontsize=9, color=INK,
                        bbox=dict(boxstyle="round,pad=0.3", fc=SOFT_BLUE,
                                  ec=LINE_COLOR),
                        arrowprops=dict(arrowstyle="-", color=LINE_COLOR, lw=0.8))
        if len(ys) >= 2:
            delta = ys[-1] - ys[0]
            ax.annotate(f"Δ = {delta:+.0f} psi\nover {(xs[-1]-xs[0]).days} d",
                        xy=(0.97, 0.93), xycoords="axes fraction",
                        ha="right", va="top", fontsize=11, color=TE_DARK_BLUE,
                        fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7",
                                  ec=ACCENT_ORG, lw=1))
    _add_events(ax, well, events); _style_axes(ax)
    ax.set_title(f"{well} — pressure anchors  (no production-test data in R1)",
                 fontsize=11, color=TE_BLUE, loc="left", fontweight="bold",
                 pad=14)
    ax.set_ylabel("Pres @ datum 3900 ft (psi)", color=INK, fontsize=10)
    fig.subplots_adjust(top=0.88); fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER); plt.close(fig)


def chart_pi_ranking(summary: pd.DataFrame, path: Path) -> None:
    s = summary.sort_values("d_pct_yr", ascending=True, na_position="first")
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    vals = s["d_pct_yr"].fillna(0).to_numpy()
    colors = [ACCENT_GREEN if v > 15 else ACCENT_ORG if v > 0 else TE_DARK_BLUE
              for v in vals]
    bars = ax.barh(s["well"], vals, color=colors,
                   edgecolor=TE_DARK_BLUE, linewidth=0.6)
    ax.set_xlim(min(vals.min(), 0) - 18, max(vals.max(), 0) + 14)
    for b, v, n, raw in zip(bars, vals, s["pi_n"].fillna(0), s["d_pct_yr"]):
        if pd.isna(raw):
            ax.text(1, b.get_y() + b.get_height() / 2,
                    f"n/a  (n={int(n)})", va="center", ha="left",
                    fontsize=9, color=MUTED, style="italic")
        else:
            ax.text(v + 1, b.get_y() + b.get_height() / 2,
                    f"{v:+.1f} %/yr (n={int(n)})", va="center", ha="left",
                    fontsize=9, color=INK)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlabel("D (%/yr) — positive = PI declining", color=INK, fontsize=10)
    ax.set_title("Candidate ranking by PI decline rate",
                 color=TE_BLUE, fontsize=13, loc="left", fontweight="bold")
    _style_axes(ax)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:+.0f}"))
    fig.tight_layout()
    fig.savefig(path, dpi=170, facecolor=PAPER); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------
def slide_cover(prs):
    """Use the 'Option N°1 Ouverture de chapitre' layout, override the
    title + subtitle placeholders. Logos and footer come from the master."""
    s = prs.slides.add_slide(_layout(prs, "Option N°1 Ouverture de chapitre"))
    title_set = sub_set = False
    for ph in s.placeholders:
        idx = ph.placeholder_format.idx
        if idx == 0 and not title_set:    # title
            tf = ph.text_frame; tf.clear()
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
            _run(p, "PC26 — Objective 1.1C", size=40, color=TE_BLUE, bold=True)
            p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.LEFT
            _run(p2, "Shah SIMSIMA R1 — Stimulation Candidates Roadmap",
                 size=24, color=TE_BLUE)
            title_set = True
        elif idx in (1, 2) and not sub_set:   # subtitle / extra text
            tf = ph.text_frame; tf.clear()
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
            _run(p, "TotalEnergies ALSG  ×  ADNOC Onshore", size=18, color=INK)
            sub_set = True
        elif idx == 15:    # date / extra zone — but we'll overwrite below
            tf = ph.text_frame; tf.clear()
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
            _run(p, "23 April 2026", size=14, color=INK)
    # date textbox (template positions a "ZoneTexte" at y=5.33)
    dt = _textbox(s, Inches(0.54), Inches(5.33), Inches(11.0), Inches(0.4))
    p = dt.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    _run(p, "23 April 2026", size=14, color=INK)
    # strapline
    sb = _textbox(s, Inches(0.54), Inches(6.0), Inches(11.0), Inches(0.4))
    p = sb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    _run(p, "PI decline ranking · 5 stimulation candidates · final-5 defers SY-131, SY-133 backup",
         size=11, color=MUTED)
    # footer applied after deck is fully built (see _stamp_footers)


def _content_slide(prs, title: str, *, subtitle: str | None = None):
    s = prs.slides.add_slide(_layout(prs, "Title and Content"))
    _set_title(s, title, size=24, color=TE_BLUE, bold=True)
    if subtitle is not None:
        sb = _textbox(s, Inches(0.51), Inches(1.05), Inches(12.5), Inches(0.35))
        p = sb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
        _run(p, subtitle, size=12, color=MUTED)
    # remove the body placeholder so we can draw fresh content
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 13:
            ph._element.getparent().remove(ph._element)
    # footer applied after deck is fully built (see _stamp_footers)
    return s


def slide_exec_summary(prs):
    s = _content_slide(
        prs, "Executive summary",
        subtitle="Five stimulation candidates selected from a seven-well screen")
    _bullets(s, Inches(0.6), Inches(1.5), Inches(12.2), Inches(4.4),
             EXEC_SUMMARY_BULLETS, size=15)
    _callout_banner(
        s, "Final-5 (in execution order): SY-110 · SY-069 · SY-074 · SY-120 · SY-146")


def slide_reservoir_context(prs):
    s = _content_slide(prs, "Reservoir context — Shah SIMSIMA R1",
                       subtitle="Dual-media fractured carbonate — only one in ADNOC Onshore")
    items = list(RESERVOIR_CONTEXT.items())
    left = items[: (len(items) + 1) // 2]
    right = items[(len(items) + 1) // 2 :]
    def kv_col(col_x):
        return _textbox(s, col_x, Inches(1.5), Inches(5.6), Inches(4.6))
    for col_items, col_x in [(left, Inches(0.6)), (right, Inches(7.0))]:
        tb = kv_col(col_x); tf = tb.text_frame
        for i, (k, v) in enumerate(col_items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(6); p.line_spacing = 1.15
            _run(p, f"{k}  ", size=13, color=TE_BLUE, bold=True)
            _run(p, str(v), size=13, color=INK)
    # vertical divider
    _rect(s, Inches(6.7), Inches(1.5), Emu(15000), Inches(4.6),
          LINE_COLOR, line=LINE_COLOR)


def slide_overview_table(prs, summary: pd.DataFrame):
    s = _content_slide(prs, "Candidate overview",
                       subtitle="All seven wells · D %/yr is log-linear fit of valid PI points")
    cols = ["Well", "Category", "Status", "Tests", "PI pts",
            "PI first → last", "PI Δ %", "D %/yr", "R²", "Qo last"]
    widths_in = [0.85, 3.55, 0.85, 0.70, 0.70, 1.70, 0.85, 0.85, 0.65, 0.85]
    row_h = 0.42
    x0 = Inches(0.5); y0 = Inches(1.55)
    # header
    x = x0
    for c, (h, w) in enumerate(zip(cols, widths_in)):
        _rect(s, x, y0, Inches(w), Inches(row_h), TE_BLUE)
        tb = _textbox(s, x, y0, Inches(w), Inches(row_h),
                      anchor=MSO_ANCHOR.MIDDLE)
        p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        _run(p, h, size=11, color=PAPER, bold=True)
        x += Inches(w)

    statcol = {"Final": "#E7F8EE", "Backup": "#FFF4D6", "Defer": "#FEE2E2", "—": PAPER}
    def key(r):
        return (["Final", "Backup", "Defer", "—"].index(r["status"]),
                -(r["d_pct_yr"] if pd.notna(r["d_pct_yr"]) else -9999))
    rows = sorted(summary.to_dict("records"), key=key)
    y = y0 + Inches(row_h)
    for r in rows:
        pi_first = f"{r['pi_first']:.2f}" if pd.notna(r.get("pi_first")) else "—"
        pi_last  = f"{r['pi_last']:.2f}"  if pd.notna(r.get("pi_last"))  else "—"
        pi_chg   = f"{r['pi_change_pct']:+.0f}%" if pd.notna(r.get("pi_change_pct")) else "—"
        d_val    = f"{r['d_pct_yr']:+.1f}" if pd.notna(r.get("d_pct_yr")) else "—"
        r2       = f"{r['r2']:.2f}" if pd.notna(r.get("r2")) else "—"
        qo_last  = f"{r['qo_last']:.0f}" if pd.notna(r.get("qo_last")) else "—"
        vals = [r["well"], WELL_META.get(r["well"], {}).get("category", ""),
                r["status"], str(int(r["tests_n"] or 0)),
                (str(int(r["pi_n"])) if pd.notna(r.get("pi_n")) else "—"),
                f"{pi_first} → {pi_last}", pi_chg, d_val, r2, qo_last]
        fill = statcol.get(r["status"], PAPER)
        x = x0
        for c, (v, w) in enumerate(zip(vals, widths_in)):
            _rect(s, x, y, Inches(w), Inches(row_h), fill, line=LINE_COLOR)
            tb = _textbox(s, x, y, Inches(w), Inches(row_h),
                          anchor=MSO_ANCHOR.MIDDLE)
            p = tb.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c != 1 else PP_ALIGN.LEFT
            bold = (c == 0) or (c == 2)
            _run(p, v, size=10, color=INK, bold=bold)
            x += Inches(w)
        y += Inches(row_h)


def slide_pi_ranking(prs, summary: pd.DataFrame):
    s = _content_slide(prs, "PI decline ranking",
                       subtitle="Log-linear fit of valid PI points (BHFP = PIP + Δ per well)")
    png = CHARTS / "pi_ranking_v3.png"
    chart_pi_ranking(summary, png)
    s.shapes.add_picture(str(png), Inches(0.5), Inches(1.5),
                          width=Inches(8.9), height=Inches(4.5))
    # interpretation panel
    _rect(s, Inches(9.7), Inches(1.5), Inches(3.3), Inches(4.5),
          SOFT_BLUE, line=LINE_COLOR)
    tt = _textbox(s, Inches(9.9), Inches(1.6), Inches(3.0), Inches(0.4))
    p = tt.text_frame.paragraphs[0]
    _run(p, "Interpretation", size=13, color=TE_BLUE, bold=True)
    _bullets(s, Inches(9.9), Inches(2.05), Inches(3.0), Inches(3.8), [
        "Green: D ≥ 15 %/yr — active PI degradation",
        "Amber: 0–15 %/yr — mild decline",
        "Blue: D < 0 — PI actually increased",
        "SY-074 not rendered — insufficient PI points",
        "SY-146 not rendered — water-injector, no oil PI",
    ], size=11)
    _callout_banner(
        s, "SY-069 and SY-110 dominate the ranking · SY-131 deferred (PI grew) · SY-120 is the sustain-play case")


def slide_well_story(prs, well: str, tests, decline, events):
    meta = WELL_META.get(well, {})
    s = _content_slide(prs, f"{well} — {meta.get('category', '')}",
                       subtitle=f"{meta.get('reservoir','')} · {meta.get('type','')} · completion {meta.get('completion','')}")
    png = CHARTS / f"well_v3_{well}.png"
    chart_production_pi(well, tests, decline, events, png)
    s.shapes.add_picture(str(png), Inches(0.4), Inches(1.45),
                          width=Inches(7.5), height=Inches(4.7))
    # right column: key finding + why now
    _rect(s, Inches(8.1), Inches(1.45), Inches(5.0), Inches(3.0),
          SOFT_BLUE, line=LINE_COLOR)
    tt = _textbox(s, Inches(8.25), Inches(1.55), Inches(4.7), Inches(0.35))
    p = tt.text_frame.paragraphs[0]
    _run(p, "Key finding", size=13, color=TE_BLUE, bold=True)
    tb = _textbox(s, Inches(8.25), Inches(1.95), Inches(4.7), Inches(2.5))
    p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    _run(p, KEY_FINDINGS.get(well, "—"), size=12, color=INK)

    _rect(s, Inches(8.1), Inches(4.6), Inches(5.0), Inches(1.55),
          TE_BLUE, line=TE_BLUE)
    tt2 = _textbox(s, Inches(8.25), Inches(4.7), Inches(4.7), Inches(0.4))
    p = tt2.text_frame.paragraphs[0]
    _run(p, "Why now", size=13, color=PAPER, bold=True)
    why = {
        "SY-110": "Longest, most severe decline; stable Pres → skin-driven. "
                  "Recipe: scale-dissolver pre-flush + HCl. No Y-tool: budget rig time for ESP pull.",
        "SY-069": "135-test history ideal for bench-marking; decline accelerating. "
                  "Baseline recipe: 15 % HCl + naphtha 2-stage. PIP < pump optimum.",
        "SY-074": "New ST2 lateral (Aug-2024) never stimulated; mud-cake damage likely. "
                  "Formal PBU survey + pre-job PLT mandatory.",
        "SY-120": "Sustain-play — avoid over-drawdown (Pb = 392 psi). "
                  "Dolomite-tailored recipe; Y-tool allows CT-conveyed treatment.",
        "SY-146": "Injectivity stim — naphtha pre-flush + HCl main stage. "
                  "Hall-plot analysis pre/post; baseline needed post-completion.",
    }.get(well, "—")
    tb2 = _textbox(s, Inches(8.25), Inches(5.05), Inches(4.7), Inches(1.1))
    p = tb2.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    _run(p, why, size=11, color=PAPER)


def slide_data_gaps(prs):
    s = _content_slide(prs, "Data gaps & caveats",
                       subtitle="Interpretation risks the rig schedule must acknowledge")
    _bullets(s, Inches(0.6), Inches(1.5), Inches(12.2), Inches(4.4),
             DATA_GAPS, size=14)
    _callout_banner(
        s, "Only 4 confirmed events on record (recompletion / ST2 / startup) — request formal stim-event register")


def slide_conclusions(prs):
    s = _content_slide(prs, "Conclusions & next steps",
                       subtitle="Stimulation sequence, pre-job acquisition, and gating checklist")
    _bullets(s, Inches(0.6), Inches(1.5), Inches(12.2), Inches(4.4),
             CONCLUSIONS, size=13)
    _callout_banner(
        s, "Lead: SY-110 · Queue: SY-069 → SY-074 (post-PBU) → SY-120 → SY-146")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def _stamp_footers(prs: Presentation) -> None:
    for i, s in enumerate(prs.slides, start=1):
        _force_footer(s, i)


def build_pptx() -> None:
    res = pipeline.run()
    tests = res["tests"]; decline = res["decline"]
    events = res["events"]; summary = res["summary"]

    if not TEMPLATE.exists():
        raise FileNotFoundError(f"template missing: {TEMPLATE}")
    prs = Presentation(str(TEMPLATE))
    _strip_slides(prs)

    slide_cover(prs)
    slide_exec_summary(prs)
    slide_reservoir_context(prs)
    slide_overview_table(prs, summary)
    slide_pi_ranking(prs, summary)
    for w in FINAL_FIVE:
        slide_well_story(prs, w, tests, decline, events)
    slide_data_gaps(prs)
    slide_conclusions(prs)

    _stamp_footers(prs)

    path = OUT / "PC26_1.1C_Stimulation_Candidates.pptx"
    prs.save(path)
    print(f"Wrote {path} ({path.stat().st_size/1024:.0f} KB, {len(prs.slides)} slides)")


if __name__ == "__main__":
    build_pptx()
