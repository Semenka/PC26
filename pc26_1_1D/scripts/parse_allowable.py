"""Parse Shah Q2-2026 Allowable workbook and classify ~124 strings into 9 bottleneck categories.

Emits wells.json with per-string tags and bottleneck_counts.json with category aggregates.
"""
import json
import re
from pathlib import Path
import openpyxl

DATA = Path('/home/user/pc26_1_1D/data/Shah Q2 2026 Allowable-V1 (final).xlsx')
OUT_WELLS = Path('/home/user/pc26_1_1D/data/wells.json')
OUT_COUNTS = Path('/home/user/pc26_1_1D/data/bottleneck_counts.json')

# Column map (sheet "Q2-2026 OP Allowable RM_Upd" — headers at row 9, data rows 11-134)
COLS = {
    'cmpl': 1, 'string': 2, 'uwi': 3, 'reservoir': 4, 'type_tb': 5, 'hv': 6,
    'station': 7, 'allowable': 9, 'tr': 10, 'inactive': 11,
    'exp_allow': 12, 'exp_tr': 13, 'action_inactive': 14, 'dws': 15,
    'rm_highlights': 16, 'rm_comment': 17, 'sh_guidelines': 18,
    'test_date': 19, 'ck_size': 20, 'esp_freq': 21, 'pip': 22,
    'qo': 23, 'wc': 24, 'gor': 25,
    'psurv_date': 26, 'bhcip': 27, 'bhfp': 28,
    'pi_date': 29, 'pi': 30, 'stim_date': 31, 'stim_yn': 32, 'ft_req': 33,
    'pump_type': 34, 'pump_range': 35, 'qw': 36,
}

# Classification regex — applied to combined RM highlights + RM comment (case-insensitive)
BOTTLENECK_PATTERNS = {
    'S1': [r'low\s*pip', r'low\s*intake', r'stim(ulation)?\s*(required|candidate|recommended)',
           r'propose\s*to\s*do\s*stimulation', r'naphtha', r'hcl\s*stim', r'acid(izing|\s*job)'],
    'S2': [r'high\s*water\s*cut', r'wc\s*(increase|>\s*60)', r'water\s*cut\s*(>|above)\s*60',
           r'high\s*wc', r'water\s*shut.?off', r'wso'],
    'S3': [r'bhfp\s*(<|below)\s*\d', r'low\s*bhfp', r'close\s*to\s*the\s*gl',
           r'limit\s*production\s*to\s*get\s*pwf', r'pwf\s*above\s*pb', r'close\s*to\s*pb',
           r'bubble\s*point'],
    'S4': [],  # handled separately via Inactive=Y column
    'S5': [r'improve\s*sector\s*vrr', r'pressure\s*depletion', r'pres\s*declining',
           r'reservoir\s*pressure\s*support'],
    'C1': [r'low\s*dp\s*(across\s*)?choke', r'low\s*d\s*p', r'vsd\s*required',
           r'choke\s*fully\s*open', r'install\s*vsd', r'pws.?vsd\s*required'],
    'C2': [r'esp\s*(running\s*)?at\s*max', r'max\s*frequency', r'freq\s*(is|=|\s)?\s*60\s*hz',
           r'running\s*at\s*60\s*hz', r'test\s*at\s*higher\s*freq'],
    'C3': [],  # inferred later from full-choke + low-Qo + high WHFT proxy
}

def _text_for_well(ws, r):
    parts = []
    for col in (COLS['rm_highlights'], COLS['rm_comment'], COLS['action_inactive']):
        v = ws.cell(row=r, column=col).value
        if v:
            parts.append(str(v))
    return ' \n '.join(parts)

