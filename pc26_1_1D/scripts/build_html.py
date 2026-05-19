"""Build the single-file dark dashboard for PC26 Obj 1.1D.

Reads parsed wells.json + bottleneck_counts.json; emits self-contained HTML
with Chart.js 4.4.0, dark navy theme, oil-amber accents, 5 tabs.
"""
import json
import re
from pathlib import Path

DATA_DIR = Path('/home/user/pc26_1_1D/data')
OUT = Path('/home/user/pc26_1_1D/deliverables/PC26_1.1D_Bottleneck_Dashboard.html')

wells = json.loads((DATA_DIR / 'wells.json').read_text())
counts = json.loads((DATA_DIR / 'bottleneck_counts.json').read_text())

# Category metadata for rendering
CAT_META = {
    'S1': {'label': 'Low PIP / stim candidate', 'group': 'Subsurface', 'bopd_lost': 12000, 'color': '#34D399', 'opp': '§4.1'},
    'S2': {'label': 'High water cut (>60%)',     'group': 'Subsurface', 'bopd_lost': 7000,  'color': '#06B6D4', 'opp': '§4.6 + 1.2A'},
    'S3': {'label': 'Low BHFP / close to Pb',    'group': 'Subsurface', 'bopd_lost': 1800,  'color': '#F59E0B', 'opp': '§4.2'},
    'S4': {'label': 'Inactive — WO backlog',     'group': 'Subsurface', 'bopd_lost': 3920,  'color': '#16A34A', 'opp': '§4.8 + 1.1B'},
    'S5': {'label': 'Reservoir P depletion',     'group': 'Subsurface', 'bopd_lost': 5000,  'color': '#0891B2', 'opp': '§4.5'},
    'C1': {'label': 'Low ΔP choke / VSD req.',   'group': 'Surface/Completion', 'bopd_lost': 6500, 'color': '#F59E0B', 'opp': '§4.3'},
    'C2': {'label': 'ESP at max frequency',      'group': 'Completion', 'bopd_lost': 3500, 'color': '#1E3A5F', 'opp': '§4.4'},
    'C3': {'label': 'Surface back-pressure (proxy)', 'group': 'Surface', 'bopd_lost': None, 'color': '#DC2626', 'opp': '§4.7'},
    'W1': {'label': 'Cluster capacity ceiling 25/26 Mbwpd', 'group': 'Water Injection', 'bopd_lost': None, 'color': '#06B6D4', 'opp': '§4.5 Ph2'},
    'W2': {'label': 'WI integrity (SY-175, SY-180)', 'group': 'Water Injection', 'bopd_lost': None, 'color': '#06B6D4', 'opp': '§4.5 Ph1'},
    'W3': {'label': 'R1↔R2 inter-reservoir loss', 'group': 'Water Injection', 'bopd_lost': None, 'color': '#06B6D4', 'opp': '§4.6 (a)'},
    'W4': {'label': 'High-WC PW load', 'group': 'Water Injection', 'bopd_lost': None, 'color': '#06B6D4', 'opp': '§4.6 (c)'},
}

