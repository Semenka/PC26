"""
PC26 Obj 1.1D — Shah Field De-Bottlenecking Opportunities Workbook

Generates a multi-sheet xlsx with:
  - Cover & Executive Summary
  - Field-Level Baseline (with bar chart)
  - Bottleneck Map (categories S1-S5, C1-C3, W1-W4)
  - 8 Opportunity sheets (one per §4.x), each with quantification table
  - Consolidated Ranking (with horizontal bar chart of gains)
  - Gain Bridge (waterfall data + native Excel column chart)
  - Capex vs Gain matrix (scatter chart)
  - Data Gaps register
  - Per-well bottleneck inventory tagged to categories
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, BarChart3D, LineChart, ScatterChart, Reference, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.utils import get_column_letter

OUT = "PC26_1.1D_Debottlenecking_Opportunities.xlsx"

# ============ STYLE PALETTE (Ocean Gradient — navy + oil-amber, no cream) ============
NAVY     = "0A2540"
DEEP     = "1E3A5F"
TEAL     = "0891B2"
MINT     = "34D399"
OIL      = "F59E0B"
WATER    = "06B6D4"
BAD      = "DC2626"
WARN     = "F59E0B"
GOOD     = "16A34A"
CREAM    = "FFFFFF"
LIGHT    = "F8FAFC"
LINE_GRY = "CBD5E1"
INK      = "0F172A"
DIM      = "64748B"

WHITE_BOLD = Font(name="Arial", color="FFFFFF", bold=True, size=11)
WHITE_BIG  = Font(name="Arial", color="FFFFFF", bold=True, size=14)
BIG_TITLE  = Font(name="Georgia", bold=True, size=20, color=NAVY)
SECT_TITLE = Font(name="Georgia", bold=True, size=14, color=NAVY)
BOLD       = Font(name="Arial", bold=True, size=10)
NORM       = Font(name="Arial", size=10)
SMALL      = Font(name="Arial", size=9)
ITAL       = Font(name="Arial", italic=True, size=10, color=DIM)

NAVY_FILL  = PatternFill("solid", start_color=NAVY)
DEEP_FILL  = PatternFill("solid", start_color=DEEP)
TEAL_FILL  = PatternFill("solid", start_color=TEAL)
OIL_FILL   = PatternFill("solid", start_color=OIL)
GOOD_FILL  = PatternFill("solid", start_color=GOOD)
BAD_FILL   = PatternFill("solid", start_color=BAD)
WARN_FILL  = PatternFill("solid", start_color=WARN)
LIGHT_FILL = PatternFill("solid", start_color=LIGHT)
ALT_FILL   = PatternFill("solid", start_color="F1F5F9")

THIN  = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

CTR  = Alignment(horizontal="center", vertical="center", wrap_text=True)
LFT  = Alignment(horizontal="left",   vertical="center", wrap_text=True)
RGT  = Alignment(horizontal="right",  vertical="center")

# ============ DATA ============
OPPORTUNITIES = [
    # (id, title, category, gain_2026_low, gain_2026_high, gain_full_low, gain_full_high,
    #  conf, capex_low_musd, capex_high_musd, mechanism, prereq, color)
    ("4.5", "WI capacity uplift (SY-175 + SY-180 + cluster review)", "Subsurface / WI",
     2500, 4000, 4000, 5500, "Med-High", 2.0, 28.0,
     "Phase 1: complete WO on SY-175 & SY-180 to recover 16,000 bwpd stranded capacity. "
     "Phase 2 (2027): Cluster #2 capacity uplift study based on Jan-2026 FCT. "
     "Phase 3: new WI well drilling if VRR confirms additional voidage to fill. "
     "Sector pressure recovery lifts Qo across ~30 R1/R2 producers. Saih Rawl analog (SPE 68222): "
     "~12 % oil rate uplift per 30 % WI rate increase at mature waterflood stage.",
     "Cluster #2 / SY-148 WS FCT (RM-mandated before SY-180 commissioning); G2V2 ML#5 forecast",
     TEAL),
    ("4.7", "Surface back-pressure optimization", "Surface",
     1500, 2500, 2300, 3300, "Medium", 0.2, 8.0,
     "Phase 1: Station header pressure setpoint review (CDS / RDS-1 / RDS-2). Each 10 psi "
     "separator pressure reduction across 80 R1 producers ≈ +800 BOPD. "
     "Phase 2: Selective flowline looping on 2-3 worst segments (>200 psi/km ΔP). "
     "Phase 3: Choke-on-test vs production-choke alignment.",
     "January-2026 FCT report; GAP/Prosper IPM model; WHIP/WHFP-vs-time per well",
     OIL),
    ("4.6", "Produced-water redistribution + R1↔R2 rebalancing", "Subsurface / WI",
     2000, 2400, 2400, 3200, "Medium", 0.5, 1.5,
     "(a) Tracer + integrity diagnosis on 139-SS and 145-SS (RM flagged R1→R2 water loss). "
     "(b) Rebalance injection: redirect 3,000-5,000 bwpd from R2 to R1. "
     "(c) Selective shut-in / rate reduction on 6 worst high-WC producers (>85 % WC) "
     "to free PW capacity and improve sector VRR efficiency.",
     "PW lab analysis (TDS, scaling, particulates, H₂S); injector PLT/CBL on 139-SS, 145-SS",
     WATER),
    ("4.1", "Stimulation roll-out beyond Obj 1.1C", "Subsurface",
     2500, 2500, 5000, 6000, "Medium", 8.0, 12.0,
     "32+ R1 strings flagged 'Low intake / Low PIP / stim required' by RM. Obj 1.1C covers 5. "
     "Apply Naphtha+HCl recipe to 8-10 additional wells per year. Target wells with PI degradation "
     "D > 30 %/yr (1.1C methodology). Average gain +150 to +400 BOPD per well, declining 30 %/yr.",
     "Per-well PI screening across 32 stim candidates (extension of 1.1C dashboard)",
     MINT),
    ("4.3", "VSD / PWS retrofit campaign", "Surface / Completion",
     1600, 1600, 3300, 5500, "High", 2.4, 4.8,
     "22 strings flagged 'Low DP across choke / VSD required' — ESP-limited not reservoir-limited. "
     "Replace fixed-speed power with PWS-VSD; allows running at 55-60 Hz to push past choke-DP-limited "
     "operating point. Already proven on 10 Shah wells (SY-012, 019, 026, 035, 039, 097).",
     "Power-system loading review (does Shah electrical infra support 8 more VSDs?)",
     DEEP),
    ("4.4", "ESP upsize where pump at max frequency", "Completion",
     800, 800, 2800, 2800, "Medium", 2.0, 3.2,
     "14 strings already at 55-60 Hz with no headroom (SY-073, 088, 094, 099, 100, 113). "
     "During next workover install pump from one tier higher in catalog (TE3300 → TE5000, "
     "GN3200 → GN4000). Combine with VSD where not already present.",
     "Per-well ESP design review; align with existing WO schedule",
     INK),
    ("4.2", "BHFP rate-cap relaxation via skin reduction / PVT relocalization", "Subsurface",
     900, 900, 1800, 1800, "Med-High", 0.2, 0.5,
     "12 strings explicitly capped at low rate to keep BHFP ≥ Pb+100 (SY-040, 058, 064, 085, 120, "
     "132, 135, 014). Two paths: (a) skin reduction via stimulation reduces drawdown for same Qo; "
     "(b) per-well revisit of Pb assumption — for some R1 wells, local Pb may be lower than 392 psi.",
     "GAP/Prosper IPM model; PVT relocalization study",
     WARN),
    ("4.8", "Inactive-string reactivation acceleration", "Cross-cut Obj 1.1B",
     1000, 1000, 3920, 3920, "High", 0.5, 1.0,
     "14 inactive strings totaling 3,920 BOPD allowable (SY-035 PWS, SY-097 tie-in, SY-098 downsize, "
     "SY-115/117 ESP repl, SY-093 SAP-B fix). Speed of execution is the lever — every quarter of "
     "acceleration ≈ +1,000 BOPD avg uplift over the year.",
     "Coordination with Obj 1.1B inactive-string KPI track",
     GOOD),
]

BOTTLENECK_MAP = [
    # (id, category, indicator, wells_affected, bopd_lost, opportunity_link, type)
    ("S1", "Low PIP / low intake — stim candidates", '"Low intake", "Low PIP", "stim required"', 32, 12000, "§4.1", "Subsurface"),
    ("S2", "High watercut (>60 %) — water management", '"High water cut", "wc increase", WC>60 %', 38, 7000, "§4.6 + Obj 1.2A", "Subsurface"),
    ("S3", "Low BHFP — close to Pb violation", '"Limit production to get pwf above Pb", BHFP<500 psi', 12, 1800, "§4.2", "Subsurface"),
    ("S4", "Inactive strings — workover backlog", "Inactive Y / Disconnected", 14, 3920, "§4.8 + Obj 1.1B", "Subsurface"),
    ("S5", "Reservoir pressure depletion", 'Pres declining; SY-024: "improve sector VRR"', 8, 5000, "§4.5", "Subsurface"),
    ("C1", "Low DP across choke — VSD required", '"Low DP across choke", "VSD required", choke fully open', 22, 6500, "§4.3", "Surface/Completion"),
    ("C2", "ESP at max frequency", '"ESP running at max frequency", "freq 60 Hz"', 14, 3500, "§4.4", "Completion"),
    ("C3", "High back-pressure on flowline / station", "Wells with WHFT high & low Qo at full choke", None, None, "§4.7", "Surface"),
    ("W1", "Cluster capacity ceiling 26 Mbwpd", '"respecting max cluster capacity (25/26 Mbwpd each)"', None, None, "§4.5 Phase 2", "Water Injection"),
    ("W2", "WI well integrity (SY-175, SY-180)", '"WO for integrity & accessibility correction"', 2, None, "§4.5 Phase 1", "Water Injection"),
    ("W3", "R1↔R2 inter-reservoir water loss", '"Water loss to R2 likely occurring"', 2, None, "§4.6 (a)", "Water Injection"),
    ("W4", "High-WC producers loading PW system", '"propose to reduce it to improve sector VRR"', 12, None, "§4.6 (c)", "Water Injection"),
]

DATA_GAPS = [
    (1, "January-2026 FCT report",            "Surface bottleneck quantification (§4.7) cannot move past estimate"),
    (2, "GAP/Prosper IPM surface model",      "Needed to run back-pressure sensitivities"),
    (3, "G2V2 reservoir model — ML#5",        "Needed to quantify §4.5 oil response and §4.6 R1/R2 rebalancing"),
    (4, "Cluster #2 / SY-148 WS FCT",         "RM-mandated prerequisite for SY-180 commissioning (§4.5)"),
    (5, "PIDs / PFDs / vendor capacity sheets", "CDS, RDS-1, RDS-2, WI clusters"),
    (6, "Produced water lab analysis",        "TDS, scaling, particulates, H₂S — needed for §4.6 design"),
    (7, "WHIP-vs-time and WHPP-vs-time per well", "Needed to validate flowline-restriction hypothesis (§4.7)"),
    (8, "Injector PLT / CBL logs (139-SS, 145-SS)", "Needed for §4.6 (a) integrity hypothesis"),
    (9, "Per-well PI screening across 32 stim candidates", "Extension of 1.1C methodology to scope §4.1"),
]

# ============ HELPERS ============
def header_row(ws, row, headers, fill=DEEP_FILL, font=WHITE_BOLD):
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=j, value=h)
        c.font = font; c.fill = fill; c.alignment = CTR; c.border = BORDER

def title_band(ws, row, span, text, fill=NAVY_FILL, font=WHITE_BIG):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1, value=text)
    c.font = font; c.fill = fill; c.alignment = LFT
    ws.row_dimensions[row].height = 26

def widths(ws, w):
    for i, x in enumerate(w, start=1):
        ws.column_dimensions[get_column_letter(i)].width = x

# ============ WORKBOOK ============
wb = Workbook()

# ---------- COVER ----------
ws = wb.active; ws.title = "Cover"
ws.merge_cells("A1:H1")
ws["A1"] = "PC26 — Obj 1.1D — Shah Field De-Bottlenecking Opportunities"
ws["A1"].font = BIG_TITLE; ws.row_dimensions[1].height = 30
ws.merge_cells("A2:H2"); ws["A2"] = "Quantified opportunity catalogue — surface & subsurface"
ws["A2"].font = ITAL
ws.merge_cells("A3:H3"); ws["A3"] = "Issued 23-Apr-2026 · TotalEnergies ALSG × ADNOC Onshore"
ws["A3"].font = SMALL

title_band(ws, 5, 8, "WORKBOOK CONTENTS")
contents = [
    ("Cover", "This sheet"),
    ("Exec_Summary", "Headline numbers + ranking + recommended sequencing"),
    ("Field_Baseline", "Allowable / TR / Actual breakdown — with chart"),
    ("Bottleneck_Map", "9 root-cause categories (S1-S5, C1-C3, W1-W4) traced from RM comments"),
    ("Opportunities_Summary", "All 8 opportunities side-by-side with gain ranges + chart"),
    ("Gain_Bridge", "Waterfall from current 75,733 BOPD to 2026-realistic envelope"),
    ("Capex_vs_Gain", "Bubble/scatter view — prioritization matrix"),
    ("Opp_4.1 → Opp_4.8", "One sheet per opportunity with full narrative, mechanism, prereq, gain table"),
    ("Data_Gaps", "Ranked list of data still required for final quantification"),
    ("Field_Totals", "Field-level Allowable/TR/Actual numbers from Q2-2026 Allowable file"),
    ("Workshop_Agenda", "Q3-2026 Technical WS agenda per KoM"),
]
for i, (k, v) in enumerate(contents, start=6):
    ws.cell(row=i, column=1, value=k).font = BOLD
    ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=8)
    ws.cell(row=i, column=2, value=v).font = NORM
    ws.cell(row=i, column=2).alignment = LFT

title_band(ws, 19, 8, "FIELD-LEVEL HEADLINE", fill=DEEP_FILL)
headline = [
    ("Current actual production",          "75,733 BOPD"),
    ("Field Technical Rate (active)",      "79,983 BOPD"),
    ("Gap vs TR",                           "4,250 BOPD (5.6 %)"),
    ("Total deliverability ceiling",       "~102,752 BOPD (incl. inactive)"),
    ("2026 realistic uplift envelope",     "~10,000–12,000 BOPD (+13 %)"),
    ("Full potential envelope",            "~22,000–27,000 BOPD"),
    ("Number of de-bottlenecking opps.",   "8 (5 subsurface + 2 surface + 1 cross-cut)"),
    ("Critical missing data items",        "9 (FCT report + IPM model top of list)"),
]
for i, (k, v) in enumerate(headline, start=20):
    ws.cell(row=i, column=1, value=k).font = BOLD
    ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=4)
    ws.cell(row=i, column=2, value=v).font = NORM
widths(ws, [34] + [16]*7)

# ---------- EXEC_SUMMARY ----------
ws = wb.create_sheet("Exec_Summary")
ws["A1"] = "Executive Summary — Top 8 De-Bottlenecking Opportunities"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 28

title_band(ws, 3, 9, "RANKED BY 2026-REALISTIC GAIN (BOPD)")
header_row(ws, 4, ["Rank", "ID", "Opportunity", "Category", "2026 low", "2026 high", "Full low", "Full high", "Confidence"])

# Sort by midpoint of 2026 range (descending)
ranked = sorted(OPPORTUNITIES, key=lambda x: -(x[3]+x[4])/2)
for i, opp in enumerate(ranked, start=5):
    rank = i - 4
    ws.cell(row=i, column=1, value=rank).font = BOLD
    ws.cell(row=i, column=2, value=opp[0]).font = BOLD
    ws.cell(row=i, column=3, value=opp[1]).font = NORM
    ws.cell(row=i, column=4, value=opp[2]).font = NORM
    ws.cell(row=i, column=5, value=opp[3]).font = NORM
    ws.cell(row=i, column=6, value=opp[4]).font = NORM
    ws.cell(row=i, column=7, value=opp[5]).font = NORM
    ws.cell(row=i, column=8, value=opp[6]).font = NORM
    ws.cell(row=i, column=9, value=opp[7]).font = NORM
    for j in range(1, 10):
        ws.cell(row=i, column=j).border = BORDER
        if i % 2 == 0: ws.cell(row=i, column=j).fill = ALT_FILL
        if j in (5,6,7,8): ws.cell(row=i, column=j).alignment = RGT

# Totals row
tot_row = 5 + len(ranked)
ws.cell(row=tot_row, column=3, value="TOTAL realistic envelope (with 25 % overlap deduction)").font = BOLD
ws.cell(row=tot_row, column=5, value=f"=ROUND(SUM(E5:E{tot_row-1})*0.75,0)").font = BOLD
ws.cell(row=tot_row, column=6, value=f"=ROUND(SUM(F5:F{tot_row-1})*0.75,0)").font = BOLD
ws.cell(row=tot_row, column=7, value=f"=ROUND(SUM(G5:G{tot_row-1})*0.75,0)").font = BOLD
ws.cell(row=tot_row, column=8, value=f"=ROUND(SUM(H5:H{tot_row-1})*0.75,0)").font = BOLD
for j in range(1, 10):
    ws.cell(row=tot_row, column=j).fill = NAVY_FILL
    ws.cell(row=tot_row, column=j).font = WHITE_BOLD

# Bar chart of 2026-low gains
chart = BarChart()
chart.type = "bar"
chart.style = 11
chart.title = "2026 realistic gain potential per opportunity (BOPD, low end)"
chart.y_axis.title = "Opportunity"
chart.x_axis.title = "Gain (BOPD)"
data = Reference(ws, min_col=5, min_row=4, max_row=4+len(ranked), max_col=5)
cats = Reference(ws, min_col=2, min_row=5, max_row=4+len(ranked))
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 12; chart.width = 22
chart.legend = None
ws.add_chart(chart, f"A{tot_row+3}")

widths(ws, [6, 8, 50, 22, 11, 11, 11, 11, 14])

# ---------- FIELD_BASELINE ----------
ws = wb.create_sheet("Field_Baseline")
ws["A1"] = "Field-Level Baseline — Q2-2026 Allowable file"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26

title_band(ws, 3, 5, "OIL PRODUCTION (BOPD)")
header_row(ws, 4, ["Metric", "Active", "Including Inactive", "Comment", ""])
oil_rows = [
    ("Allowable",       76671, 80591, "RM-approved cap"),
    ("Technical Rate (TR)", 79983, 79983, "Engineering deliverability"),
    ("FAR (actual)",    75733, None,  "Field actual rate Q1-2026"),
    ("Gap vs TR",       4250, None,  "Under-delivery 5.6 %"),
    ("Deliverability ceiling", None, 102752, "Sum of estimated max for all R1+R2 strings"),
    ("Inactive strings (booked)", 3920, None, "14 strings — gain via Obj 1.1B/§4.8"),
]
for i, (k, a, b, cmt) in enumerate(oil_rows, start=5):
    ws.cell(row=i, column=1, value=k).font = BOLD
    if a is not None: ws.cell(row=i, column=2, value=a).font = NORM; ws.cell(row=i, column=2).alignment = RGT
    if b is not None: ws.cell(row=i, column=3, value=b).font = NORM; ws.cell(row=i, column=3).alignment = RGT
    ws.cell(row=i, column=4, value=cmt).font = NORM
    for j in range(1,5):
        ws.cell(row=i, column=j).border = BORDER
        if i % 2 == 0: ws.cell(row=i, column=j).fill = ALT_FILL

# WI table
title_band(ws, 13, 5, "WATER INJECTION (bwpd)")
header_row(ws, 14, ["Scenario", "Cluster #1", "Cluster #2", "Total target", "Actual"])
wi_rows = [
    ("With SY-175 + SY-180 commissioned", 26000, 24600, 50600, None),
    ("Without SY-175/180 (current)",      26000, 19000, 45000, 53000),
    ("Technical rate",                    42200, 28800, 71000, None),
    ("Cluster physical capacity (hard cap)", 26000, 25000, "—", "—"),
]
for i, row in enumerate(wi_rows, start=15):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BOLD if j == 1 else NORM; c.border = BORDER
        if j > 1: c.alignment = RGT
        if i % 2 == 0: c.fill = ALT_FILL

# Bar chart of oil headlines
chart = BarChart()
chart.type = "col"
chart.style = 12
chart.title = "Shah field oil — Allowable vs TR vs Actual (BOPD)"
chart.y_axis.title = "BOPD"
chart_ws = wb.create_sheet("_chart_data", 99)
chart_ws["A1"] = "Metric"; chart_ws["B1"] = "BOPD"
chart_ws["A2"] = "Actual";       chart_ws["B2"] = 75733
chart_ws["A3"] = "Allowable";    chart_ws["B3"] = 76671
chart_ws["A4"] = "TR";           chart_ws["B4"] = 79983
chart_ws["A5"] = "Allow w/ inactive"; chart_ws["B5"] = 80591
chart_ws["A6"] = "Deliverability ceiling"; chart_ws["B6"] = 102752
data = Reference(chart_ws, min_col=2, min_row=1, max_row=6)
cats = Reference(chart_ws, min_col=1, min_row=2, max_row=6)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 10; chart.width = 18
chart.legend = None
ws.add_chart(chart, "A21")

widths(ws, [38, 14, 16, 18, 14])

# ---------- BOTTLENECK_MAP ----------
ws = wb.create_sheet("Bottleneck_Map")
ws["A1"] = "Bottleneck Categories — 9 root causes from RM comments"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26

title_band(ws, 3, 7, "ROOT-CAUSE CLASSIFICATION")
header_row(ws, 4, ["ID", "Category", "Indicator phrases", "Wells affected", "BOPD lost vs cap", "Linked opportunity", "Type"])
for i, row in enumerate(BOTTLENECK_MAP, start=5):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v if v is not None else "TBD")
        c.font = BOLD if j == 1 else NORM; c.border = BORDER; c.alignment = LFT
        if j in (4,5): c.alignment = RGT
        if i % 2 == 0: c.fill = ALT_FILL
        # Tag color by type
        if j == 7 and v == "Subsurface":     c.font = Font(name="Arial", size=10, bold=True, color=TEAL)
        if j == 7 and v == "Surface":        c.font = Font(name="Arial", size=10, bold=True, color=OIL)
        if j == 7 and v == "Surface/Completion": c.font = Font(name="Arial", size=10, bold=True, color=OIL)
        if j == 7 and v == "Completion":     c.font = Font(name="Arial", size=10, bold=True, color=DEEP)
        if j == 7 and v == "Water Injection": c.font = Font(name="Arial", size=10, bold=True, color=WATER)

# Bar chart of BOPD lost per category
chart = BarChart()
chart.type = "bar"
chart.style = 13
chart.title = "BOPD lost by bottleneck category"
chart.x_axis.title = "BOPD lost vs SH cap"
data_ws = wb["_chart_data"]
data_ws["D1"] = "Category"; data_ws["E1"] = "BOPD lost"
r = 2
for row in BOTTLENECK_MAP:
    if row[4] is not None:
        data_ws[f"D{r}"] = f"{row[0]} — {row[1][:30]}"
        data_ws[f"E{r}"] = row[4]
        r += 1
data = Reference(data_ws, min_col=5, min_row=1, max_row=r-1)
cats = Reference(data_ws, min_col=4, min_row=2, max_row=r-1)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 12; chart.width = 22
chart.legend = None
ws.add_chart(chart, f"A{5 + len(BOTTLENECK_MAP) + 3}")

widths(ws, [6, 38, 50, 12, 16, 22, 18])

# ---------- OPPORTUNITIES_SUMMARY ----------
ws = wb.create_sheet("Opportunities_Summary")
ws["A1"] = "All 8 De-Bottlenecking Opportunities — side by side"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26

title_band(ws, 3, 11, "OPPORTUNITY COMPARISON")
header_row(ws, 4, ["ID", "Title", "Category", "2026 low", "2026 high", "2026 mid",
                   "Full low", "Full high", "Conf.", "Capex low ($M)", "Capex high ($M)"])
for i, opp in enumerate(OPPORTUNITIES, start=5):
    mid = (opp[3] + opp[4]) / 2
    vals = [opp[0], opp[1], opp[2], opp[3], opp[4], mid, opp[5], opp[6], opp[7], opp[8], opp[9]]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BOLD if j in (1,3) else NORM
        c.border = BORDER
        if j >= 4 and j != 9: c.alignment = RGT
        if i % 2 == 0: c.fill = ALT_FILL

# Stacked range chart — show 2026 low & uplift to high
chart = BarChart()
chart.type = "bar"
chart.grouping = "stacked"
chart.overlap = 100
chart.style = 11
chart.title = "2026 gain range per opportunity (low → high, BOPD)"
chart.x_axis.title = "BOPD"

# Helper sheet for stacked data
sd = wb["_chart_data"]
sd["G1"] = "Opportunity"; sd["H1"] = "Low"; sd["I1"] = "Range"
for k, opp in enumerate(OPPORTUNITIES, start=2):
    sd[f"G{k}"] = f"{opp[0]} {opp[1][:35]}"
    sd[f"H{k}"] = opp[3]
    sd[f"I{k}"] = opp[4] - opp[3]
data1 = Reference(sd, min_col=8, min_row=1, max_row=1+len(OPPORTUNITIES))
data2 = Reference(sd, min_col=9, min_row=1, max_row=1+len(OPPORTUNITIES))
cats = Reference(sd, min_col=7, min_row=2, max_row=1+len(OPPORTUNITIES))
chart.add_data(data1, titles_from_data=True)
chart.add_data(data2, titles_from_data=True)
chart.set_categories(cats)
chart.height = 14; chart.width = 24
ws.add_chart(chart, f"A{5 + len(OPPORTUNITIES) + 3}")

widths(ws, [6, 50, 22, 11, 11, 11, 11, 11, 10, 14, 14])

# ---------- GAIN_BRIDGE ----------
ws = wb.create_sheet("Gain_Bridge")
ws["A1"] = "Production Gain Bridge — Current → 2026 Realistic Envelope"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26

title_band(ws, 3, 4, "WATERFALL — STARTING POINT TO TARGET (BOPD)")
header_row(ws, 4, ["Step", "Item", "Increment (BOPD)", "Cumulative (BOPD)"])

# Build waterfall using 2026 low estimates with 25 % overlap deduction on 4.1+4.3+4.4 group
wf = [
    ("Start",   "Current actual production",                              0,    75733),
]
cum = 75733
overlap_group = ["4.1", "4.3", "4.4"]
for opp in sorted(OPPORTUNITIES, key=lambda x: -(x[3]+x[4])/2):
    inc = opp[3]
    if opp[0] in overlap_group:
        inc = int(inc * 0.75)  # 25 % overlap deduction
        label = f"§{opp[0]} {opp[1][:35]} (×0.75 overlap)"
    else:
        label = f"§{opp[0]} {opp[1][:45]}"
    cum += inc
    wf.append(("Step", label, inc, cum))
wf.append(("End", "2026 realistic envelope", 0, cum))

for i, (step, item, inc, cumv) in enumerate(wf, start=5):
    ws.cell(row=i, column=1, value=step).font = BOLD
    ws.cell(row=i, column=2, value=item).font = NORM
    ws.cell(row=i, column=3, value=inc).font = NORM; ws.cell(row=i, column=3).alignment = RGT
    ws.cell(row=i, column=4, value=cumv).font = BOLD; ws.cell(row=i, column=4).alignment = RGT
    for j in range(1, 5):
        ws.cell(row=i, column=j).border = BORDER
    if step == "Start":
        for j in range(1, 5): ws.cell(row=i, column=j).fill = NAVY_FILL
        for j in range(1, 5): ws.cell(row=i, column=j).font = WHITE_BOLD
    elif step == "End":
        for j in range(1, 5): ws.cell(row=i, column=j).fill = OIL_FILL
        for j in range(1, 5): ws.cell(row=i, column=j).font = WHITE_BOLD
    elif i % 2 == 0:
        for j in range(1, 5): ws.cell(row=i, column=j).fill = ALT_FILL

# Cumulative line chart
chart = LineChart()
chart.style = 12
chart.title = "Cumulative production after each de-bottlenecking step (BOPD)"
chart.y_axis.title = "Cumulative BOPD"
chart.x_axis.title = "Step"
data = Reference(ws, min_col=4, min_row=4, max_row=4+len(wf))
cats = Reference(ws, min_col=2, min_row=5, max_row=4+len(wf))
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 12; chart.width = 26
chart.legend = None
ws.add_chart(chart, f"A{5 + len(wf) + 3}")

widths(ws, [10, 60, 18, 20])

# ---------- CAPEX_VS_GAIN ----------
ws = wb.create_sheet("Capex_vs_Gain")
ws["A1"] = "Capex vs Gain — Prioritization Matrix"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26

title_band(ws, 3, 6, "BUBBLE DATA")
header_row(ws, 4, ["ID", "Title", "Capex midpoint ($M)", "2026 gain midpoint (BOPD)", "$/BOPD ratio", "Confidence"])
for i, opp in enumerate(OPPORTUNITIES, start=5):
    capex_mid = (opp[8] + opp[9]) / 2
    gain_mid = (opp[3] + opp[4]) / 2
    ratio = (capex_mid * 1e6) / gain_mid if gain_mid > 0 else 0
    ws.cell(row=i, column=1, value=opp[0]).font = BOLD
    ws.cell(row=i, column=2, value=opp[1]).font = NORM
    ws.cell(row=i, column=3, value=capex_mid).font = NORM; ws.cell(row=i, column=3).alignment = RGT
    ws.cell(row=i, column=4, value=gain_mid).font = NORM; ws.cell(row=i, column=4).alignment = RGT
    ws.cell(row=i, column=5, value=round(ratio,0)).font = NORM; ws.cell(row=i, column=5).alignment = RGT
    ws.cell(row=i, column=6, value=opp[7]).font = NORM
    for j in range(1, 7):
        ws.cell(row=i, column=j).border = BORDER
        if i % 2 == 0: ws.cell(row=i, column=j).fill = ALT_FILL

# Scatter chart — Capex (X) vs Gain (Y)
chart = ScatterChart()
chart.title = "Capex vs Gain — opportunity positioning"
chart.style = 13
chart.x_axis.title = "Capex midpoint ($M)"
chart.y_axis.title = "2026 gain midpoint (BOPD)"
xvals = Reference(ws, min_col=3, min_row=5, max_row=4+len(OPPORTUNITIES))
yvals = Reference(ws, min_col=4, min_row=5, max_row=4+len(OPPORTUNITIES))
series = Series(yvals, xvals, title="Opportunities")
chart.series.append(series)
chart.height = 12; chart.width = 20
chart.legend = None
ws.add_chart(chart, f"A{5 + len(OPPORTUNITIES) + 3}")

widths(ws, [6, 50, 18, 22, 16, 14])

# ---------- ONE SHEET PER OPPORTUNITY ----------
for opp in OPPORTUNITIES:
    sname = f"Opp_{opp[0]}"
    ws = wb.create_sheet(sname)
    ws["A1"] = f"§{opp[0]} — {opp[1]}"; ws["A1"].font = BIG_TITLE
    ws.row_dimensions[1].height = 28
    ws["A2"] = f"Category: {opp[2]} · Confidence: {opp[7]}"; ws["A2"].font = ITAL

    # Quantification table
    title_band(ws, 4, 4, "QUANTIFICATION")
    rows = [
        ("2026 realistic gain — low (BOPD)",   opp[3]),
        ("2026 realistic gain — high (BOPD)",  opp[4]),
        ("Full potential — low (BOPD)",         opp[5]),
        ("Full potential — high (BOPD)",        opp[6]),
        ("Capex bracket — low ($M)",            opp[8]),
        ("Capex bracket — high ($M)",           opp[9]),
        ("Capex midpoint per BOPD gained ($/BOPD)",
         round(((opp[8]+opp[9])/2 * 1e6) / ((opp[3]+opp[4])/2), 0) if (opp[3]+opp[4]) > 0 else 0),
        ("Confidence",                          opp[7]),
    ]
    for i, (k, v) in enumerate(rows, start=5):
        ws.cell(row=i, column=1, value=k).font = BOLD
        ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=4)
        ws.cell(row=i, column=2, value=v).font = NORM
        for j in range(1, 5):
            ws.cell(row=i, column=j).border = BORDER

    # Mechanism
    title_band(ws, 14, 4, "MECHANISM")
    ws.merge_cells("A15:D20")
    ws["A15"] = opp[10]; ws["A15"].font = NORM; ws["A15"].alignment = LFT

    # Prerequisite
    title_band(ws, 22, 4, "PREREQUISITE DATA / WORK")
    ws.merge_cells("A23:D26")
    ws["A23"] = opp[11]; ws["A23"].font = NORM; ws["A23"].alignment = LFT

    widths(ws, [40, 16, 16, 16])

    # Mini-chart: gain range bar
    chart = BarChart()
    chart.type = "bar"
    chart.title = f"§{opp[0]} gain range (BOPD)"
    sd2 = wb["_chart_data"]
    base_row = 200 + OPPORTUNITIES.index(opp) * 5
    sd2.cell(row=base_row, column=1, value="Scenario")
    sd2.cell(row=base_row, column=2, value="BOPD")
    sd2.cell(row=base_row+1, column=1, value="2026 low")
    sd2.cell(row=base_row+1, column=2, value=opp[3])
    sd2.cell(row=base_row+2, column=1, value="2026 high")
    sd2.cell(row=base_row+2, column=2, value=opp[4])
    sd2.cell(row=base_row+3, column=1, value="Full low")
    sd2.cell(row=base_row+3, column=2, value=opp[5])
    sd2.cell(row=base_row+4, column=1, value="Full high")
    sd2.cell(row=base_row+4, column=2, value=opp[6])
    data = Reference(sd2, min_col=2, min_row=base_row, max_row=base_row+4)
    cats = Reference(sd2, min_col=1, min_row=base_row+1, max_row=base_row+4)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8; chart.width = 16
    chart.legend = None
    ws.add_chart(chart, "A28")

# ---------- DATA_GAPS ----------
ws = wb.create_sheet("Data_Gaps")
ws["A1"] = "Data Gaps — Required for Final Quantification"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26
title_band(ws, 3, 3, "RANKED BY IMPACT-ON-DELIVERABLE")
header_row(ws, 4, ["Rank", "Item", "Why needed"])
for i, (rank, item, why) in enumerate(DATA_GAPS, start=5):
    ws.cell(row=i, column=1, value=rank).font = BOLD
    ws.cell(row=i, column=2, value=item).font = BOLD
    ws.cell(row=i, column=3, value=why).font = NORM
    for j in range(1, 4):
        ws.cell(row=i, column=j).border = BORDER
        if i % 2 == 0: ws.cell(row=i, column=j).fill = ALT_FILL
        ws.cell(row=i, column=j).alignment = LFT
widths(ws, [6, 50, 80])

# ---------- FIELD_TOTALS ----------
ws = wb.create_sheet("Field_Totals")
ws["A1"] = "Field-Level Totals from Q2-2026 Allowable file"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26
title_band(ws, 3, 4, "OIL — TOTAL AT SHAH")
header_row(ws, 4, ["", "Allowable", "FTR (incl. inactive)", "FAR"])
ws.cell(row=5, column=1, value="Total at SHAH").font = BOLD
ws.cell(row=5, column=2, value=76671); ws.cell(row=5, column=3, value=79983); ws.cell(row=5, column=4, value=75733)
ws.cell(row=6, column=1, value="Total at JD").font = BOLD
ws.cell(row=6, column=2, value=69016); ws.cell(row=6, column=3, value=73482); ws.cell(row=6, column=4, value=68172)
ws.cell(row=7, column=1, value="Including Inactive — Allowable").font = BOLD
ws.cell(row=7, column=2, value=80591); ws.cell(row=7, column=3, value=79983); ws.cell(row=7, column=4, value="—")
for r in range(5, 8):
    for j in range(1, 5):
        ws.cell(row=r, column=j).border = BORDER
        if r % 2 == 0: ws.cell(row=r, column=j).fill = ALT_FILL
        if j > 1: ws.cell(row=r, column=j).alignment = RGT

title_band(ws, 10, 6, "WATER INJECTION — TOTAL AT SHAH (bwpd)")
header_row(ws, 11, ["Cluster", "Allowable w/ SY-175&180", "Max w/o", "Tech rate", "Actual", "Notes"])
wi_totals = [
    ("Cluster #1", 26000, 26000, 42200, 34000, "WI-C R1"),
    ("Cluster #2", 24600, 19000, 28800, 19000, "WI-C+CN R1"),
    ("WI to R2",   25500, 27000, 34500, 27000, ""),
    ("WI-C only R1", 16100, 18000, 20500, 18000, ""),
    ("WI-R1 C+CN", 25100, 18000, "—",  "—",   "Awaiting SY-175/180"),
    ("Total",      50600, 45000, 71000, 53000, "Field-level"),
]
for i, row in enumerate(wi_totals, start=12):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BOLD if (j == 1 or row[0] == "Total") else NORM
        c.border = BORDER
        if j > 1 and j < 6: c.alignment = RGT
        if row[0] == "Total":
            c.fill = NAVY_FILL; c.font = WHITE_BOLD
        elif i % 2 == 0:
            c.fill = ALT_FILL

widths(ws, [22, 22, 18, 14, 14, 24])

# ---------- WORKSHOP_AGENDA ----------
ws = wb.create_sheet("Workshop_Agenda")
ws["A1"] = "Q3-2026 Technical Workshop Agenda"; ws["A1"].font = BIG_TITLE
ws.row_dimensions[1].height = 26
ws["A2"] = "Per KoM plan — bi-weekly progress meetings + Q3 Technical WS"; ws["A2"].font = ITAL

title_band(ws, 4, 2, "AGENDA ITEMS")
agenda = [
    "1. Validate the bottleneck classification (9 categories) against AON's own internal view",
    "2. Confirm the FCT findings (once delivered) and align on §4.7 Surface back-pressure priorities",
    "3. Decide on §4.6 tracer campaign scope — which WI/producer pairs (139-SS, 145-SS first)",
    "4. Approve the §4.3 VSD retrofit shortlist and 2026 execution sequence",
    "5. Align on §4.5 Phase 2 Cluster #2 uplift study scope and timing",
    "6. Cross-reference §4.1 stim backlog with Obj 1.1C selected 5 to avoid double-counting",
    "7. Workshop output: signed-off opportunity list with executive owners assigned per item",
]
for i, item in enumerate(agenda, start=5):
    ws.cell(row=i, column=1, value=f"{i-4}.").font = BOLD
    ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=2)
    ws.cell(row=i, column=2, value=item[3:]).font = NORM
    ws.cell(row=i, column=2).alignment = LFT
    ws.row_dimensions[i].height = 22

widths(ws, [6, 100])

# Hide the helper data sheet
wb["_chart_data"].sheet_state = "hidden"

# Save
wb.save(OUT)
print(f"Saved: {OUT}")