def classify(ws, r, well):
    text = _text_for_well(ws, r).lower()
    tags = []
    # S4 — inactive (Y / Disconnected / Observer)
    if well['inactive'] in ('Y', 'DISCONNECTED', 'OBSERVER'):
        tags.append('S4')
    # S1-S3, S5, C1-C2 from regex
    for cat, patterns in BOTTLENECK_PATTERNS.items():
        if not patterns:
            continue
        for p in patterns:
            if re.search(p, text):
                tags.append(cat)
                break
    # C2 proxy: ESP freq >= 58 Hz
    freq = well.get('esp_freq')
    try:
        if freq is not None and float(freq) >= 58:
            if 'C2' not in tags:
                tags.append('C2')
    except (TypeError, ValueError):
        pass
    # C3 proxy: choke ≥ 256/64 AND test Qo < 70% of allowable (flagged but cannot quantify without FCT)
    try:
        ck = well.get('ck_size')
        allow = well.get('allowable')
        qo = well.get('qo')
        if ck and allow and qo and float(ck) >= 256 and float(qo) < 0.7 * float(allow):
            tags.append('C3')
    except (TypeError, ValueError):
        pass
    return sorted(set(tags))

def main():
    wb = openpyxl.load_workbook(DATA, data_only=True)
    ws = wb['Q2-2026 OP Allowable RM_Upd']
    wells = []
    for r in range(11, 135):
        s = ws.cell(row=r, column=COLS['string']).value
        if not (s and isinstance(s, str) and s.upper().startswith('SY')):
            continue
        well = {}
        for k, col in COLS.items():
            v = ws.cell(row=r, column=col).value
            if k in ('test_date', 'psurv_date', 'pi_date', 'stim_date') and v is not None:
                # serialize dates
                try:
                    v = v.strftime('%Y-%m-%d')
                except AttributeError:
                    v = str(v)
            well[k] = v
        # Normalize
        well['allowable'] = well.get('allowable') or 0
        well['tr'] = well.get('tr') or 0
        well['inactive'] = (well.get('inactive') or 'N').strip().upper()
        well['tags'] = classify(ws, r, well)
        wells.append(well)

    # Aggregate category counts
    cat_meta = {
        'S1': ('Low PIP / stim candidate', 'Subsurface', 12000),
        'S2': ('High water cut (>60%)', 'Subsurface', 7000),
        'S3': ('Low BHFP / close to Pb', 'Subsurface', 1800),
        'S4': ('Inactive string — WO backlog', 'Subsurface', 3920),
        'S5': ('Reservoir P depletion', 'Subsurface', 5000),
        'C1': ('Low ΔP across choke / VSD req.', 'Surface/Completion', 6500),
        'C2': ('ESP at max frequency', 'Completion', 3500),
        'C3': ('Surface back-pressure (proxy)', 'Surface', None),
    }
    counts = {}
    for code, (label, group, bopd_lost) in cat_meta.items():
        wells_in_cat = [w for w in wells if code in w['tags']]
        counts[code] = {
            'label': label,
            'group': group,
            'bopd_lost': bopd_lost,
            'wells_affected': len(wells_in_cat),
            'wells': [w['string'] for w in wells_in_cat[:40]],
        }
    # WI categories (hand-curated from WI sheet text)
    counts['W1'] = {'label': 'Cluster capacity ceiling 25/26 Mbwpd', 'group': 'Water Injection',
                   'bopd_lost': None, 'wells_affected': None, 'wells': []}
    counts['W2'] = {'label': 'WI well integrity (SY-175, SY-180)', 'group': 'Water Injection',
                   'bopd_lost': None, 'wells_affected': 2, 'wells': ['175 TB', '180 TB']}
    counts['W3'] = {'label': 'R1→R2 inter-reservoir water loss', 'group': 'Water Injection',
                   'bopd_lost': None, 'wells_affected': 2, 'wells': ['139 SS', '145 SS']}
    counts['W4'] = {'label': 'High-WC producers loading PW system', 'group': 'Water Injection',
                   'bopd_lost': None, 'wells_affected': None, 'wells': []}

    # Derive high-WC producers (>85%) for W4
    hiwc = [w for w in wells if w.get('wc') and isinstance(w['wc'], (int, float)) and w['wc'] > 85]
    counts['W4']['wells_affected'] = len(hiwc)
    counts['W4']['wells'] = [w['string'] for w in hiwc[:20]]

    OUT_WELLS.write_text(json.dumps(wells, default=str, indent=2))
    OUT_COUNTS.write_text(json.dumps(counts, indent=2))
    print(f'Wells parsed:        {len(wells)}')
    for code, d in counts.items():
        print(f'  {code} {d["label"]:42s}  n={d["wells_affected"]}')

if __name__ == '__main__':
    main()