OPPS = [
    {'id': '4.5', 'title': 'WI capacity uplift (SY-175 + SY-180 + cluster review)',
     'category': 'Subsurface / WI', 'lo': 2500, 'hi': 4000, 'full_lo': 4000, 'full_hi': 5500,
     'conf': 'Med-High', 'capex_lo': 2.0, 'capex_hi': 28.0,
     'mech': "Phase 1: complete WO on SY-175 & SY-180 to recover 16,000 bwpd stranded capacity. "
             "Phase 2 (2027): Cluster #2 capacity uplift study based on Jan-2026 FCT. "
             "Phase 3: new WI well drilling if VRR confirms additional voidage to fill. "
             "Sector pressure recovery lifts Qo across ~30 R1/R2 producers. Saih Rawl analog "
             "(SPE 68222): ~12% oil rate uplift per 30% WI rate increase at mature waterflood stage.",
     'prereq': "Cluster #2 / SY-148 WS FCT (RM-mandated before SY-180 commissioning); G2V2 ML#5 forecast"},
    {'id': '4.7', 'title': 'Surface back-pressure optimization', 'category': 'Surface',
     'lo': 1500, 'hi': 2500, 'full_lo': 2300, 'full_hi': 3300,
     'conf': 'Medium', 'capex_lo': 0.2, 'capex_hi': 8.0,
     'mech': "Phase 1: Station header pressure setpoint review (CDS / RDS-1 / RDS-2). Each 10 psi "
             "separator pressure reduction across 80 R1 producers ≈ +800 BOPD. "
             "Phase 2: Selective flowline looping on 2-3 worst segments (>200 psi/km ΔP). "
             "Phase 3: Choke-on-test vs production-choke alignment. "
             "PENDING FCT REPORT — estimates carry wide uncertainty until Jan-2026 FCT data lands.",
     'prereq': "January-2026 FCT report; GAP/Prosper IPM model; WHIP/WHFP-vs-time per well"},
    {'id': '4.6', 'title': 'Produced-water redistribution + R1↔R2 rebalancing',
     'category': 'Subsurface / WI', 'lo': 2000, 'hi': 2400, 'full_lo': 2400, 'full_hi': 3200,
     'conf': 'Medium', 'capex_lo': 0.5, 'capex_hi': 1.5,
     'mech': "(a) Tracer + integrity diagnosis on 139-SS and 145-SS (RM flagged R1→R2 water loss). "
             "(b) Rebalance injection: redirect 3,000-5,000 bwpd from R2 to R1. "
             "(c) Selective shut-in / rate reduction on 6 worst high-WC producers (>85% WC) to "
             "free PW capacity and improve sector VRR efficiency.",
     'prereq': "PW lab analysis (TDS, scaling, particulates, H₂S); injector PLT/CBL on 139-SS, 145-SS"},
    {'id': '4.1', 'title': 'Stimulation roll-out beyond Obj 1.1C', 'category': 'Subsurface',
     'lo': 2500, 'hi': 2500, 'full_lo': 5000, 'full_hi': 6000,
     'conf': 'Medium', 'capex_lo': 8.0, 'capex_hi': 12.0,
     'mech': "32+ R1 strings flagged 'Low intake / Low PIP / stim required' by RM. Obj 1.1C "
             "covers 5. Apply Naphtha+HCl recipe to 8-10 additional wells per year. Target wells "
             "with PI degradation D > 30%/yr (1.1C methodology). Average gain +150 to +400 BOPD "
             "per well, declining 30%/yr.",
     'prereq': "Per-well PI screening across 32 stim candidates (extension of 1.1C dashboard)"},
    {'id': '4.3', 'title': 'VSD / PWS retrofit campaign', 'category': 'Surface / Completion',
     'lo': 1600, 'hi': 1600, 'full_lo': 3300, 'full_hi': 5500,
     'conf': 'High', 'capex_lo': 2.4, 'capex_hi': 4.8,
     'mech': "22 strings flagged 'Low DP across choke / VSD required' — ESP-limited not "
             "reservoir-limited. Replace fixed-speed power with PWS-VSD; allows running at "
             "55-60 Hz to push past choke-DP-limited operating point. Already proven on "
             "10 Shah wells (SY-012, 019, 026, 035, 039, 097).",
     'prereq': "Power-system loading review (does Shah electrical infra support 8 more VSDs?)"},
    {'id': '4.4', 'title': 'ESP upsize where pump at max frequency', 'category': 'Completion',
     'lo': 800, 'hi': 800, 'full_lo': 2800, 'full_hi': 2800,
     'conf': 'Medium', 'capex_lo': 2.0, 'capex_hi': 3.2,
     'mech': "14 strings already at 55-60 Hz with no headroom (SY-073, 088, 094, 099, 100, 113). "
             "During next workover install pump from one tier higher in catalog "
             "(TE3300 → TE5000, GN3200 → GN4000). Combine with VSD where not already present.",
     'prereq': "Per-well ESP design review; align with existing WO schedule"},
    {'id': '4.2', 'title': 'BHFP rate-cap relaxation via skin reduction / PVT relocalization',
     'category': 'Subsurface', 'lo': 900, 'hi': 900, 'full_lo': 1800, 'full_hi': 1800,
     'conf': 'Med-High', 'capex_lo': 0.2, 'capex_hi': 0.5,
     'mech': "12 strings explicitly capped at low rate to keep BHFP ≥ Pb+100 (SY-040, 058, 064, "
             "085, 120, 132, 135, 014). Two paths: (a) skin reduction via stimulation reduces "
             "drawdown for same Qo; (b) per-well revisit of Pb assumption — for some R1 wells, "
             "local Pb may be lower than 392 psi.",
     'prereq': "GAP/Prosper IPM model; PVT relocalization study"},
    {'id': '4.8', 'title': 'Inactive-string reactivation acceleration', 'category': 'Cross-cut Obj 1.1B',
     'lo': 1000, 'hi': 1000, 'full_lo': 3920, 'full_hi': 3920,
     'conf': 'High', 'capex_lo': 0.5, 'capex_hi': 1.0,
     'mech': "14 inactive strings totaling 3,920 BOPD allowable (SY-035 PWS, SY-097 tie-in, "
             "SY-098 downsize, SY-115/117 ESP repl, SY-093 SAP-B fix). Speed of execution is the "
             "lever — every quarter of acceleration ≈ +1,000 BOPD avg uplift over the year.",
     'prereq': "Coordination with Obj 1.1B inactive-string KPI track"},
]

DATA_GAPS = [
    ("January-2026 FCT report", "Surface bottleneck quantification (§4.7) cannot move past estimate"),
    ("GAP/Prosper IPM surface model", "Needed to run back-pressure sensitivities"),
    ("G2V2 reservoir model — ML#5", "Needed to quantify §4.5 oil response and §4.6 R1/R2 rebalancing"),
    ("Cluster #2 / SY-148 WS FCT", "RM-mandated prerequisite for SY-180 commissioning (§4.5)"),
    ("PIDs / PFDs / vendor capacity sheets", "CDS, RDS-1, RDS-2, WI clusters"),
    ("Produced water lab analysis", "TDS, scaling, particulates, H₂S — needed for §4.6 design"),
    ("WHIP-vs-time and WHPP-vs-time per well", "Validate flowline-restriction hypothesis (§4.7)"),
    ("Injector PLT / CBL logs (139-SS, 145-SS)", "Needed for §4.6 (a) integrity hypothesis"),
    ("Per-well PI screening across 32 stim candidates", "Extension of 1.1C methodology to scope §4.1"),
]


def well_short(w):
    """Compact normalized well record for the Wells tab."""
    s = (w.get('string') or '').replace(':ST', '')
    qo = w.get('qo')
    wc = w.get('wc')
    return {
        'string': s,
        'reservoir': w.get('reservoir') or '',
        'allow': w.get('allowable') or 0,
        'tr': w.get('tr') or 0,
        'qo': round(qo, 1) if isinstance(qo, (int, float)) else None,
        'wc': round(wc, 1) if isinstance(wc, (int, float)) else None,
        'bhfp': w.get('bhfp'),
        'esp_freq': w.get('esp_freq'),
        'inactive': w.get('inactive') or 'N',
        'rm': (w.get('rm_comment') or '')[:160],
        'tags': w.get('tags') or [],
    }


