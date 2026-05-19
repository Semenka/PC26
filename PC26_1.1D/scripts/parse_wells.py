"""
PC26 Obj 1.1D — Parse the Q2-2026 Allowable file and classify every producer
string into one of nine bottleneck categories. Emits wells.json for the HTML
dashboard and a classified.csv for audit.
"""
import openpyxl
import json
import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT  = ROOT / "scripts"

XLSX = DATA / "Shah Q2 2026 Allowable-V1 (final).xlsx"

def text(v):
    if v is None: return ""
    return str(v).strip()

def num(v):
    if v is None or v == "": return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

# ---------- producer parsing ----------
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Q2-2026 OP Allowable RM_Upd"]

producers = []
for r in range(11, 135):
    cmpl = ws.cell(row=r, column=1).value
    if not cmpl: continue
    rec = {
        "cmpl":       text(cmpl),
        "uwi":        text(ws.cell(row=r, column=3).value),
        "reservoir":  text(ws.cell(row=r, column=4).value),
        "string":     text(ws.cell(row=r, column=5).value),
        "type":       text(ws.cell(row=r, column=6).value),
        "station":    text(ws.cell(row=r, column=7).value),
        "allowable":  num(ws.cell(row=r, column=9).value),
        "tr":         num(ws.cell(row=r, column=10).value),
        "inactive":   text(ws.cell(row=r, column=11).value),
        "exp_all":    num(ws.cell(row=r, column=12).value),
        "exp_tr":     num(ws.cell(row=r, column=13).value),
        "action":     text(ws.cell(row=r, column=14).value),
        "rm_prev":    text(ws.cell(row=r, column=16).value),
        "rm":         text(ws.cell(row=r, column=17).value),
        "sh_guide":   num(ws.cell(row=r, column=18).value),
        "test_date":  text(ws.cell(row=r, column=19).value),
        "ck":         num(ws.cell(row=r, column=20).value),
        "freq":       num(ws.cell(row=r, column=21).value),
        "pip":        num(ws.cell(row=r, column=22).value),
        "qo":         num(ws.cell(row=r, column=23).value),
        "wc":         num(ws.cell(row=r, column=24).value),
        "gor":        num(ws.cell(row=r, column=25).value),
        "bhcip":      num(ws.cell(row=r, column=27).value),
        "bhfp":       num(ws.cell(row=r, column=28).value),
        "pi":         num(ws.cell(row=r, column=30).value),
        "stim_yn":    text(ws.cell(row=r, column=32).value),
        "flow_test":  text(ws.cell(row=r, column=33).value),
        "pump_type":  text(ws.cell(row=r, column=34).value),
        "pump_range": text(ws.cell(row=r, column=35).value),
    }
    rec["rm_all"] = (rec["rm_prev"] + " | " + rec["rm"]).lower()
    producers.append(rec)

# ---------- classification ----------
def classify(p):
    cats = []
    rm = p["rm_all"]
    # S4 inactive
    if p["inactive"].upper() in ("Y", "YES") or "disconnect" in rm:
        cats.append("S4")
    # S1 low PIP / stim candidate
    if re.search(r"low\s*(pip|intake)|stim", rm) or \
       re.search(r"naphtha|hcl", rm) or \
       (p["stim_yn"].upper() == "Y"):
        cats.append("S1")
    # S2 high water cut
    wc = p["wc"] or 0
    if wc >= 60 or re.search(r"high\s*water\s*cut|wc\s*increase|watercut", rm):
        cats.append("S2")
    # S3 low BHFP / Pb violation
    if re.search(r"pwf\s*above\s*pb|pb\s*violation|limit\s*production", rm) or \
       (p["bhfp"] is not None and p["bhfp"] < 500 and (p["qo"] or 0) > 0):
        cats.append("S3")
    # S5 reservoir depletion
    if re.search(r"sector\s*vrr|pressure\s*depletion|pres\s*declin|improve\s*sector", rm):
        cats.append("S5")
    # C1 low DP across choke / VSD required
    if re.search(r"low\s*dp|vsd\s*required|choke\s*fully\s*open|pws\s*required", rm):
        cats.append("C1")
    # C2 ESP at max frequency
    if re.search(r"max\s*freq|higher\s*freq|esp.{0,20}60\s*hz|freq.{0,10}60", rm) or \
       (p["freq"] is not None and p["freq"] >= 58):
        cats.append("C2")
    # C3 surface back-pressure (proxy — wells with no assigned subsurface bottleneck,
    # full choke on test, and Qo << allowable)
    if not cats and p["qo"] and p["allowable"] and \
       p["qo"] < 0.7 * p["allowable"] and p["inactive"].upper() != "Y":
        cats.append("C3")
    return cats

