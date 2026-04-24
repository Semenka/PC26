"""
PC26 Obj 1.1C — dark-themed HTML dashboard v2.

Reads intermediates from analysis/out and renders a self-contained HTML file
with three charts per well (production, PI + linear-decline fit, pressure/ESP),
an overview tab with sortable candidate table and PI ranking card, and a data
gaps tab. Uses Plotly (CDN).
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.constants import (
    ALL_WELLS, FINAL_FIVE, BACKUP, DEFERRED, PALETTE, WELL_META,
    KEY_FINDINGS, DATA_GAPS, CONFIRMED_EVENTS, PRES_SURVEYS,
)
from analysis import pipeline

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables"
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Plotly trace / layout helpers
# ---------------------------------------------------------------------------
BG = PALETTE["bg"]; PANEL = PALETTE["panel"]; TEXT = PALETTE["text"]
SUB = PALETTE["subtle"]; GRID = PALETTE["grid"]
OIL = PALETTE["oil"]; NAVY = PALETTE["navy"]
CONF = PALETTE["confirmed"]; INFER = PALETTE["inferred"]


def _layout(title: str, yaxis: str, yaxis2: str | None = None, height: int = 360) -> dict:
    L = dict(
        title=dict(text=title, font=dict(color=TEXT, size=16, family="Calibri,sans-serif")),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Calibri,sans-serif"),
        margin=dict(l=60, r=50, t=50, b=50), height=height,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=SUB), title="Date"),
        yaxis=dict(title=yaxis, gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=SUB)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT), orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    if yaxis2 is not None:
        L["yaxis2"] = dict(title=yaxis2, overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)", tickfont=dict(color=SUB))
    return L


def _event_shapes(well: str, events: pd.DataFrame, ymin=0, ymax=1) -> list[dict]:
    shapes = []
    for _, e in events[events["well"] == well].iterrows():
        is_conf = e["confidence"] == "confirmed"
        shapes.append(dict(
            type="line", xref="x", yref="paper",
            x0=e["date"].isoformat(), x1=e["date"].isoformat(), y0=0, y1=1,
            line=dict(color=CONF if is_conf else INFER,
                      width=2, dash="solid" if is_conf else "dash"),
            layer="below",
        ))
    return shapes


def _event_markers(well: str, events: pd.DataFrame, yval: float) -> dict:
    sub = events[events["well"] == well]
    if sub.empty:
        return None
    return dict(
        x=sub["date"].dt.strftime("%Y-%m-%d").tolist(),
        y=[yval] * len(sub),
        mode="markers+text",
        marker=dict(
            size=10,
            color=[CONF if c == "confirmed" else INFER for c in sub["confidence"]],
            symbol=["circle" if c == "confirmed" else "triangle-up-open" for c in sub["confidence"]],
            line=dict(color=TEXT, width=1),
        ),
        text=sub["label"].tolist(),
        hovertext=sub["label"].tolist(),
        hoverinfo="x+text",
        textposition="top center",
        textfont=dict(size=9, color=SUB),
        name="Events",
        type="scatter",
        showlegend=True,
    )


def _production_chart(well: str, tests: pd.DataFrame, events: pd.DataFrame) -> dict:
    g = tests[tests["well"] == well].sort_values("date")
    qo = dict(
        x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
        y=g["qo_bopd"].round(1).tolist(),
        mode="lines+markers", name="Qo (BOPD)",
        line=dict(color=OIL, width=2), marker=dict(size=5),
        hovertemplate="%{x}<br>Qo=%{y:.0f} BOPD<extra></extra>",
    )
    wc = dict(
        x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
        y=g["wc_pct"].round(1).tolist(),
        mode="lines+markers", name="WC (%)", yaxis="y2",
        line=dict(color="#60A5FA", width=1.5, dash="dot"), marker=dict(size=4),
        hovertemplate="%{x}<br>WC=%{y:.1f}%<extra></extra>",
    )
    traces = [qo, wc]
    em = _event_markers(well, events, yval=(g["qo_bopd"].max() or 1) * 0.95)
    if em: traces.append(em)
    layout = _layout(f"Production — {well}", "Qo (BOPD)", "Water-cut (%)")
    layout["shapes"] = _event_shapes(well, events)
    layout["yaxis2"]["range"] = [0, 100]
    return dict(data=traces, layout=layout)


def _pi_chart(well: str, tests: pd.DataFrame, decline: pd.DataFrame,
              events: pd.DataFrame) -> dict:
    g = tests[(tests["well"] == well) & tests["pi_valid"]].sort_values("date")
    d = decline[decline["well"] == well]
    traces = []
    if g.empty:
        layout = _layout(f"PI vs time — {well}", "PI (BOPD/psi)")
        layout["annotations"] = [dict(
            x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
            text="PI NOT COMPUTABLE<br>(insufficient formal pressure surveys)",
            font=dict(color=OIL, size=16))]
        return dict(data=[], layout=layout)

    traces.append(dict(
        x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
        y=g["pi_bopd_psi"].round(3).tolist(),
        mode="markers", name="PI points",
        marker=dict(color=OIL, size=7, line=dict(color=TEXT, width=0.5)),
        hovertemplate="%{x}<br>PI=%{y:.3f} BOPD/psi<extra></extra>",
    ))
    # log-linear fit overlay
    if len(d) and d.iloc[0]["valid"]:
        dd = d.iloc[0]
        t0 = g["date"].min()
        xs = g["date"]
        t_yr = (xs - t0).dt.total_seconds() / (365.25 * 86400)
        ys = np.exp(dd["intercept"] + dd["slope"] * t_yr)
        traces.append(dict(
            x=xs.dt.strftime("%Y-%m-%d").tolist(),
            y=ys.round(3).tolist(),
            mode="lines", name=f"Fit: D={dd['d_pct_yr']:.0f} %/yr (R²={dd['r2']:.2f})",
            line=dict(color=CONF if dd["d_pct_yr"] > 0 else "#818CF8",
                      width=2.5, dash="solid"),
            hoverinfo="skip",
        ))
    em = _event_markers(well, events, yval=(g["pi_bopd_psi"].max() or 1) * 0.9)
    if em: traces.append(em)
    layout = _layout(f"Productivity Index — {well}", "PI (BOPD / psi)")
    layout["shapes"] = _event_shapes(well, events)
    layout["yaxis"]["type"] = "log"
    return dict(data=traces, layout=layout)


def _pressure_chart(well: str, tests: pd.DataFrame, events: pd.DataFrame) -> dict:
    g = tests[tests["well"] == well].sort_values("date")
    traces = []
    if g["pip_psig"].notna().any():
        traces.append(dict(
            x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
            y=g["pip_psig"].tolist(), mode="lines+markers", name="PIP (psig)",
            line=dict(color="#60A5FA", width=1.5), marker=dict(size=4),
            hovertemplate="%{x}<br>PIP=%{y:.0f} psig<extra></extra>",
        ))
    if g["bhfp_psi"].notna().any():
        traces.append(dict(
            x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
            y=g["bhfp_psi"].round(0).tolist(), mode="lines", name="BHFP = PIP+Δ",
            line=dict(color=OIL, width=1.8, dash="dot"),
            hovertemplate="%{x}<br>BHFP=%{y:.0f} psi<extra></extra>",
        ))
    if g["pres_psi"].notna().any():
        traces.append(dict(
            x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
            y=g["pres_psi"].round(0).tolist(), mode="lines",
            name="Pres (interp)",
            line=dict(color=CONF, width=2),
            hovertemplate="%{x}<br>Pres=%{y:.0f} psi<extra></extra>",
        ))
    # anchors
    anchors = PRES_SURVEYS.get(well, [])
    if anchors:
        traces.append(dict(
            x=[a[0].isoformat() for a in anchors],
            y=[a[1] for a in anchors],
            mode="markers", name="Pres survey",
            marker=dict(color=CONF, size=12, symbol="diamond",
                        line=dict(color=TEXT, width=1)),
            hovertext=[f"{a[2]}: {a[1]:.0f} psi" for a in anchors],
            hoverinfo="x+text",
        ))
    # secondary axis: ESP Freq
    if g["freq_hz"].notna().any():
        traces.append(dict(
            x=g["date"].dt.strftime("%Y-%m-%d").tolist(),
            y=g["freq_hz"].tolist(), mode="lines+markers", name="ESP Freq (Hz)",
            yaxis="y2", line=dict(color=PALETTE["bad"], width=1, dash="dash"),
            marker=dict(size=3),
            hovertemplate="%{x}<br>Freq=%{y:.0f} Hz<extra></extra>",
        ))
    layout = _layout(f"Pressure & ESP — {well}", "Pressure (psi / psig)",
                     "ESP Freq (Hz)")
    layout["shapes"] = _event_shapes(well, events)
    if "yaxis2" in layout: layout["yaxis2"]["range"] = [30, 60]
    return dict(data=traces, layout=layout)


# ---------------------------------------------------------------------------
# Overview tab
# ---------------------------------------------------------------------------
def _overview_table(summary: pd.DataFrame) -> str:
    rows = []
    colour = {"Final": CONF, "Backup": OIL, "Defer": PALETTE["bad"], "—": SUB}
    for _, r in summary.iterrows():
        w = r["well"]
        meta = WELL_META.get(w, {})
        status = r["status"]
        pi_first = f"{r['pi_first']:.2f}" if pd.notna(r["pi_first"]) else "—"
        pi_last  = f"{r['pi_last']:.2f}"  if pd.notna(r["pi_last"])  else "—"
        pi_chg   = f"{r['pi_change_pct']:+.1f}%" if pd.notna(r["pi_change_pct"]) else "—"
        d_pct    = f"{r['d_pct_yr']:+.1f}" if pd.notna(r["d_pct_yr"]) else "—"
        r2       = f"{r['r2']:.2f}" if pd.notna(r["r2"]) else "—"
        qo_last  = f"{r['qo_last']:.0f}" if pd.notna(r["qo_last"]) else "—"
        wc_last  = f"{r['wc_last']:.1f}" if pd.notna(r["wc_last"]) else "—"
        rows.append(
            f"<tr data-status='{status}'>"
            f"<td><b>{w}</b></td>"
            f"<td>{meta.get('category','—')}</td>"
            f"<td><span class='pill' style='background:{colour[status]}'>{status}</span></td>"
            f"<td class='num'>{r['tests_n']}</td>"
            f"<td class='num'>{r['pi_n'] or '—'}</td>"
            f"<td class='num'>{pi_first}</td>"
            f"<td class='num'>{pi_last}</td>"
            f"<td class='num'>{pi_chg}</td>"
            f"<td class='num'>{d_pct}</td>"
            f"<td class='num'>{r2}</td>"
            f"<td class='num'>{qo_last}</td>"
            f"<td class='num'>{wc_last}</td>"
            f"</tr>"
        )
    header = (
        "<tr>"
        "<th data-sort='s'>Well</th>"
        "<th data-sort='s'>Category</th>"
        "<th data-sort='s'>Status</th>"
        "<th data-sort='n'>Tests</th>"
        "<th data-sort='n'>PI pts</th>"
        "<th data-sort='n'>PI first</th>"
        "<th data-sort='n'>PI last</th>"
        "<th data-sort='n'>PI Δ %</th>"
        "<th data-sort='n'>D %/yr</th>"
        "<th data-sort='n'>R²</th>"
        "<th data-sort='n'>Qo last</th>"
        "<th data-sort='n'>WC last</th>"
        "</tr>"
    )
    return f"<table id='overview'><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def _pi_ranking_card(summary: pd.DataFrame) -> str:
    s = summary.copy()
    s["rank_key"] = s["d_pct_yr"].fillna(-999)
    s = s.sort_values("rank_key", ascending=False)
    items = []
    for _, r in s.iterrows():
        if pd.isna(r["d_pct_yr"]):
            badge = "—"
        else:
            badge = f"{r['d_pct_yr']:+.0f} %/yr"
        pi_chg = f"{r['pi_change_pct']:+.0f}%" if pd.notna(r["pi_change_pct"]) else "—"
        items.append(
            f"<li><span class='rank-name'>{r['well']}</span>"
            f"<span class='rank-badge'>{badge}</span>"
            f"<span class='rank-sub'>PI change {pi_chg} · {WELL_META.get(r['well'],{}).get('category','')}</span></li>"
        )
    return "<ul class='ranking'>" + "".join(items) + "</ul>"


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------
_HTML_SHELL = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>PC26 1.1C · Well Performance Dashboard v2</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
:root {{
  --bg: {bg}; --panel: {panel}; --text: {text}; --sub: {sub};
  --oil: {oil}; --navy: {navy}; --ok: {ok}; --warn: {warn}; --bad: {bad};
}}
* {{ box-sizing: border-box; }}
html,body {{ background: var(--bg); color: var(--text); margin:0; padding:0;
  font-family: Calibri, "Segoe UI", sans-serif; }}
header {{ padding: 20px 28px; background: var(--navy); border-bottom: 2px solid var(--oil); }}
header h1 {{ margin: 0; font-family: Georgia, serif; font-size: 22px; }}
header .meta {{ color: var(--sub); font-size: 12px; margin-top: 4px; }}
nav {{ display: flex; gap: 4px; padding: 0 16px; background: var(--panel);
  overflow-x: auto; border-bottom: 1px solid #202733; }}
nav button {{ background: transparent; color: var(--sub); border: none;
  padding: 12px 18px; font-size: 14px; cursor: pointer; border-bottom: 3px solid transparent;
  font-family: inherit; }}
nav button.active {{ color: var(--oil); border-bottom-color: var(--oil); font-weight: 600; }}
nav button:hover {{ color: var(--text); }}
main {{ padding: 20px 28px; }}
.tab {{ display: none; }}
.tab.active {{ display: block; }}
.grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; }}
@media (min-width: 1100px) {{ .grid.two {{ grid-template-columns: 1fr 1fr; }} }}
.card {{ background: var(--panel); border-radius: 8px; padding: 16px;
  border: 1px solid #1c2430; }}
.card h3 {{ margin: 0 0 8px 0; color: var(--oil); font-family: Georgia, serif; font-size: 16px; }}
.finding {{ color: var(--sub); font-size: 13px; line-height: 1.5; margin: 0; }}
.finding b {{ color: var(--text); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 6px; }}
th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #1f2937; }}
th {{ color: var(--sub); font-weight: 600; cursor: pointer; user-select: none; }}
th:hover {{ color: var(--oil); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.pill {{ display: inline-block; padding: 2px 10px; border-radius: 12px;
  color: #0A0F1A; font-weight: 600; font-size: 11px; letter-spacing: 0.3px; }}
ul.ranking {{ list-style: none; padding: 0; margin: 0; }}
ul.ranking li {{ padding: 10px 12px; margin-bottom: 6px; background: #10151E;
  border-left: 3px solid var(--oil); border-radius: 4px;
  display: grid; grid-template-columns: auto auto 1fr; gap: 10px; align-items: baseline; }}
.rank-name {{ font-weight: 700; color: var(--text); }}
.rank-badge {{ color: var(--oil); font-family: monospace; font-size: 13px;
  padding: 2px 8px; background: rgba(245,158,11,0.1); border-radius: 4px; }}
.rank-sub {{ color: var(--sub); font-size: 12px; }}
.legend {{ font-size: 11px; color: var(--sub); margin-top: 8px; }}
.legend span {{ margin-right: 18px; }}
.legend .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  margin-right: 4px; vertical-align: middle; }}
.legend .conf {{ background: {confirmed}; }}
.legend .infer {{ background: {inferred}; border: 1px dashed {inferred}; }}
.kv {{ display: grid; grid-template-columns: auto 1fr; gap: 6px 16px; font-size: 13px; }}
.kv dt {{ color: var(--sub); margin:0; }}
.kv dd {{ margin:0; color: var(--text); }}
.gaps li {{ margin-bottom: 10px; color: var(--sub); line-height: 1.6; }}
.gaps li::marker {{ color: var(--oil); }}
footer {{ padding: 14px 28px; border-top: 1px solid #202733; color: var(--sub); font-size: 11px; }}
</style></head>
<body>
<header>
  <h1>PC26 · Obj 1.1C — Well Performance Dashboard v2</h1>
  <div class="meta">Shah SIMSIMA R1 · Stimulation Roadmap · TotalEnergies ALSG × ADNOC Onshore · Issued 23-Apr-2026</div>
</header>
<nav id="nav">{nav_buttons}</nav>
<main>{tabs}</main>
<footer>PC26 · Obj 1.1C · Confidential — internal decision support only.</footer>
<script>
const FIG = {figjson};
function initTabs() {{
  const btns = document.querySelectorAll('nav button');
  btns.forEach(b => b.addEventListener('click', () => {{
    btns.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + b.dataset.target).classList.add('active');
    renderFor(b.dataset.target);
  }}));
  btns[0].click();
}}
const rendered = new Set();
function renderFor(key) {{
  Object.keys(FIG).forEach(id => {{
    if (id.startsWith('chart-' + key + '-') && !rendered.has(id)) {{
      const spec = FIG[id];
      Plotly.newPlot(id, spec.data, spec.layout,
        {{displaylogo:false, responsive:true, modeBarButtonsToRemove:['lasso2d','select2d']}});
      rendered.add(id);
    }}
  }});
}}
function sortTable(table, col, kind) {{
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const asc = table.dataset.sortCol === String(col) && table.dataset.sortDir !== 'asc' ? 'asc' : 'asc';
  const dir = (table.dataset.sortCol === String(col) && table.dataset.sortDir === 'asc') ? 'desc' : 'asc';
  rows.sort((a,b) => {{
    let va = a.cells[col].innerText.trim();
    let vb = b.cells[col].innerText.trim();
    if (kind === 'n') {{
      const pa = parseFloat(va.replace(/[^0-9.\\-]/g,'')); const pb = parseFloat(vb.replace(/[^0-9.\\-]/g,''));
      return (isNaN(pa)?-Infinity:pa) - (isNaN(pb)?-Infinity:pb);
    }}
    return va.localeCompare(vb);
  }});
  if (dir === 'desc') rows.reverse();
  table.dataset.sortCol = col; table.dataset.sortDir = dir;
  rows.forEach(r => tbody.appendChild(r));
}}
document.addEventListener('DOMContentLoaded', () => {{
  initTabs();
  const tbl = document.getElementById('overview');
  if (tbl) {{
    tbl.querySelectorAll('th').forEach((th, i) => {{
      th.addEventListener('click', () => sortTable(tbl, i, th.dataset.sort));
    }});
  }}
}});
</script>
</body></html>
"""