def main():
    wells_short = [well_short(w) for w in wells]
    cat_rows_js = json.dumps({k: {
        'label': v['label'],
        'group': v['group'],
        'bopd_lost': v['bopd_lost'],
        'wells_affected': counts.get(k, {}).get('wells_affected'),
        'opp': v['opp'],
        'color': v['color'],
    } for k, v in CAT_META.items()})

    opps_js = json.dumps(OPPS, ensure_ascii=False)
    wells_js = json.dumps(wells_short, ensure_ascii=False)
    gaps_js = json.dumps(DATA_GAPS, ensure_ascii=False)

    html = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>PC26 1.1D · Shah Bottleneck Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #0c0d10; --panel: #14171c; --panel2: #1b1f27; --border: #232733;
  --text: #f5f7fa; --sub: #9aa3b2; --dim: #6b7280;
  --oil: #f59e0b; --oil-soft: rgba(245,158,11,0.15);
  --navy: #0a2540; --teal: #0891b2; --mint: #34d399; --water: #06b6d4;
  --bad: #dc2626; --warn: #f59e0b; --good: #16a34a;
}
* { box-sizing: border-box; }
html,body { background: var(--bg); color: var(--text); margin: 0; padding: 0;
  font-family: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 14px; line-height: 1.45; }
header { position: sticky; top: 0; z-index: 50; background: var(--navy);
  border-bottom: 2px solid var(--oil); padding: 18px 28px; }
header h1 { margin: 0; font-family: "Fraunces", Georgia, serif; font-size: 22px;
  font-weight: 700; letter-spacing: 0.2px; }
header .meta { color: var(--sub); font-size: 12px; margin-top: 4px;
  font-family: "JetBrains Mono", monospace; }
nav { position: sticky; top: 70px; z-index: 49; display: flex; gap: 2px;
  padding: 0 16px; background: var(--panel); overflow-x: auto;
  border-bottom: 1px solid var(--border); }
nav button { background: transparent; color: var(--sub); border: none;
  padding: 13px 18px; font-size: 13px; cursor: pointer;
  border-bottom: 3px solid transparent; font-family: inherit; font-weight: 500;
  white-space: nowrap; }
nav button.active { color: var(--oil); border-bottom-color: var(--oil); font-weight: 600; }
nav button:hover { color: var(--text); }
main { padding: 22px 28px 60px; max-width: 1640px; margin: 0 auto; }
.tab { display: none; }
.tab.active { display: block; }

.kpi-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
  margin-bottom: 22px; }
.kpi { background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px 18px; position: relative; overflow: hidden; }
.kpi::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--oil); }
.kpi .label { color: var(--sub); font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.6px; }
.kpi .value { font-family: "JetBrains Mono", monospace; font-size: 28px;
  font-weight: 700; color: var(--text); margin-top: 6px; }
.kpi .sub { color: var(--dim); font-size: 11px; margin-top: 4px;
  font-family: "JetBrains Mono", monospace; }

.grid { display: grid; gap: 18px; }
.grid.two { grid-template-columns: 1.2fr 1fr; }
@media (max-width: 1100px) { .grid.two { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: repeat(2, 1fr); } }

.card { background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 18px 20px; }
.card h2 { margin: 0 0 12px 0; font-family: "Fraunces", Georgia, serif;
  font-size: 17px; color: var(--text); font-weight: 600; }
.card h3 { margin: 4px 0 10px 0; color: var(--oil); font-family: "Fraunces", Georgia, serif;
  font-size: 15px; font-weight: 600; }
.card p { color: var(--sub); margin: 6px 0; font-size: 13px; }

table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 9px 11px; text-align: left; border-bottom: 1px solid var(--border);
  vertical-align: middle; }
th { color: var(--sub); font-weight: 600; cursor: pointer; user-select: none;
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px;
  background: var(--panel2); position: sticky; top: 0; }
td.num, th.num { text-align: right; font-family: "JetBrains Mono", monospace; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 10px; font-weight: 600; margin-right: 4px;
  background: rgba(245,158,11,0.15); color: var(--oil);
  font-family: "JetBrains Mono", monospace; }
