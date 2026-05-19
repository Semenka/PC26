"""
PC26 Obj 1.1D — Single-file dark HTML dashboard
Chart.js 4.4.0 + Fraunces / IBM Plex Sans / JetBrains Mono
Tabs: Overview · Bottleneck Map · Opportunities · Wells · Data Gaps
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WELLS_JSON = ROOT / "scripts" / "wells.json"
OUT = ROOT / "deliverables" / "PC26_1.1D_Bottleneck_Dashboard.html"

data = json.loads(WELLS_JSON.read_text())

# Strip the rm_all helper field; keep what the table needs
wells_min = []
for p in data["producers"]:
    wells_min.append({
        "cmpl":      p["cmpl"],
        "uwi":       p["uwi"],
        "res":       p["reservoir"],
        "string":    p["string"],
        "alw":       p["allowable"],
        "tr":        p["tr"],
        "qo":        p["qo"],
        "wc":        p["wc"],
        "pi":        p["pi"],
        "bhfp":      p["bhfp"],
        "freq":      p["freq"],
        "inact":     p["inactive"],
        "cats":      p["cats"],
        "rm":        (p["rm"] or p["rm_prev"])[:240],
    })

wi_min = [
    {"well": w["well"], "res": w["reservoir"], "alw": w["alw_with"],
     "max_wo": w["alw_without"], "tr": w["tr"], "actual": w["actual"],
     "whip": w["whip"], "rm": w["rm"][:240]}
    for w in data["wi"]
]

# Bottleneck categories (from §ANALYSIS BLOCK — canonical numbers)
BOTTLENECKS = [
    {"id":"S1", "label":"Low PIP / stim candidate",                    "type":"Subsurface", "wells":32, "bopd":12000, "link":"§4.1"},
    {"id":"S2", "label":"High water cut (>60%)",                       "type":"Subsurface", "wells":38, "bopd":7000,  "link":"§4.6 + 1.2A"},
    {"id":"S3", "label":"Low BHFP — close to Pb",                      "type":"Subsurface", "wells":12, "bopd":1800,  "link":"§4.2"},
    {"id":"S4", "label":"Inactive strings — WO backlog",               "type":"Subsurface", "wells":14, "bopd":3920,  "link":"§4.8 + 1.1B"},
    {"id":"S5", "label":"Reservoir pressure depletion",                "type":"Subsurface", "wells":8,  "bopd":5000,  "link":"§4.5"},
    {"id":"C1", "label":"Low DP across choke / VSD required",          "type":"Surface",    "wells":22, "bopd":6500,  "link":"§4.3"},
    {"id":"C2", "label":"ESP at max frequency",                        "type":"Completion", "wells":14, "bopd":3500,  "link":"§4.4"},
    {"id":"C3", "label":"High back-pressure (flowline / station)",     "type":"Surface",    "wells":None,"bopd":3000, "link":"§4.7"},
    {"id":"W1", "label":"Cluster capacity ceiling 26 Mbwpd",           "type":"WI",         "wells":None,"bopd":None, "link":"§4.5 Ph 2"},
    {"id":"W2", "label":"WI well integrity (SY-175, SY-180)",          "type":"WI",         "wells":2,   "bopd":None, "link":"§4.5 Ph 1"},
    {"id":"W3", "label":"R1↔R2 inter-reservoir water loss",            "type":"WI",         "wells":2,   "bopd":None, "link":"§4.6 (a)"},
    {"id":"W4", "label":"High-WC producers loading PW system",        "type":"WI",         "wells":12,  "bopd":None, "link":"§4.6 (c)"},
]

# Opportunities, ranked by midpoint of 2026 gain
OPPS = [
    {"id":"4.5","title":"WI capacity uplift (SY-175 + SY-180 + cluster review)",
     "category":"Subsurface / WI","low":2500,"high":4000,"full_low":4000,"full_high":5500,
     "conf":"Med-High","capex_low":2.0,"capex_high":28.0,
     "mechanism":"Phase 1: complete WO on SY-175 & SY-180 to recover 16,000 bwpd stranded capacity. Phase 2 (2027): Cluster #2 capacity uplift study based on Jan-2026 FCT. Phase 3: new WI well drilling if VRR confirms additional voidage to fill. Sector pressure recovery lifts Qo across ~30 R1/R2 producers. Saih Rawl analog (SPE 68222): ~12% oil rate uplift per 30% WI rate increase at mature waterflood stage.",
     "prereq":"Cluster #2 / SY-148 WS FCT (RM-mandated before SY-180 commissioning); G2V2 ML#5 forecast"},
    {"id":"4.7","title":"Surface back-pressure optimization",
     "category":"Surface","low":1500,"high":2500,"full_low":2300,"full_high":3300,
     "conf":"Medium","capex_low":0.2,"capex_high":8.0,
     "mechanism":"Phase 1: Station header pressure setpoint review (CDS / RDS-1 / RDS-2). Each 10 psi separator pressure reduction across 80 R1 producers ≈ +800 BOPD. Phase 2: Selective flowline looping on 2-3 worst segments (>200 psi/km ΔP). Phase 3: Choke-on-test vs production-choke alignment.",
     "prereq":"January-2026 FCT report; GAP/Prosper IPM model; WHIP/WHFP-vs-time per well — pending FCT report"},
    {"id":"4.6","title":"Produced-water redistribution + R1↔R2 rebalancing",
     "category":"Subsurface / WI","low":2000,"high":2400,"full_low":2400,"full_high":3200,
     "conf":"Medium","capex_low":0.5,"capex_high":1.5,
     "mechanism":"(a) Tracer + integrity diagnosis on 139-SS and 145-SS (RM flagged R1→R2 water loss). (b) Rebalance injection: redirect 3,000-5,000 bwpd from R2 to R1. (c) Selective shut-in / rate reduction on 6 worst high-WC producers (>85% WC) to free PW capacity and improve sector VRR efficiency.",
     "prereq":"PW lab analysis (TDS, scaling, particulates, H₂S); injector PLT/CBL on 139-SS, 145-SS"},
    {"id":"4.1","title":"Stimulation roll-out beyond Obj 1.1C",
     "category":"Subsurface","low":2500,"high":2500,"full_low":5000,"full_high":6000,
     "conf":"Medium","capex_low":8.0,"capex_high":12.0,
     "mechanism":"32+ R1 strings flagged 'Low intake / Low PIP / stim required' by RM. Obj 1.1C covers 5. Apply Naphtha+HCl recipe to 8-10 additional wells per year. Target wells with PI degradation D > 30%/yr (1.1C methodology). Average gain +150 to +400 BOPD per well, declining 30%/yr.",
     "prereq":"Per-well PI screening across 32 stim candidates (extension of 1.1C dashboard)"},
    {"id":"4.3","title":"VSD / PWS retrofit campaign",
     "category":"Surface / Completion","low":1600,"high":1600,"full_low":3300,"full_high":5500,
     "conf":"High","capex_low":2.4,"capex_high":4.8,
     "mechanism":"22 strings flagged 'Low DP across choke / VSD required' — ESP-limited not reservoir-limited. Replace fixed-speed power with PWS-VSD; allows running at 55-60 Hz to push past choke-DP-limited operating point. Already proven on 10 Shah wells (SY-012, 019, 026, 035, 039, 097).",
     "prereq":"Power-system loading review (does Shah electrical infra support 8 more VSDs?)"},
    {"id":"4.4","title":"ESP upsize where pump at max frequency",
     "category":"Completion","low":800,"high":800,"full_low":2800,"full_high":2800,
     "conf":"Medium","capex_low":2.0,"capex_high":3.2,
     "mechanism":"14 strings already at 55-60 Hz with no headroom (SY-073, 088, 094, 099, 100, 113). During next workover install pump from one tier higher in catalog (TE3300 → TE5000, GN3200 → GN4000). Combine with VSD where not already present.",
     "prereq":"Per-well ESP design review; align with existing WO schedule"},
    {"id":"4.2","title":"BHFP rate-cap relaxation via skin reduction / PVT relocalization",
     "category":"Subsurface","low":900,"high":900,"full_low":1800,"full_high":1800,
     "conf":"Med-High","capex_low":0.2,"capex_high":0.5,
     "mechanism":"12 strings explicitly capped at low rate to keep BHFP ≥ Pb+100 (SY-040, 058, 064, 085, 120, 132, 135, 014). Two paths: (a) skin reduction via stimulation reduces drawdown for same Qo; (b) per-well revisit of Pb assumption — for some R1 wells, local Pb may be lower than 392 psi.",
     "prereq":"GAP/Prosper IPM model; PVT relocalization study"},
    {"id":"4.8","title":"Inactive-string reactivation acceleration",
     "category":"Cross-cut Obj 1.1B","low":1000,"high":1000,"full_low":3920,"full_high":3920,
     "conf":"High","capex_low":0.5,"capex_high":1.0,
     "mechanism":"14 inactive strings totaling 3,920 BOPD allowable (SY-035 PWS, SY-097 tie-in, SY-098 downsize, SY-115/117 ESP repl, SY-093 SAP-B fix). Speed of execution is the lever — every quarter of acceleration ≈ +1,000 BOPD avg uplift over the year.",
     "prereq":"Coordination with Obj 1.1B inactive-string KPI track"},
]

DATA_GAPS = [
    ("January-2026 FCT report",            "Surface bottleneck quantification (§4.7) cannot move past estimate"),
    ("GAP/Prosper IPM surface model",      "Needed to run back-pressure sensitivities"),
    ("G2V2 reservoir model — ML#5",        "Needed to quantify §4.5 oil response and §4.6 R1/R2 rebalancing"),
    ("Cluster #2 / SY-148 WS FCT",         "RM-mandated prerequisite for SY-180 commissioning (§4.5)"),
    ("PIDs / PFDs / vendor capacity sheets", "CDS, RDS-1, RDS-2, WI clusters"),
    ("Produced water lab analysis",        "TDS, scaling, particulates, H₂S — needed for §4.6 design"),
    ("WHIP-vs-time / WHPP-vs-time per well", "Needed to validate flowline-restriction hypothesis (§4.7)"),
    ("Injector PLT / CBL logs (139-SS, 145-SS)", "Needed for §4.6 (a) integrity hypothesis"),
    ("Per-well PI screening (32 stim candidates)", "Extension of 1.1C methodology to scope §4.1"),
]

# ---- Build HTML ----
WELLS_JSON_INLINE = json.dumps(wells_min, separators=(",",":"))
WI_JSON_INLINE    = json.dumps(wi_min,    separators=(",",":"))
BOTTLENECKS_JSON  = json.dumps(BOTTLENECKS,separators=(",",":"))
OPPS_JSON         = json.dumps(OPPS,      separators=(",",":"))
GAPS_JSON         = json.dumps(DATA_GAPS, separators=(",",":"))

html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PC26 1.1D · Shah De-Bottlenecking Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg:#0c0d10; --panel:#13161c; --panel2:#181c24; --line:#1f242e;
  --text:#e8eaee; --sub:#8b94a3; --dim:#5b6577;
  --oil:#f59e0b; --navy:#0a2540; --teal:#0891b2; --mint:#34d399;
  --water:#06b6d4; --ok:#16a34a; --warn:#f59e0b; --bad:#dc2626;
}
* { box-sizing: border-box; }
html,body { background:var(--bg); color:var(--text); margin:0; padding:0;
  font-family:"IBM Plex Sans", -apple-system, system-ui, sans-serif; font-size:14px; }
header { position:sticky; top:0; z-index:50; padding:18px 28px;
  background:linear-gradient(180deg,#0a2540 0%, #0c0d10 100%);
  border-bottom:2px solid var(--oil); }
header h1 { margin:0; font-family:"Fraunces", Georgia, serif; font-size:22px; font-weight:700;
  letter-spacing:.2px; }
header .sub { color:var(--sub); font-size:12px; margin-top:4px;
  font-family:"JetBrains Mono", monospace; }
nav { display:flex; gap:2px; padding:0 16px; background:var(--panel);
  overflow-x:auto; border-bottom:1px solid var(--line); position:sticky; top:74px; z-index:40; }
nav button { background:transparent; color:var(--sub); border:none;
  padding:14px 20px; font-size:13px; cursor:pointer; border-bottom:3px solid transparent;
  font-family:inherit; letter-spacing:.3px; text-transform:uppercase; font-weight:500; }
nav button.active { color:var(--oil); border-bottom-color:var(--oil); }
nav button:hover { color:var(--text); }
main { padding:22px 28px; max-width:1500px; margin:0 auto; }
.tab { display:none; } .tab.active { display:block; }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }
.kpi { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--oil);
  padding:16px 18px; border-radius:6px; }
.kpi .lbl { font-size:11px; color:var(--sub); letter-spacing:.6px;
  text-transform:uppercase; font-family:"JetBrains Mono", monospace; }
.kpi .val { font-family:"JetBrains Mono", monospace; font-size:28px; font-weight:700;
  color:var(--text); margin-top:6px; line-height:1; }
.kpi .unit { font-size:13px; color:var(--sub); margin-left:6px; font-weight:500; }
.kpi.teal { border-left-color:var(--teal); }
.kpi.mint { border-left-color:var(--mint); }
.kpi.bad  { border-left-color:var(--bad);  }
.grid { display:grid; gap:16px; }
.grid.two { grid-template-columns:1fr 1fr; }
.grid.three { grid-template-columns:repeat(3,1fr); }
@media (max-width:900px) { .grid.two,.grid.three { grid-template-columns:1fr; } .kpis { grid-template-columns:repeat(2,1fr); } }
.card { background:var(--panel); border:1px solid var(--line); border-radius:6px;
  padding:18px 20px; margin-bottom:16px; }
.card h2 { margin:0 0 14px 0; font-family:"Fraunces", Georgia, serif; font-size:18px;
  color:var(--text); font-weight:600; letter-spacing:.2px; }
.card h2 .tag { font-family:"JetBrains Mono", monospace; font-size:11px; color:var(--oil);
  background:rgba(245,158,11,.1); padding:3px 8px; border-radius:3px; margin-left:8px;
  letter-spacing:.5px; text-transform:uppercase; }
.card .note { color:var(--sub); font-size:12px; margin-top:6px;
  font-style:italic; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { color:var(--sub); font-weight:500; text-align:left; padding:10px 8px;
  border-bottom:1px solid var(--line); font-size:11px; letter-spacing:.6px;
  text-transform:uppercase; cursor:pointer; user-select:none;
  font-family:"JetBrains Mono", monospace; background:var(--panel2); }
th:hover { color:var(--oil); }
td { padding:9px 8px; border-bottom:1px solid var(--line); }
tr:hover td { background:rgba(255,255,255,.02); }
.bar-cell { position:relative; min-width:140px; }
.bar { height:14px; background:linear-gradient(90deg,var(--oil),#d97706); border-radius:2px;
  display:inline-block; vertical-align:middle; }
.bar-num { font-family:"JetBrains Mono", monospace; font-size:12px; color:var(--text); margin-left:8px; }
.chip { display:inline-block; padding:2px 8px; border-radius:3px; font-size:11px;
  font-family:"JetBrains Mono", monospace; margin:2px 3px 2px 0; letter-spacing:.4px; }
.chip.S1 { background:rgba(52,211,153,.15); color:var(--mint); }
.chip.S2 { background:rgba(6,182,212,.15);  color:var(--water); }
.chip.S3 { background:rgba(245,158,11,.15); color:var(--oil); }
.chip.S4 { background:rgba(220,38,38,.15);  color:var(--bad); }
.chip.S5 { background:rgba(8,145,178,.15);  color:var(--teal); }
.chip.C1 { background:rgba(30,58,95,.5);    color:#93c5fd; }
.chip.C2 { background:rgba(15,23,42,.7);    color:#cbd5e1; }
.chip.C3 { background:rgba(245,158,11,.2);  color:var(--oil); }
.chip.conf-H  { background:rgba(22,163,74,.2);  color:var(--ok); }
.chip.conf-MH { background:rgba(8,145,178,.2);  color:var(--teal); }
.chip.conf-M  { background:rgba(245,158,11,.2); color:var(--oil); }
.opp-card { background:var(--panel2); border:1px solid var(--line); border-radius:6px;
  margin-bottom:12px; overflow:hidden; }
.opp-head { padding:14px 18px; cursor:pointer; display:flex; align-items:center; gap:14px;
  background:linear-gradient(90deg,var(--panel2),var(--panel)); }
.opp-head:hover { background:var(--panel); }
.opp-head .rank { font-family:"JetBrains Mono", monospace; font-size:20px; color:var(--oil);
  font-weight:700; width:34px; text-align:center; }
.opp-head .id { font-family:"JetBrains Mono", monospace; font-size:12px; color:var(--sub);
  background:rgba(245,158,11,.1); padding:3px 8px; border-radius:3px; }
.opp-head .title { flex:1; font-family:"Fraunces", Georgia, serif; font-size:16px;
  color:var(--text); }
.opp-head .gain { font-family:"JetBrains Mono", monospace; font-size:16px; color:var(--mint);
  font-weight:700; }
.opp-head .arrow { color:var(--sub); transition:transform .2s; }
.opp-card.open .arrow { transform:rotate(90deg); }
.opp-body { display:none; padding:18px 22px; background:var(--panel); border-top:1px solid var(--line); }
.opp-card.open .opp-body { display:block; }
.opp-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:14px; }
.opp-stat { background:var(--bg); border:1px solid var(--line); padding:12px; border-radius:4px; }
.opp-stat .lbl { color:var(--sub); font-size:11px; letter-spacing:.5px;
  font-family:"JetBrains Mono", monospace; text-transform:uppercase; }
.opp-stat .val { font-family:"JetBrains Mono", monospace; color:var(--text);
  font-size:18px; font-weight:600; margin-top:4px; }
.opp-section { margin-top:10px; }
.opp-section h4 { font-family:"JetBrains Mono", monospace; font-size:11px;
  color:var(--oil); letter-spacing:.7px; text-transform:uppercase; margin:0 0 6px 0; }
.opp-section p { margin:0; color:var(--text); font-size:13px; line-height:1.55; }
.opp-section .prereq { color:var(--sub); font-style:italic; }
.gain-range { background:var(--bg); height:18px; border-radius:2px; position:relative;
  border:1px solid var(--line); margin-top:8px; }
.gain-range .fill {
  position:absolute; height:100%;
  background:linear-gradient(90deg,rgba(52,211,153,.3),var(--mint));
  border-radius:2px; }
.gain-range .full {
  position:absolute; height:100%;
  background:repeating-linear-gradient(45deg,
    rgba(245,158,11,.1) 0 6px, rgba(245,158,11,.25) 6px 12px);
  border-radius:2px;
  border-left:1px dashed var(--oil); border-right:1px dashed var(--oil); }
.filter-bar { display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap; align-items:center; }
.filter-bar input, .filter-bar select { background:var(--panel2); color:var(--text);
  border:1px solid var(--line); padding:8px 12px; border-radius:4px; font-family:inherit;
  font-size:13px; }
.filter-bar input { width:240px; }
.filter-bar .lbl { color:var(--sub); font-size:11px; letter-spacing:.5px;
  font-family:"JetBrains Mono", monospace; text-transform:uppercase; }
.wells-table { max-height:600px; overflow:auto; border:1px solid var(--line);
  border-radius:4px; }
.wells-table th { position:sticky; top:0; }
.gap-row { display:flex; gap:14px; padding:14px 18px; background:var(--panel2);
  border-radius:6px; margin-bottom:10px; align-items:flex-start;
  border-left:3px solid var(--oil); }
.gap-row .num { font-family:"JetBrains Mono", monospace; font-size:20px; color:var(--oil);
  font-weight:700; width:34px; }
.gap-row .body h4 { margin:0 0 4px 0; color:var(--text); font-size:14px; font-weight:600; }
.gap-row .body p { margin:0; color:var(--sub); font-size:12px; }
.canvas-wrap { position:relative; height:340px; }
.canvas-wrap.tall { height:480px; }
.sankey-svg { width:100%; height:520px; background:var(--bg); border:1px solid var(--line);
  border-radius:4px; }
.legend { display:flex; gap:14px; margin-top:10px; flex-wrap:wrap; font-size:11px;
  color:var(--sub); font-family:"JetBrains Mono", monospace; }
.legend .dot { display:inline-block; width:10px; height:10px; border-radius:2px;
  margin-right:5px; vertical-align:middle; }
.caveat { background:rgba(245,158,11,.08); border-left:3px solid var(--oil);
  padding:10px 14px; margin:10px 0; font-size:12px; color:var(--text); border-radius:3px; }
.caveat b { color:var(--oil); font-family:"JetBrains Mono", monospace; font-size:11px;
  letter-spacing:.5px; text-transform:uppercase; }
footer { padding:20px 28px; border-top:1px solid var(--line); color:var(--dim);
  font-size:11px; font-family:"JetBrains Mono", monospace; margin-top:30px;
  text-align:center; letter-spacing:.5px; }
</style>
</head>
<body>
<header>
  <h1>Shah Field De-Bottlenecking Dashboard <span style="color:var(--oil);font-family:'JetBrains Mono',monospace;font-size:13px;margin-left:10px;">PC26 · OBJ 1.1D</span></h1>
  <div class="sub">TotalEnergies ALSG × ADNOC Onshore  ·  Issued 2026-04-23  ·  Asset Lead FP: Andrey Semenov  ·  124 producer strings + 9 WI strings</div>
</header>
<nav>
  <button class="active" data-tab="overview">Overview</button>
  <button data-tab="map">Bottleneck Map</button>
  <button data-tab="opps">Opportunities</button>
  <button data-tab="wells">Wells</button>
  <button data-tab="gaps">Data Gaps</button>
</nav>
<main>

<!-- ============== OVERVIEW ============== -->
<section id="overview" class="tab active">
  <div class="kpis">
    <div class="kpi"><div class="lbl">Current actual (FAR)</div><div class="val">75,733<span class="unit">BOPD</span></div></div>
    <div class="kpi teal"><div class="lbl">2026 realistic uplift</div><div class="val">10–12k<span class="unit">BOPD</span></div></div>
    <div class="kpi mint"><div class="lbl">De-bottlenecking opps.</div><div class="val">8</div></div>
    <div class="kpi bad"><div class="lbl">Critical data gaps</div><div class="val">9</div></div>
  </div>

  <div class="grid two">
    <div class="card">
      <h2>Field Baseline <span class="tag">Q2-2026 Allowable</span></h2>
      <div class="canvas-wrap"><canvas id="cBaseline"></canvas></div>
      <p class="note">Allowable 76,671 BOPD active · TR 79,983 BOPD · FAR 75,733 BOPD · Gap vs TR = 4,250 BOPD (5.6 %)</p>
    </div>
    <div class="card">
      <h2>Bottleneck Categories <span class="tag">RM-comment classified</span></h2>
      <table id="bnTable">
        <thead><tr><th>ID</th><th>Category</th><th>Type</th><th>Wells</th><th>BOPD lost</th><th>Link</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>8 De-Bottlenecking Opportunities — ranked by 2026 realistic gain <span class="tag">low end of range</span></h2>
    <div class="canvas-wrap tall"><canvas id="cOpps"></canvas></div>
    <div class="legend">
      <span><span class="dot" style="background:var(--mint)"></span>2026 realistic gain (low)</span>
      <span><span class="dot" style="background:rgba(245,158,11,.4)"></span>Uplift to full potential</span>
    </div>
  </div>

  <div class="caveat"><b>Note</b> &nbsp;§4.7 Surface back-pressure estimates pending Jan-2026 FCT report. All gain ranges reproduce the §ANALYSIS BLOCK quantification; per-well classification (Wells tab) is a fresh regex pass on the RM comment column for audit.</div>
</section>

<!-- ============== BOTTLENECK MAP ============== -->
<section id="map" class="tab">
  <div class="card">
    <h2>Production Flow Map <span class="tag">75,733 → 87,000 BOPD potential</span></h2>
    <svg id="sankey" class="sankey-svg" viewBox="0 0 1200 520" preserveAspectRatio="xMidYMid meet"></svg>
    <p class="note">Left band: current production. Wedges show each opportunity's 2026 realistic gain contribution (overlap deduction applied to §4.1/§4.3/§4.4 = ×0.75). Right band: post-debottleneck envelope.</p>
  </div>

  <div class="grid two">
    <div class="card">
      <h2>BOPD lost by bottleneck category</h2>
      <div class="canvas-wrap"><canvas id="cBnLoss"></canvas></div>
    </div>
    <div class="card">
      <h2>Wells affected by category</h2>
      <div class="canvas-wrap"><canvas id="cBnCount"></canvas></div>
    </div>
  </div>
</section>

<!-- ============== OPPORTUNITIES ============== -->
<section id="opps" class="tab">
  <div class="card">
    <h2>Opportunity Deep-Dives <span class="tag">click to expand</span></h2>
    <div id="oppList"></div>
  </div>
</section>

<!-- ============== WELLS ============== -->
<section id="wells" class="tab">
  <div class="card">
    <h2>All Producer Strings <span class="tag">124 strings · regex-tagged from RM comments</span></h2>
    <div class="filter-bar">
      <span class="lbl">Filter:</span>
      <input id="wellSearch" type="text" placeholder="CMPL / UWI / reservoir / RM text...">
      <span class="lbl">Category:</span>
      <select id="catFilter">
        <option value="">All categories</option>
        <option value="S1">S1 — Low PIP / stim</option>
        <option value="S2">S2 — High water cut</option>
        <option value="S3">S3 — Low BHFP / Pb risk</option>
        <option value="S4">S4 — Inactive</option>
        <option value="S5">S5 — Reservoir depletion</option>
        <option value="C1">C1 — Low DP / VSD</option>
        <option value="C2">C2 — ESP max freq</option>
        <option value="C3">C3 — Back-pressure proxy</option>
      </select>
      <span class="lbl">Reservoir:</span>
      <select id="resFilter">
        <option value="">All</option>
        <option value="SIMSIMA R1">R1</option>
        <option value="SIMSIMA R2">R2</option>
        <option value="SIMSIMA R3">R3</option>
      </select>
      <span style="margin-left:auto;color:var(--sub);font-size:12px;font-family:'JetBrains Mono',monospace;"
        id="wellCount"></span>
    </div>
    <div class="wells-table">
      <table id="wTable">
        <thead><tr>
          <th data-sort="cmpl">CMPL</th>
          <th data-sort="res">Reservoir</th>
          <th data-sort="alw">Alw</th>
          <th data-sort="tr">TR</th>
          <th data-sort="qo">Qo</th>
          <th data-sort="wc">WC%</th>
          <th data-sort="pi">PI</th>
          <th data-sort="bhfp">BHFP</th>
          <th data-sort="freq">Freq</th>
          <th data-sort="inact">Inact</th>
          <th>Cats</th>
          <th>RM Comment</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>Water-Injection Strings <span class="tag">9 WI wells</span></h2>
    <table id="wiTable">
      <thead><tr><th>Well</th><th>Reservoir</th><th>Alw w/ 175+180</th><th>Max w/o</th><th>TR</th><th>Actual</th><th>WHIP</th><th>RM</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</section>

<!-- ============== DATA GAPS ============== -->
<section id="gaps" class="tab">
  <div class="card">
    <h2>Critical Data Gaps <span class="tag">ranked by impact-on-deliverable</span></h2>
    <div id="gapList"></div>
  </div>
  <div class="caveat"><b>Request</b> &nbsp;Items 1 and 2 (Jan-2026 FCT report and GAP/Prosper IPM model) are the single most consequential — without them, surface bottleneck quantification (§4.7) cannot move past estimate and remains the largest tractable upside.</div>
</section>

</main>

<footer>
PC26 — Objective 1.1D — Shah Field De-Bottlenecking · Built __DATE__ ·
Chart.js 4.4.0 · IBM Plex Sans / Fraunces / JetBrains Mono · Single-file offline build
</footer>

<script>
const WELLS = __WELLS__;
const WI    = __WI__;
const BN    = __BN__;
const OPPS  = __OPPS__;
const GAPS  = __GAPS__;

Chart.defaults.color = '#8b94a3';
Chart.defaults.borderColor = '#1f242e';
Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";

// ----- Tabs -----
document.querySelectorAll('nav button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('nav button').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    document.getElementById(b.dataset.tab).classList.add('active');
  });
});

// ----- Baseline chart -----
new Chart(document.getElementById('cBaseline'), {
  type:'bar',
  data:{
    labels:['Actual (FAR)','Allowable','TR','Allow w/ Inactive','Ceiling'],
    datasets:[{
      data:[75733,76671,79983,80591,102752],
      backgroundColor:['#f59e0b','#0891b2','#34d399','#06b6d4','#0a2540'],
      borderRadius:3
    }]
  },
  options:{
    indexAxis:'y',
    plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c => c.raw.toLocaleString()+' BOPD'}}},
    scales:{x:{ticks:{callback:v => (v/1000).toFixed(0)+'k'}, grid:{color:'#1f242e'}},
            y:{grid:{display:false}}},
    maintainAspectRatio:false
  }
});

// ----- Bottleneck table -----
const bnTbody = document.querySelector('#bnTable tbody');
const maxBopd = Math.max(...BN.filter(b => b.bopd).map(b => b.bopd));
BN.forEach(b => {
  const tr = document.createElement('tr');
  const barW = b.bopd ? (b.bopd / maxBopd * 100).toFixed(0) : 0;
  tr.innerHTML = `
    <td><b style="color:var(--oil);font-family:'JetBrains Mono',monospace;">${b.id}</b></td>
    <td>${b.label}</td>
    <td><span class="chip ${b.type === 'Subsurface' ? 'S5' : b.type === 'Surface' ? 'C3' : b.type === 'Completion' ? 'C1' : 'S2'}">${b.type}</span></td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${b.wells ?? '—'}</td>
    <td class="bar-cell">${b.bopd ? `<span class="bar" style="width:${barW}%"></span><span class="bar-num">${b.bopd.toLocaleString()}</span>` : '<span style="color:var(--dim);font-family:\\'JetBrains Mono\\',monospace;">TBD</span>'}</td>
    <td style="color:var(--teal);font-family:'JetBrains Mono',monospace;font-size:12px;">${b.link}</td>`;
  bnTbody.appendChild(tr);
});

// ----- Opportunities ranking chart -----
const oppsSorted = [...OPPS].sort((a,b) => (b.low+b.high)/2 - (a.low+a.high)/2);
new Chart(document.getElementById('cOpps'), {
  type:'bar',
  data:{
    labels:oppsSorted.map(o => `§${o.id}  ${o.title.length>40 ? o.title.slice(0,40)+'…' : o.title}`),
    datasets:[
      {label:'2026 realistic (low)', data:oppsSorted.map(o => o.low),
        backgroundColor:'#34d399', stack:'g', borderRadius:2},
      {label:'Uplift to high', data:oppsSorted.map(o => o.high - o.low),
        backgroundColor:'#0891b2', stack:'g', borderRadius:2},
      {label:'Headroom to full potential', data:oppsSorted.map(o => o.full_high - o.high),
        backgroundColor:'rgba(245,158,11,.4)', stack:'g', borderRadius:2}
    ]
  },
  options:{
    indexAxis:'y',
    plugins:{legend:{position:'bottom', labels:{usePointStyle:true, padding:14}},
      tooltip:{callbacks:{label:c => c.dataset.label+': '+c.raw.toLocaleString()+' BOPD'}}},
    scales:{x:{stacked:true, ticks:{callback:v => (v/1000).toFixed(1)+'k'}, grid:{color:'#1f242e'}},
            y:{stacked:true, grid:{display:false}}},
    maintainAspectRatio:false
  }
});

// ----- Bottleneck Map (custom SVG) -----
function buildSankey() {
  const svg = document.getElementById('sankey');
  const W = 1200, H = 520;
  const leftX = 60, midX = 580, rightX = 1080;
  const trunkW = 36;
  const startTotal = 75733;
  // Build wedges - 2026 realistic low with overlap deduction on 4.1, 4.3, 4.4
  const overlap = new Set(['4.1','4.3','4.4']);
  const wedges = OPPS.map(o => ({
    id: o.id, label: o.title,
    val: overlap.has(o.id) ? Math.round(o.low * 0.75) : o.low,
    raw: o.low
  })).sort((a,b) => b.val - a.val);
  const totalGain = wedges.reduce((s,w) => s + w.val, 0);
  const endTotal = startTotal + totalGain;
  const colors = {
    '4.5':'#0891b2','4.7':'#f59e0b','4.6':'#06b6d4','4.1':'#34d399',
    '4.3':'#1e3a5f','4.4':'#0f172a','4.2':'#f59e0b','4.8':'#16a34a'
  };

  // Left rectangle - starting production
  let html = '';
  const leftH = 380, leftY = 70;
  html += `<rect x="${leftX}" y="${leftY}" width="${trunkW}" height="${leftH}" fill="#f59e0b" rx="3"/>`;
  html += `<text x="${leftX+trunkW/2}" y="${leftY-12}" fill="#f59e0b" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="13">FAR</text>`;
  html += `<text x="${leftX+trunkW/2}" y="${leftY+leftH+22}" fill="#e8eaee" text-anchor="middle" font-family="JetBrains Mono" font-size="14" font-weight="700">${startTotal.toLocaleString()}</text>`;
  html += `<text x="${leftX+trunkW/2}" y="${leftY+leftH+38}" fill="#8b94a3" text-anchor="middle" font-family="JetBrains Mono" font-size="11">BOPD</text>`;

  // Right rectangle - end total
  const rightH = leftH * (endTotal / startTotal * 0.95);
  const rightY = leftY - (rightH - leftH);
  html += `<rect x="${rightX}" y="${rightY}" width="${trunkW}" height="${rightH}" fill="#34d399" rx="3" opacity="0.9"/>`;
  html += `<text x="${rightX+trunkW/2}" y="${rightY-12}" fill="#34d399" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="13">2026 TARGET</text>`;
  html += `<text x="${rightX+trunkW/2}" y="${rightY+rightH+22}" fill="#e8eaee" text-anchor="middle" font-family="JetBrains Mono" font-size="14" font-weight="700">${endTotal.toLocaleString()}</text>`;
  html += `<text x="${rightX+trunkW/2}" y="${rightY+rightH+38}" fill="#8b94a3" text-anchor="middle" font-family="JetBrains Mono" font-size="11">BOPD</text>`;

  // Flow from FAR -> midpoint
  const flowPath = `M${leftX+trunkW} ${leftY} C${midX-200} ${leftY}, ${midX-200} ${leftY+leftH}, ${midX} ${leftY+leftH/2 + leftH/2}
                    L${midX} ${leftY+leftH/2 - leftH/2}
                    C${midX-200} ${leftY+leftH}, ${midX-200} ${leftY}, ${leftX+trunkW} ${leftY} Z`;
  // Simpler: rounded rect from left to midpoint as base
  html += `<path d="M ${leftX+trunkW} ${leftY} L ${midX} ${leftY+30} L ${midX} ${leftY+leftH-30} L ${leftX+trunkW} ${leftY+leftH} Z" fill="rgba(245,158,11,.15)"/>`;

  // Wedges from midpoint to right band - stack vertically aligned to right rect
  let acc = 0;
  const wedgeAreaTop = rightY + rightH - leftH;  // base existing flow at bottom
  wedges.forEach((w,i) => {
    const wh = (w.val / endTotal) * rightH;
    const wy0 = rightY + (acc) ;
    // Mid-column rectangle (wedge label band)
    const midY = leftY + 30 + i * 42;
    const color = colors[w.id] || '#0891b2';
    // Wedge label box
    html += `<rect x="${midX}" y="${midY}" width="380" height="34" fill="${color}" opacity="0.18" rx="3" stroke="${color}" stroke-width="1"/>`;
    html += `<text x="${midX+10}" y="${midY+15}" fill="${color}" font-family="JetBrains Mono" font-size="11" font-weight="700">§${w.id}</text>`;
    html += `<text x="${midX+50}" y="${midY+15}" fill="#e8eaee" font-family="IBM Plex Sans" font-size="12">${w.label.slice(0,42)}${w.label.length>42?'…':''}</text>`;
    html += `<text x="${midX+10}" y="${midY+28}" fill="${color}" font-family="JetBrains Mono" font-size="11" font-weight="700">+${w.val.toLocaleString()} BOPD</text>`;
    // Flow from wedge box to right rect (top of right column for first wedge)
    const fy = midY + 17;
    const ty = wy0 + wh/2;
    html += `<path d="M ${midX+380} ${fy} Q ${midX+500} ${fy}, ${rightX-30} ${ty} L ${rightX} ${ty}" stroke="${color}" stroke-width="2" fill="none" opacity="0.5"/>`;
    acc += wh;
  });

  // Add "from FAR" bar continuation at right
  html += `<rect x="${rightX-15}" y="${rightY+rightH-leftH*(startTotal/endTotal)}" width="0" height="0" fill="${'#f59e0b'}"/>`;

  // Bottom legend annotation
  html += `<text x="60" y="490" fill="#8b94a3" font-family="JetBrains Mono" font-size="11">Gain bridge — width of each row encodes 2026 realistic BOPD contribution (low end). §4.1/§4.3/§4.4 deflated ×0.75 for overlap.</text>`;
  svg.innerHTML = html;
}
buildSankey();

// ----- BN charts -----
const bnLossData = BN.filter(b => b.bopd);
new Chart(document.getElementById('cBnLoss'), {
  type:'bar',
  data:{labels:bnLossData.map(b => b.id), datasets:[{
    data:bnLossData.map(b => b.bopd),
    backgroundColor:bnLossData.map(b =>
      b.type==='Subsurface' ? '#0891b2' :
      b.type==='Surface'    ? '#f59e0b' :
      b.type==='Completion' ? '#1e3a5f' : '#06b6d4'),
    borderRadius:3
  }]},
  options:{
    plugins:{legend:{display:false}, tooltip:{callbacks:{label:c => bnLossData[c.dataIndex].label+': '+c.raw.toLocaleString()+' BOPD'}}},
    scales:{y:{ticks:{callback:v => (v/1000)+'k'}, grid:{color:'#1f242e'}},
            x:{grid:{display:false}}},
    maintainAspectRatio:false
  }
});
const bnCountData = BN.filter(b => b.wells);
new Chart(document.getElementById('cBnCount'), {
  type:'bar',
  data:{labels:bnCountData.map(b => b.id), datasets:[{
    data:bnCountData.map(b => b.wells),
    backgroundColor:bnCountData.map(b =>
      b.type==='Subsurface' ? '#0891b2' :
      b.type==='Surface'    ? '#f59e0b' :
      b.type==='Completion' ? '#1e3a5f' : '#06b6d4'),
    borderRadius:3
  }]},
  options:{
    plugins:{legend:{display:false},tooltip:{callbacks:{label:c => bnCountData[c.dataIndex].label+': '+c.raw+' wells'}}},
    scales:{y:{grid:{color:'#1f242e'}},x:{grid:{display:false}}},
    maintainAspectRatio:false
  }
});

// ----- Opportunity accordion -----
const oppList = document.getElementById('oppList');
oppsSorted.forEach((o, idx) => {
  const confClass = o.conf === 'High' ? 'conf-H' : o.conf === 'Med-High' ? 'conf-MH' : 'conf-M';
  const capexMid = (o.capex_low + o.capex_high) / 2;
  const gainMid = (o.low + o.high) / 2;
  const usdPerBopd = Math.round(capexMid * 1e6 / gainMid).toLocaleString();
  const maxPotential = 6000;
  const lowPct = (o.low / maxPotential * 100).toFixed(0);
  const widthPct = ((o.high - o.low) / maxPotential * 100).toFixed(0);
  const fullPct = ((o.full_high - o.high) / maxPotential * 100).toFixed(0);
  const card = document.createElement('div');
  card.className = 'opp-card' + (idx === 0 ? ' open' : '');
  card.innerHTML = `
    <div class="opp-head">
      <div class="rank">${idx+1}</div>
      <span class="id">§${o.id}</span>
      <div class="title">${o.title}</div>
      <div class="gain">+${o.low.toLocaleString()}${o.high!==o.low?'–'+o.high.toLocaleString():''} BOPD</div>
      <div class="arrow">▶</div>
    </div>
    <div class="opp-body">
      <div class="opp-grid">
        <div class="opp-stat"><div class="lbl">2026 Realistic</div><div class="val">${o.low.toLocaleString()}${o.high!==o.low?'–'+o.high.toLocaleString():''} <span style="font-size:12px;color:var(--sub);">BOPD</span></div></div>
        <div class="opp-stat"><div class="lbl">Full Potential</div><div class="val">${o.full_low.toLocaleString()}${o.full_high!==o.full_low?'–'+o.full_high.toLocaleString():''} <span style="font-size:12px;color:var(--sub);">BOPD</span></div></div>
        <div class="opp-stat"><div class="lbl">Capex Bracket</div><div class="val">$${o.capex_low}–${o.capex_high}<span style="font-size:12px;color:var(--sub);"> M</span></div></div>
        <div class="opp-stat"><div class="lbl">$ / BOPD</div><div class="val">$${usdPerBopd}</div></div>
      </div>
      <div class="opp-section">
        <h4>Gain Range</h4>
        <div class="gain-range">
          <div class="full" style="left:${lowPct}%; width:${Math.max(0, parseFloat(widthPct)+parseFloat(fullPct))}%"></div>
          <div class="fill" style="left:${lowPct}%; width:${widthPct||1}%"></div>
        </div>
        <div style="margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--sub);">Solid = 2026 realistic · Striped = headroom to full potential · Scale 0 → 6,000 BOPD</div>
      </div>
      <div class="opp-section">
        <h4>Mechanism</h4>
        <p>${o.mechanism}</p>
      </div>
      <div class="opp-section">
        <h4>Prerequisite</h4>
        <p class="prereq">${o.prereq}</p>
      </div>
      <div class="opp-section">
        <h4>Category &nbsp;·&nbsp; Confidence</h4>
        <p>${o.category} &nbsp;·&nbsp; <span class="chip ${confClass}">${o.conf}</span></p>
      </div>
    </div>`;
  oppList.appendChild(card);
});
document.querySelectorAll('.opp-head').forEach(h => {
  h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
});

// ----- Wells table -----
const wTbody = document.querySelector('#wTable tbody');
let sortKey = null, sortDir = 1;

function renderWells() {
  const q = document.getElementById('wellSearch').value.toLowerCase();
  const cat = document.getElementById('catFilter').value;
  const res = document.getElementById('resFilter').value;
  let rows = WELLS.filter(w => {
    if (q) {
      const blob = (w.cmpl+' '+w.uwi+' '+w.res+' '+(w.rm||'')).toLowerCase();
      if (!blob.includes(q)) return false;
    }
    if (cat && !(w.cats || []).includes(cat)) return false;
    if (res && w.res !== res) return false;
    return true;
  });
  if (sortKey) {
    rows.sort((a,b) => {
      const va = a[sortKey], vb = b[sortKey];
      if (va == null) return 1; if (vb == null) return -1;
      if (typeof va === 'number') return (va - vb) * sortDir;
      return String(va).localeCompare(String(vb)) * sortDir;
    });
  }
  wTbody.innerHTML = rows.map(w => `
    <tr>
      <td><b style="font-family:'JetBrains Mono',monospace;font-size:12px;">${w.cmpl}</b></td>
      <td style="color:var(--sub);font-size:12px;">${w.res || '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.alw ?? '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.tr ?? '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.qo != null ? w.qo.toFixed(0) : '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;${w.wc>=85?'color:var(--bad)':w.wc>=60?'color:var(--oil)':''}">${w.wc != null ? w.wc.toFixed(1) : '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.pi != null ? w.pi.toFixed(2) : '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.bhfp ?? '—'}</td>
      <td style="text-align:right;font-family:'JetBrains Mono',monospace;${w.freq>=58?'color:var(--oil)':''}">${w.freq ?? '—'}</td>
      <td>${w.inact === 'Y' ? '<span class="chip S4">Y</span>' : '—'}</td>
      <td>${(w.cats||[]).map(c => `<span class="chip ${c}">${c}</span>`).join('')}</td>
      <td style="color:var(--sub);font-size:11px;max-width:340px;">${w.rm || ''}</td>
    </tr>`).join('');
  document.getElementById('wellCount').textContent = `Showing ${rows.length} of ${WELLS.length}`;
}

document.querySelectorAll('#wTable th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const k = th.dataset.sort;
    if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = 1; }
    renderWells();
  });
});
document.getElementById('wellSearch').addEventListener('input', renderWells);
document.getElementById('catFilter').addEventListener('change', renderWells);
document.getElementById('resFilter').addEventListener('change', renderWells);
renderWells();

// ----- WI table -----
document.querySelector('#wiTable tbody').innerHTML = WI.map(w => `
  <tr>
    <td><b style="font-family:'JetBrains Mono',monospace;">${w.well}</b></td>
    <td><span class="chip ${w.res === 'R1' ? 'S5' : 'S2'}">${w.res || '—'}</span></td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.alw ?? '—'}</td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.max_wo ?? '—'}</td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.tr ?? '—'}</td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.actual ?? '—'}</td>
    <td style="text-align:right;font-family:'JetBrains Mono',monospace;">${w.whip ?? '—'}</td>
    <td style="color:var(--sub);font-size:11px;max-width:380px;">${w.rm || ''}</td>
  </tr>`).join('');

// ----- Data Gaps -----
const gapList = document.getElementById('gapList');
GAPS.forEach((g, i) => {
  const row = document.createElement('div');
  row.className = 'gap-row';
  row.innerHTML = `
    <div class="num">${String(i+1).padStart(2,'0')}</div>
    <div class="body">
      <h4>${g[0]}</h4>
      <p>${g[1]}</p>
    </div>`;
  gapList.appendChild(row);
});
</script>
</body>
</html>
"""

from datetime import date
html = (html
        .replace("__WELLS__", WELLS_JSON_INLINE)
        .replace("__WI__",    WI_JSON_INLINE)
        .replace("__BN__",    BOTTLENECKS_JSON)
        .replace("__OPPS__",  OPPS_JSON)
        .replace("__GAPS__",  GAPS_JSON)
        .replace("__DATE__",  date.today().isoformat()))

OUT.write_text(html)
print(f"Wrote: {OUT}  ({OUT.stat().st_size:,} bytes)")