def _nav_and_tabs(tabs: list[tuple[str, str, str]]) -> tuple[str, str]:
    btns = "".join(
        f'<button data-target="{key}">{label}</button>'
        for key, label, _ in tabs
    )
    panels = "".join(
        f'<section id="tab-{key}" class="tab">{body}</section>'
        for key, _, body in tabs
    )
    return btns, panels


def _well_tab(well: str, summary: pd.DataFrame) -> str:
    meta = WELL_META.get(well, {})
    s = summary[summary["well"] == well].iloc[0] if (summary["well"] == well).any() else {}
    finding = KEY_FINDINGS.get(well, "—")
    legend = ("<div class='legend'>"
              "<span><span class='dot conf'></span>Confirmed event</span>"
              "<span><span class='dot infer'></span>Inferred event (Qo step-up)</span>"
              "</div>")
    key_stats = "".join([
        f"<dt>Category</dt><dd>{meta.get('category','')}</dd>",
        f"<dt>Status</dt><dd>{meta.get('status','')}</dd>",
        f"<dt>Reservoir / Type</dt><dd>{meta.get('reservoir','')} · {meta.get('type','')}</dd>",
        f"<dt>Completion</dt><dd>{meta.get('completion','')}</dd>",
        f"<dt>Allowable / TR / SH cap</dt><dd>{meta.get('allowable','')} / {meta.get('tr','')} / {meta.get('sh_cap','')} BOPD</dd>",
        f"<dt>Tests</dt><dd>{int(s['tests_n']) if isinstance(s,dict) is False and pd.notna(s.get('tests_n')) else 0}</dd>",
        f"<dt>Valid PI points</dt><dd>{int(s['pi_n']) if pd.notna(s.get('pi_n', np.nan)) else 0}</dd>",
        f"<dt>PI first → last</dt><dd>"
        f"{s['pi_first']:.2f} → {s['pi_last']:.2f} BOPD/psi</dd>"
        if pd.notna(s.get('pi_first', np.nan)) else "<dt>PI</dt><dd>not computable</dd>",
        f"<dt>D (%/yr)</dt><dd>{s['d_pct_yr']:+.1f} %/yr  (R²={s['r2']:.2f})</dd>"
        if pd.notna(s.get('d_pct_yr', np.nan)) else "<dt>D</dt><dd>—</dd>",
    ])
    charts = "".join([
        f"<div class='card'><h3>Production</h3><div id='chart-{well}-prod' style='height:360px'></div>{legend}</div>",
        f"<div class='card'><h3>Productivity Index (log scale) + linear-decline fit</h3>"
        f"<div id='chart-{well}-pi' style='height:360px'></div>{legend}</div>",
        f"<div class='card'><h3>Pressure &amp; ESP</h3><div id='chart-{well}-pres' style='height:360px'></div>{legend}</div>",
    ])
    return (
        f"<div class='grid two'>"
        f"<div class='card'><h3>Key finding</h3><p class='finding'>{finding}</p>"
        f"<dl class='kv' style='margin-top:14px'>{key_stats}</dl></div>"
        f"<div class='card'><h3>Status & events</h3><p class='finding'>"
        f"Confirmed events on record: "
        + ", ".join([f"{d.isoformat()} — {l}" for d, l in CONFIRMED_EVENTS.get(well, [])]) + ".<br>"
        f"Inferred events are machine-detected Qo step-ups (≥ +30 % sustained over 3 tests).</p>"
        f"</div>"
        f"</div>"
        f"<div class='grid'>{charts}</div>"
    )