.tag.water { background: rgba(6,182,212,0.18); color: #67e8f9; }
.tag.subsurface { background: rgba(52,211,153,0.18); color: #6ee7b7; }
.tag.completion { background: rgba(30,58,95,0.6); color: #93c5fd; }
.tag.surface { background: rgba(245,158,11,0.18); color: #fbbf24; }
.tag.bad { background: rgba(220,38,38,0.20); color: #fca5a5; }
.tag.good { background: rgba(22,163,74,0.18); color: #86efac; }
.tag.warn { background: rgba(245,158,11,0.18); color: #fbbf24; }

.bar-cell { display: flex; align-items: center; gap: 8px; min-width: 160px; }
.bar-cell .bar { flex: 1; height: 6px; background: var(--panel2); border-radius: 3px;
  position: relative; overflow: hidden; }
.bar-cell .bar > i { display: block; height: 100%; background: var(--oil); }
.bar-cell .num { font-family: "JetBrains Mono", monospace; min-width: 60px;
  text-align: right; font-size: 12px; }

.conf-pill { display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-size: 10px; font-weight: 700; font-family: "JetBrains Mono", monospace; }
.conf-h  { background: rgba(22,163,74,0.20); color: #86efac; }
.conf-mh { background: rgba(245,158,11,0.20); color: #fbbf24; }
.conf-m  { background: rgba(220,38,38,0.20); color: #fca5a5; }

.opp-card { background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 0; margin-bottom: 12px; overflow: hidden; }
.opp-head { padding: 14px 18px; cursor: pointer; display: flex; align-items: center;
  gap: 14px; background: linear-gradient(90deg, var(--panel2) 0%, var(--panel) 100%); }
.opp-head:hover { background: var(--panel2); }
.opp-id { font-family: "JetBrains Mono", monospace; color: var(--oil); font-weight: 700;
  font-size: 14px; min-width: 38px; }
.opp-title { font-family: "Fraunces", Georgia, serif; font-size: 15px; flex: 1; font-weight: 600; }
.opp-gain { font-family: "JetBrains Mono", monospace; color: var(--mint);
  font-weight: 700; font-size: 13px; }
.opp-body { display: none; padding: 16px 22px 20px; border-top: 1px solid var(--border); }
.opp-card.open .opp-body { display: block; }
.opp-body h4 { margin: 14px 0 6px; color: var(--oil); font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.4px; font-family: "JetBrains Mono", monospace; }
.opp-body p { margin: 4px 0; color: var(--sub); font-size: 13px; line-height: 1.55; }
.range-bar { height: 18px; background: var(--panel2); border-radius: 4px;
  position: relative; overflow: hidden; margin: 4px 0 12px; }
.range-bar > .fill { position: absolute; top: 0; bottom: 0; background: var(--oil);
  opacity: 0.85; }
.range-bar > .label { position: absolute; top: 0; bottom: 0; left: 8px; right: 8px;
  display: flex; align-items: center; color: var(--text); font-size: 11px;
  font-family: "JetBrains Mono", monospace; font-weight: 600; z-index: 1; }
.kpi-mini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  margin-bottom: 12px; }
.kpi-mini > div { background: var(--panel2); padding: 10px 12px; border-radius: 6px;
  border: 1px solid var(--border); }
.kpi-mini .l { color: var(--sub); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.4px; }
.kpi-mini .v { font-family: "JetBrains Mono", monospace; font-size: 16px;
  font-weight: 700; color: var(--text); margin-top: 2px; }

#wells-filter { background: var(--panel2); color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 8px 12px; font-family: inherit; font-size: 13px;
  width: 320px; }
#wells-filter:focus { outline: none; border-color: var(--oil); }
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 14px; }
.chip-row .chip { background: var(--panel2); color: var(--sub);
  border: 1px solid var(--border); padding: 5px 12px; border-radius: 999px;
  font-size: 11px; cursor: pointer; font-family: "JetBrains Mono", monospace; }
.chip-row .chip.active { background: var(--oil-soft); color: var(--oil);
  border-color: var(--oil); }

.sankey { font-family: "JetBrains Mono", monospace; font-size: 11px; }
.sankey text { fill: var(--text); font-family: inherit; }
.sankey .axis { fill: var(--sub); }

.note { background: rgba(220,38,38,0.08); border-left: 3px solid var(--bad);
  padding: 10px 14px; color: var(--sub); font-size: 12px; margin: 10px 0;
  border-radius: 4px; }

.footer { color: var(--dim); font-size: 11px; padding: 30px 28px 10px;
  font-family: "JetBrains Mono", monospace; text-align: center; }

canvas { background: transparent !important; }
</style>
</head>
<body>

<header>
  <h1>Shah Field De-Bottlenecking · PC26 Obj 1.1D</h1>
  <div class="meta">TotalEnergies ALSG × ADNOC Onshore · Asset Lead FP: Andrey Semenov · Issued __ISSUED__</div>
</header>

<nav>
  <button class="tabbtn active" data-tab="overview">Overview</button>
  <button class="tabbtn" data-tab="map">Bottleneck Map</button>
  <button class="tabbtn" data-tab="opps">Opportunities</button>
  <button class="tabbtn" data-tab="wells">Wells (__N__)</button>
  <button class="tabbtn" data-tab="gaps">Data Gaps</button>
</nav>

<main>

<!-- OVERVIEW -->
<section class="tab active" id="overview">
  <div class="kpi-strip">
    <div class="kpi"><div class="label">Field Actual (FAR)</div><div class="value">75,733</div><div class="sub">BOPD · Q1-2026</div></div>
    <div class="kpi"><div class="label">2026 Uplift Envelope</div><div class="value">+10–12k</div><div class="sub">BOPD · 25% overlap-deducted</div></div>
    <div class="kpi"><div class="label">Opportunities</div><div class="value">8</div><div class="sub">5 subsurface · 2 surface · 1 cross</div></div>
    <div class="kpi"><div class="label">Critical Data Gaps</div><div class="value">9</div><div class="sub">FCT + IPM model top of list</div></div>
  </div>

  <div class="grid two">
    <div class="card">
      <h2>Field baseline — Allowable vs TR vs Actual</h2>
      <canvas id="baseline-chart" height="180"></canvas>
      <p style="margin-top:10px"><span style="color:var(--text);font-weight:600">Allowable 76,671</span> · TR 79,983 · FAR 75,733 BOPD — under-delivery gap of <b style="color:var(--warn)">4,250 BOPD (5.6%)</b>. Including inactive strings the allowable rises to 80,591 BOPD; ceiling deliverability ~102,752 BOPD.</p>
    </div>
    <div class="card">
      <h2>Water injection — current vs target</h2>
      <canvas id="wi-chart" height="180"></canvas>
      <p style="margin-top:10px">Field WI actual <b>53,000 bwpd</b> vs technical rate <b>71,000 bwpd</b>. SY-175 + SY-180 commissioning unlocks +16,000 bwpd of stranded capacity. Cluster physical caps 25/26 Mbwpd each.</p>
    </div>
  </div>

  <div class="card" style="margin-top:18px">
    <h2>9 bottleneck categories — wells affected & BOPD lost</h2>
    <table id="bottleneck-table">
      <thead><tr><th>ID</th><th>Category</th><th>Group</th><th class="num">Wells affected</th><th>BOPD lost vs cap</th><th>Linked opportunity</th></tr></thead>
      <tbody id="bt-body"></tbody>
    </table>
  </div>

  <div class="card" style="margin-top:18px">
    <h2>Opportunity ranking — 2026 realistic gain (BOPD)</h2>
    <canvas id="opp-rank-chart" height="200"></canvas>
    <p style="margin-top:10px">Ranking uses the midpoint of the 2026-realistic gain range. After 25% overlap deduction (§4.1 + §4.3 + §4.4 share wells) the envelope is <b style="color:var(--mint)">~10,000–12,000 BOPD (+13% field uplift)</b> — comparable to the Saih Rawl Shuaiba debottlenecking outcome (SPE 68222: +6,300 BOPD on a smaller system).</p>
  </div>
</section>

<!-- BOTTLENECK MAP -->
<section class="tab" id="map">
  <div class="card">
    <h2>Bottleneck flow — current actual → 8 opportunities → target envelope</h2>
    <p>SVG flow chart: each wedge sized by 2026-realistic gain midpoint. Order matches the consolidated ranking. Hover any wedge for opportunity title and gain range.</p>
    <div id="sankey-host" style="width:100%; overflow-x:auto; padding-top:10px"></div>
  </div>

  <div class="grid two" style="margin-top:18px">
    <div class="card">
      <h2>Wells per bottleneck category</h2>
      <canvas id="cat-wells-chart" height="200"></canvas>
    </div>
    <div class="card">
      <h2>BOPD lost per bottleneck (where quantifiable)</h2>
      <canvas id="cat-bopd-chart" height="200"></canvas>
      <p style="margin-top:10px"><span class="tag bad">C3 / W1 / W2 / W3 / W4</span> not quantified per-well from the Allowable — needs FCT, integrity logs, and tracer data.</p>
    </div>
  </div>
</section>

<!-- OPPORTUNITIES -->
<section class="tab" id="opps">
  <div class="card">
    <h2>8 quantified opportunities — click to expand</h2>
    <p>Each card shows the 2026-realistic gain range, full potential, capex bracket, mechanism, and prerequisite data/work. Confidence is colour-coded: <span class="conf-pill conf-h">High</span> <span class="conf-pill conf-mh">Med-High</span> <span class="conf-pill conf-m">Medium</span>.</p>
    <div id="opps-list" style="margin-top:14px"></div>
  </div>
</section>

<!-- WELLS -->
<section class="tab" id="wells">
  <div class="card">
    <h2>All __N__ strings — RM-tagged constraints</h2>
    <input id="wells-filter" placeholder="Search by string, reservoir, RM comment…" />
    <div class="chip-row" id="chip-row"></div>
    <table id="wells-table">
      <thead><tr>
        <th data-k="string">String</th>
        <th data-k="reservoir">Reservoir</th>
        <th class="num" data-k="allow">Allow.</th>
        <th class="num" data-k="tr">TR</th>
        <th class="num" data-k="qo">Latest Qo</th>
        <th class="num" data-k="wc">WC %</th>
        <th class="num" data-k="bhfp">BHFP</th>
        <th class="num" data-k="esp_freq">ESP Hz</th>
        <th data-k="inactive">Status</th>
        <th data-k="tags">Bottleneck tags</th>
        <th data-k="rm">RM comment</th>
      </tr></thead>
      <tbody id="wells-body"></tbody>
    </table>
    <p style="margin-top:10px; color:var(--dim); font-size:11px;">Sorting: click any column header. Filter: text search across all columns AND chip filters (multi-select OR). Source: <code>Shah Q2 2026 Allowable-V1 (final).xlsx</code>, sheet <code>Q2-2026 OP Allowable RM_Upd</code>, rows 11-134.</p>
  </div>
</section>

<!-- DATA GAPS -->
<section class="tab" id="gaps">
  <div class="card">
    <h2>9 critical data items still required</h2>
    <p>Ranked by impact on deliverable confidence. Items 1-4 are blockers for tightening the §4.5 and §4.7 estimates — the two largest opportunities.</p>
    <table>
      <thead><tr><th style="width:40px">#</th><th>Item</th><th>Why needed</th></tr></thead>
      <tbody id="gaps-body"></tbody>
    </table>
    <div class="note">All §4.7 surface-back-pressure estimates carry wide uncertainty until the Jan-2026 FCT report and GAP/Prosper IPM surface model become available.</div>
  </div>
</section>

</main>

<div class="footer">PC26 Obj 1.1D · Generated offline from Q2-2026 Allowable file · Chart.js 4.4.0 · No live API calls</div>

<script>
const CATS = __CATS__;
const OPPS = __OPPS__;
const WELLS = __WELLS__;
const GAPS = __GAPS__;

// ===== TABS =====
document.querySelectorAll('.tabbtn').forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll('.tabbtn').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  b.classList.add('active');
  document.getElementById(b.dataset.tab).classList.add('active');
}));

// ===== Chart.js defaults (guarded — page still works if CDN failed) =====
const CHART_AVAILABLE = (typeof Chart !== 'undefined');
if (CHART_AVAILABLE) {
  Chart.defaults.color = '#9aa3b2';
  Chart.defaults.borderColor = '#232733';
  Chart.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
} else {
  console.warn('Chart.js not loaded — charts will display placeholders, data tables unaffected.');
  document.querySelectorAll('canvas').forEach(c => {
    const ph = document.createElement('div');
    ph.style.cssText = 'padding:20px; color:var(--sub); text-align:center; border:1px dashed var(--border); border-radius:6px; font-family:"JetBrains Mono",monospace; font-size:12px;';
    ph.textContent = '[Chart unavailable — Chart.js failed to load]';
    c.replaceWith(ph);
  });
}
function safeChart(el, cfg) { if (CHART_AVAILABLE && el) new Chart(el, cfg); }

// ===== Baseline chart =====
safeChart(document.getElementById('baseline-chart'), {
  type: 'bar',
  data: {
    labels: ['Actual (FAR)','Allowable','TR','Allow w/ Inactive','Deliv. ceiling'],
    datasets: [{ label: 'BOPD',
      data: [75733, 76671, 79983, 80591, 102752],
      backgroundColor: ['#f59e0b','#0891b2','#34d399','#06b6d4','#1e3a5f']
    }]
  },
  options: {
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#1b1f27' }, ticks: { callback: v => v.toLocaleString() } },
      x: { grid: { display: false } }
    }
  }
});

// ===== WI chart =====
safeChart(document.getElementById('wi-chart'), {
  type: 'bar',
  data: {
    labels: ['w/ SY-175+180','w/o SY-175+180','Tech rate','Actual'],
    datasets: [
      { label: 'Cluster #1', data: [26000, 26000, 42200, 34000], backgroundColor: '#0891b2' },
      { label: 'Cluster #2', data: [24600, 19000, 28800, 19000], backgroundColor: '#06b6d4' }
    ]
  },
  options: {
    plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } },
    scales: {
      y: { beginAtZero: true, stacked: true, grid: { color: '#1b1f27' },
           ticks: { callback: v => v.toLocaleString() } },
      x: { stacked: true, grid: { display: false } }
    }
  }
});

// ===== Bottleneck table =====
const btBody = document.getElementById('bt-body');
Object.entries(CATS).forEach(([id, c]) => {
  const maxBOPD = 12000;
  const pct = c.bopd_lost ? Math.round(c.bopd_lost / maxBOPD * 100) : 0;
  const groupTag = c.group.includes('Surface') ? 'surface'
    : c.group.includes('Water') ? 'water'
    : c.group.includes('Completion') ? 'completion' : 'subsurface';
  btBody.insertAdjacentHTML('beforeend', `
    <tr>
      <td><span class="tag">${id}</span></td>
      <td>${c.label}</td>
      <td><span class="tag ${groupTag}">${c.group}</span></td>
      <td class="num">${c.wells_affected ?? '—'}</td>
      <td><div class="bar-cell"><div class="bar"><i style="width:${pct}%"></i></div><span class="num">${c.bopd_lost ? c.bopd_lost.toLocaleString() : 'TBD'}</span></div></td>
      <td><span class="tag">${c.opp}</span></td>
    </tr>`);
});

// ===== Opportunity ranking chart =====
const ranked = [...OPPS].sort((a,b) => ((b.lo+b.hi)/2)-((a.lo+a.hi)/2));
safeChart(document.getElementById('opp-rank-chart'), {
  type: 'bar',
  data: {
    labels: ranked.map(o => `§${o.id}`),
    datasets: [
      { label: '2026 low',  data: ranked.map(o => o.lo), backgroundColor: '#f59e0b' },
      { label: '2026 range (low→high)', data: ranked.map(o => o.hi - o.lo), backgroundColor: 'rgba(245,158,11,0.35)' }
    ]
  },
  options: {
    indexAxis: 'y',
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10 } },
      tooltip: { callbacks: {
        title: (it) => { const o = ranked[it[0].dataIndex]; return `§${o.id} ${o.title}`; },
        label: (it) => { const o = ranked[it.dataIndex]; return `${o.lo.toLocaleString()}–${o.hi.toLocaleString()} BOPD · ${o.conf}`; }
      } }
    },
    scales: {
      x: { stacked: true, grid: { color: '#1b1f27' },
           ticks: { callback: v => v.toLocaleString() + ' BOPD' } },
      y: { stacked: true, grid: { display: false } }
    }
  }
});