for p in producers:
    p["cats"] = classify(p)

# ---------- field totals reading ----------
totals = {
    "allowable_active": num(ws.cell(row=144, column=9).value),
    "ftr_incl_inact":   num(ws.cell(row=144, column=10).value),
    "far":              num(ws.cell(row=144, column=11).value),
    "allowable_jd":     num(ws.cell(row=145, column=9).value),
    "ftr_jd":           num(ws.cell(row=145, column=10).value),
    "far_jd":           num(ws.cell(row=145, column=11).value),
    "allowable_incl_inact": num(ws.cell(row=151, column=9).value),
    "tr_shah":          num(ws.cell(row=151, column=10).value),
}

# ---------- WI parsing ----------
ws_wi = wb["Q2-2026 WI Allowable"]
wi_strings = []
for r in range(4, 13):
    well = ws_wi.cell(row=r, column=2).value
    if not well: continue
    wi_strings.append({
        "well":   text(well),
        "reservoir": text(ws_wi.cell(row=r, column=3).value),
        "alw_with": num(ws_wi.cell(row=r, column=4).value),
        "alw_without": num(ws_wi.cell(row=r, column=5).value),
        "tr":     num(ws_wi.cell(row=r, column=6).value),
        "actual": num(ws_wi.cell(row=r, column=7).value),
        "whip":   num(ws_wi.cell(row=r, column=8).value),
        "rm":     text(ws_wi.cell(row=r, column=9).value),
        "sim":    num(ws_wi.cell(row=r, column=10).value),
    })

# ---------- category roll-up ----------
CAT_DEFS = [
    ("S1", "Low PIP / stim candidate"),
    ("S2", "High water cut (>60%)"),
    ("S3", "Low BHFP — Pb risk"),
    ("S4", "Inactive string"),
    ("S5", "Reservoir pressure depletion"),
    ("C1", "Low DP choke / VSD required"),
    ("C2", "ESP at max frequency"),
    ("C3", "Surface back-pressure (proxy)"),
]
cat_counts = {cid: 0 for cid, _ in CAT_DEFS}
for p in producers:
    for c in p["cats"]:
        cat_counts[c] = cat_counts.get(c, 0) + 1

print(f"Producers parsed: {len(producers)}")
print(f"WI strings: {len(wi_strings)}")
print("Category counts:")
for cid, lbl in CAT_DEFS:
    print(f"  {cid} {lbl}: {cat_counts[cid]}")
print("Totals:", totals)

# ---------- write JSON for HTML + CSV for audit ----------
out = {
    "producers": producers,
    "wi": wi_strings,
    "totals": totals,
    "cat_counts": cat_counts,
}
with open(OUT / "wells.json", "w") as f:
    json.dump(out, f, indent=2, default=str)

with open(OUT / "classified.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cmpl","uwi","reservoir","string","allowable","tr","qo","wc","pi","bhfp","freq","inactive","cats","rm"])
    for p in producers:
        w.writerow([p["cmpl"], p["uwi"], p["reservoir"], p["string"],
                    p["allowable"], p["tr"], p["qo"], p["wc"], p["pi"],
                    p["bhfp"], p["freq"], p["inactive"], ";".join(p["cats"]),
                    (p["rm"] or p["rm_prev"])[:150]])
print("Wrote wells.json and classified.csv")