def build_html():
    res = pipeline.run()
    tests = res["tests"]; decline = res["decline"]
    events = res["events"]; summary = res["summary"]

    fig: dict[str, dict] = {}
    well_tabs = []
    # fixed order: put FINAL_FIVE first, then defer/backup
    ordered = FINAL_FIVE + [w for w in ALL_WELLS if w not in FINAL_FIVE]
    for w in ordered:
        fig[f"chart-{w}-prod"] = _production_chart(w, tests, events)
        fig[f"chart-{w}-pi"]   = _pi_chart(w, tests, decline, events)
        fig[f"chart-{w}-pres"] = _pressure_chart(w, tests, events)
        well_tabs.append((w, w, _well_tab(w, summary)))

    overview_body = (
        "<div class='grid two'>"
        "<div class='card'><h3>Candidate overview</h3>"
        f"{_overview_table(summary)}</div>"
        "<div class='card'><h3>PI decline ranking (D %/yr, highest first)</h3>"
        f"{_pi_ranking_card(summary)}</div>"
        "</div>"
        f"<div class='card'><h3>Field context — Shah SIMSIMA R1</h3><dl class='kv'>"
        + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in {
            "STOOIP":"3,439 MMSTB", "Np (12/2022)":"590 MMBBL",
            "Recovery factor":"17.2%", "Bubble point Pb":"392 psi",
            "Reservoir type":"Dual-media fractured carbonate",
            "SH Max Qo (R1 H)":"2,000 BOPD", "SH Min BHFP":"1,232 psia",
        }.items())
        + "</dl></div>"
    )
    gaps_body = (
        "<div class='card'><h3>Data gaps & caveats</h3>"
        "<ul class='gaps'>" + "".join(f"<li>{g}</li>" for g in DATA_GAPS) + "</ul>"
        "</div>"
    )

    tabs = [("overview", "Overview", overview_body)] + well_tabs + [("gaps", "Data Gaps", gaps_body)]
    btns, panels = _nav_and_tabs(tabs)
    html = _HTML_SHELL.format(
        bg=PALETTE["bg"], panel=PALETTE["panel"], text=PALETTE["text"],
        sub=PALETTE["subtle"], oil=PALETTE["oil"], navy=PALETTE["navy"],
        ok=PALETTE["ok"], warn=PALETTE["warn"], bad=PALETTE["bad"],
        confirmed=PALETTE["confirmed"], inferred=PALETTE["inferred"],
        nav_buttons=btns, tabs=panels,
        figjson=json.dumps(fig, default=str),
    )
    path = OUT / "PC26_1.1C_Well_Performance_Dashboard_v2.html"
    path.write_text(html, encoding="utf-8")
    print(f"Wrote {path} ({path.stat().st_size/1024:.0f} KB, {len(fig)} figures)")


if __name__ == "__main__":
    build_html()