// ===== Sankey-style SVG flow =====
function renderSankey() {
  const host = document.getElementById('sankey-host');
  const start = 75733;
  const incrs = ranked.map(o => ({ id: o.id, title: o.title, lo: o.lo, hi: o.hi,
    mid: (o.lo+o.hi)/2,
    actual_inc: ['4.1','4.3','4.4'].includes(o.id) ? Math.round(o.lo*0.75) : o.lo }));
  const cum = [start];
  let c = start;
  incrs.forEach(i => { c += i.actual_inc; cum.push(c); });
  const target = c;
  const W = 1500, H = 360, padL = 60, padR = 40, padT = 30, padB = 90;
  const xs = Array.from({length: cum.length}, (_,i) => padL + i*(W-padL-padR)/(cum.length-1));
  const yScale = v => H - padB - (v - start*0.96) * (H - padT - padB) / (target*1.02 - start*0.96);
  const colors = ['#0891b2','#f59e0b','#06b6d4','#34d399','#1e3a5f','#475569','#fbbf24','#16a34a'];

  let svg = `<svg class="sankey" viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet">`;
  // baseline grid
  svg += `<line x1="${padL}" y1="${H-padB}" x2="${W-padR}" y2="${H-padB}" stroke="#232733" stroke-dasharray="4 4"/>`;
  // Wedges
  for (let i = 0; i < incrs.length; i++) {
    const x0 = xs[i], x1 = xs[i+1];
    const y0a = yScale(cum[i]), y0b = H - padB;
    const y1a = yScale(cum[i+1]), y1b = H - padB;
    svg += `<path d="M ${x0} ${y0a} L ${x1} ${y1a} L ${x1} ${y1b} L ${x0} ${y0b} Z" fill="${colors[i % colors.length]}" opacity="0.85"><title>§${incrs[i].id} ${incrs[i].title}\n+${incrs[i].actual_inc.toLocaleString()} BOPD (2026 low, overlap-adjusted)\n2026 range ${incrs[i].lo.toLocaleString()}–${incrs[i].hi.toLocaleString()}</title></path>`;
    // wedge label
    const xm = (x0+x1)/2, ym = (yScale(cum[i+1]) + (H-padB))/2;
    svg += `<text x="${xm}" y="${ym}" text-anchor="middle" font-size="11" fill="#0c0d10" font-weight="700">§${incrs[i].id}</text>`;
    svg += `<text x="${xm}" y="${ym+13}" text-anchor="middle" font-size="10" fill="#0c0d10">+${incrs[i].actual_inc.toLocaleString()}</text>`;
  }
  // cumulative line
  let path = `M ${xs[0]} ${yScale(cum[0])}`;
  for (let i = 1; i < cum.length; i++) path += ` L ${xs[i]} ${yScale(cum[i])}`;
  svg += `<path d="${path}" fill="none" stroke="#f5f7fa" stroke-width="2.5"/>`;
  cum.forEach((v, i) => {
    svg += `<circle cx="${xs[i]}" cy="${yScale(v)}" r="4" fill="#f59e0b" stroke="#0c0d10" stroke-width="2"/>`;
    svg += `<text x="${xs[i]}" y="${yScale(v)-12}" text-anchor="middle" font-size="11" fill="#f5f7fa" font-weight="700">${v.toLocaleString()}</text>`;
  });
  // x-axis labels
  const labels = ['Start (FAR)', ...incrs.map(i => '§' + i.id), 'Envelope'];
  labels.forEach((l, i) => {
    svg += `<text x="${xs[i] !== undefined ? xs[i] : xs[xs.length-1]}" y="${H-padB+24}" text-anchor="middle" font-size="11" class="axis">${l}</text>`;
  });
  svg += `<text x="${padL}" y="${padT}" font-size="12" fill="#9aa3b2">BOPD →</text>`;
  svg += `<text x="${xs[0]}" y="${yScale(start)+22}" text-anchor="middle" font-size="11" fill="#9aa3b2">Current</text>`;
  svg += `<text x="${xs[xs.length-1]}" y="${yScale(target)+22}" text-anchor="middle" font-size="11" fill="#f59e0b">+${(target-start).toLocaleString()} BOPD</text>`;
  svg += `</svg>`;
  host.innerHTML = svg;
}
renderSankey();

// ===== category bar charts =====
const catEntries = Object.entries(CATS);
safeChart(document.getElementById('cat-wells-chart'), {
  type: 'bar',
  data: {
    labels: catEntries.map(([k,v]) => `${k} · ${v.label.substring(0,22)}`),
    datasets: [{ data: catEntries.map(([k,v]) => v.wells_affected || 0),
      backgroundColor: catEntries.map(([k,v]) => v.color) }]
  },
  options: { indexAxis: 'y', plugins: { legend: { display: false } },
    scales: { x: { grid: { color: '#1b1f27' } }, y: { grid: { display: false } } } }
});
const quant = catEntries.filter(([k,v]) => v.bopd_lost);
safeChart(document.getElementById('cat-bopd-chart'), {
  type: 'bar',
  data: {
    labels: quant.map(([k,v]) => `${k} · ${v.label.substring(0,22)}`),
    datasets: [{ data: quant.map(([k,v]) => v.bopd_lost),
      backgroundColor: quant.map(([k,v]) => v.color) }]
  },
  options: { indexAxis: 'y', plugins: { legend: { display: false } },
    scales: { x: { grid: { color: '#1b1f27' }, ticks: { callback: v => v.toLocaleString() } },
              y: { grid: { display: false } } } }
});

// ===== Opportunities accordion =====
const oppsList = document.getElementById('opps-list');
const confClass = c => c === 'High' ? 'conf-h' : c === 'Med-High' ? 'conf-mh' : 'conf-m';
ranked.forEach(o => {
  const mid = (o.lo + o.hi) / 2;
  const maxGain = 3500;
  const fillPct = Math.min(100, (o.hi / maxGain) * 100);
  const loPct = (o.lo / maxGain) * 100;
  oppsList.insertAdjacentHTML('beforeend', `
    <div class="opp-card">
      <div class="opp-head">
        <span class="opp-id">§${o.id}</span>
        <span class="opp-title">${o.title}</span>
        <span class="conf-pill ${confClass(o.conf)}">${o.conf}</span>
        <span class="opp-gain">+${o.lo.toLocaleString()}${o.lo!==o.hi?'–'+o.hi.toLocaleString():''} BOPD</span>
      </div>
      <div class="opp-body">
        <div class="kpi-mini">
          <div><div class="l">2026 Realistic</div><div class="v">${o.lo.toLocaleString()}–${o.hi.toLocaleString()}</div></div>
          <div><div class="l">Full Potential</div><div class="v">${o.full_lo.toLocaleString()}–${o.full_hi.toLocaleString()}</div></div>
          <div><div class="l">Capex Bracket</div><div class="v">$${o.capex_lo}–${o.capex_hi}M</div></div>
        </div>
        <h4>Gain range — 2026 realistic</h4>
        <div class="range-bar"><div class="fill" style="left:${loPct}%; width:${fillPct-loPct}%"></div><span class="label">${o.lo.toLocaleString()} → ${o.hi.toLocaleString()} BOPD</span></div>
        <h4>Mechanism</h4><p>${o.mech}</p>
        <h4>Prerequisite data / work</h4><p>${o.prereq}</p>
        <h4>Category</h4><p>${o.category}</p>
      </div>
    </div>`);
});
document.querySelectorAll('.opp-card .opp-head').forEach(h =>
  h.addEventListener('click', () => h.parentElement.classList.toggle('open')));

// ===== Wells table =====
const wellsBody = document.getElementById('wells-body');
const tagColor = t => {
  if (t.startsWith('S')) return 'subsurface';
  if (t.startsWith('C')) return t === 'C2' ? 'completion' : 'surface';
  return 'water';
};
function fmt(v, suffix='') { return (v === null || v === undefined || v === '') ? '—' : (typeof v === 'number' ? v.toLocaleString() : v) + suffix; }
let sortKey = 'allow', sortDesc = true;
let activeChips = new Set();
let searchText = '';

function renderWells() {
  const f = searchText.toLowerCase();
  let rows = WELLS.filter(w => {
    if (activeChips.size && !w.tags.some(t => activeChips.has(t))) return false;
    if (!f) return true;
    return (w.string + ' ' + w.reservoir + ' ' + w.rm + ' ' + w.tags.join(' ')).toLowerCase().includes(f);
  });
  rows.sort((a,b) => {
    let va = a[sortKey], vb = b[sortKey];
    if (Array.isArray(va)) va = va.join(',');
    if (Array.isArray(vb)) vb = vb.join(',');
    if (va === null || va === undefined) va = '';
    if (vb === null || vb === undefined) vb = '';
    if (typeof va === 'number' && typeof vb === 'number') return sortDesc ? vb-va : va-vb;
    return sortDesc ? String(vb).localeCompare(String(va)) : String(va).localeCompare(String(vb));
  });
  wellsBody.innerHTML = rows.map(w => `
    <tr>
      <td><b>${w.string}</b></td>
      <td>${w.reservoir}</td>
      <td class="num">${fmt(w.allow)}</td>
      <td class="num">${fmt(w.tr)}</td>
      <td class="num">${fmt(w.qo)}</td>
      <td class="num">${w.wc !== null ? w.wc.toFixed(1) : '—'}</td>
      <td class="num">${fmt(w.bhfp)}</td>
      <td class="num">${fmt(w.esp_freq)}</td>
      <td>${w.inactive === 'Y' ? '<span class="tag bad">INA</span>' : w.inactive === 'DISCONNECTED' ? '<span class="tag bad">DISC</span>' : w.inactive === 'OBSERVER' ? '<span class="tag warn">OBS</span>' : '<span class="tag good">ON</span>'}</td>
      <td>${w.tags.map(t => `<span class="tag ${tagColor(t)}">${t}</span>`).join('')}</td>
      <td style="color:var(--sub); font-size:12px;">${w.rm}</td>
    </tr>`).join('');
}

// chip row
const chipRow = document.getElementById('chip-row');
chipRow.innerHTML = Object.keys(CATS).map(k => `<span class="chip" data-cat="${k}">${k} (${CATS[k].wells_affected || 0})</span>`).join('') + '<span class="chip" data-cat="__clear__">Clear filters</span>';
chipRow.addEventListener('click', e => {
  if (!e.target.classList.contains('chip')) return;
  const k = e.target.dataset.cat;
  if (k === '__clear__') { activeChips.clear(); chipRow.querySelectorAll('.chip').forEach(x => x.classList.remove('active')); }
  else {
    if (activeChips.has(k)) { activeChips.delete(k); e.target.classList.remove('active'); }
    else { activeChips.add(k); e.target.classList.add('active'); }
  }
  renderWells();
});

document.getElementById('wells-filter').addEventListener('input', e => { searchText = e.target.value; renderWells(); });
document.querySelectorAll('#wells-table th').forEach(th => th.addEventListener('click', () => {
  const k = th.dataset.k;
  if (sortKey === k) sortDesc = !sortDesc; else { sortKey = k; sortDesc = true; }
  renderWells();
}));
renderWells();

// ===== Gaps =====
document.getElementById('gaps-body').innerHTML = GAPS.map((g, i) =>
  `<tr><td><span class="tag">${i+1}</span></td><td><b>${g[0]}</b></td><td style="color:var(--sub)">${g[1]}</td></tr>`).join('');

</script>
</body></html>"""

    html = (html
            .replace('__CATS__', cat_rows_js)
            .replace('__OPPS__', opps_js)
            .replace('__WELLS__', wells_js)
            .replace('__GAPS__', gaps_js)
            .replace('__N__', str(len(wells_short)))
            .replace('__ISSUED__', '19-May-2026'))
    OUT.write_text(html)
    print(f'Wrote {OUT}  ({OUT.stat().st_size//1024} KB)')

if __name__ == '__main__':
    main()
