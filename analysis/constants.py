"""
PC26 Obj 1.1C — project-wide constants: well calibrations, event dates,
pressure-survey anchors, palette, verbatim findings, candidate status.

Pressure-survey anchors (Pres @ datum 3900 ft) and completion/event dates
were extracted from the prior-session v1 deliverable.

BHFP calibration Δ (psi) was provided in the resume prompt (per-well from
the Q2-2026 Allowable), and cross-checked against "Latest BHFP (estimated)"
in the v1 workbook.
"""
from __future__ import annotations
from datetime import date

# ---------------------------------------------------------------------------
# Branding / palette
# ---------------------------------------------------------------------------
PALETTE = {
    "navy": "#0A2540",
    "oil":  "#F59E0B",
    "ink":  "#111827",
    "paper":"#FFFFFF",
    "muted":"#6B7280",
    "line": "#E5E7EB",
    "ok":   "#16A34A",
    "warn": "#F59E0B",
    "bad":  "#DC2626",
    # dark dashboard
    "bg":      "#0E1117",
    "panel":   "#151B24",
    "text":    "#F5F7FA",
    "subtle":  "#94A3B8",
    "grid":    "#1F2937",
    "confirmed":"#22C55E",   # solid green
    "inferred": "#F59E0B",   # dashed amber
}

# ---------------------------------------------------------------------------
# Candidates & canonical well identifiers
# ---------------------------------------------------------------------------
ALL_WELLS = ["SY-069", "SY-074", "SY-110", "SY-120", "SY-131", "SY-133", "SY-146"]
FINAL_FIVE = ["SY-110", "SY-069", "SY-074", "SY-120", "SY-146"]  # revised final-5
BACKUP = ["SY-133"]
DEFERRED = ["SY-131"]  # PI increased +15% — not a degradation case

# Map raw R1-workbook well token -> canonical id
WELL_ALIAS = {
    "SY - 0069 - TB": "SY-069",
    "SY - 0074 - TB": "SY-074",
    "SY - 0110 - TB": "SY-110",
    "SY - 0120 - TB": "SY-120",
    "SY - 0131 - TB": "SY-131",
    "SY - 0133 - TB": "SY-133",
}

# ---------------------------------------------------------------------------
# PI methodology constants
# ---------------------------------------------------------------------------
# BHFP = PIP + Δ   (Δ in psi)
BHFP_DELTA = {
    "SY-069": 365,
    "SY-074": 672,
    "SY-110": 354,
    "SY-120": 411,
    "SY-131": 284,
    "SY-133": 289,
}
BHFP_DELTA_DEFAULT = 360  # field median for any unlisted well

# physical drawdown filter (Pres - BHFP)
DRAWDOWN_MIN = 30
DRAWDOWN_MAX = 2500
PRES_EXTRAP_CAP_DAYS = 365  # ±1 year extrapolation past nearest survey

# ---------------------------------------------------------------------------
# Formal reservoir-pressure survey anchors (from prior v1 workbook)
# ---------------------------------------------------------------------------
# each entry: (date, Pres @ 3900 ft, test_type)
PRES_SURVEYS = {
    "SY-069": [(date(2024, 11, 24), 946.95, "GRAD")],
    "SY-074": [(date(2016,  8, 25), 1553.50, "GRAD (pre-ST baseline, R2 layer)")],
    "SY-110": [(date(2020, 12,  6),  985.99, "BHCIP"),
               (date(2025,  3, 19), 1015.17, "GRAD")],
    "SY-120": [(date(2021,  4, 20),  932.19, "BHCIP"),
               (date(2024, 10,  1),  734.58, "GRAD")],
    "SY-131": [(date(2023,  3, 17), 1094.19, "BHCIP"),
               (date(2026,  3,  2),  846.59, "GRAD")],
    "SY-133": [(date(2021,  7, 12), 1072.59, "BHCIP"),
               (date(2025,  1, 23),  828.45, "GRAD")],
    "SY-146": [(date(2025,  5, 13), 2090.42, "BHCIP (injection)"),
               (date(2025,  9, 25), 1789.69, "GRAD")],
}

# ---------------------------------------------------------------------------
# Events — confirmed (solid green) vs inferred (dashed amber)
# ---------------------------------------------------------------------------
CONFIRMED_EVENTS = {
    "SY-069": [(date(2023, 1, 17), "Recompletion")],
    "SY-074": [(date(2024, 8, 11), "ST2 sidetrack")],
    "SY-110": [(date(2023, 1, 31), "Recompletion")],
    "SY-120": [(date(2020, 8, 12), "Re-completion / startup")],
    "SY-131": [(date(2020,10, 23), "Startup")],
    "SY-146": [(date(2025, 7, 10), "New completion (water injector)")],
}

# Qo step-up detector parameters (inferred events)
STEP_UP_PCT = 0.30          # ≥ +30% vs rolling-median baseline
STEP_UP_WINDOW = 3          # sustained over ≥ 3 subsequent tests
STEP_UP_MIN_GAP_DAYS = 14   # min spacing between inferred events

# ---------------------------------------------------------------------------
# Well classification (from prior v1 Summary sheet)
# ---------------------------------------------------------------------------
WELL_META = {
    "SY-069": dict(reservoir="SIMSIMA R1", type="Horizontal",
                   category="PI degradation", status="Active producer",
                   completion="2023-01-17", allowable=90, tr=90, sh_cap=2000,
                   station="SHAH RDS-2"),
    "SY-074": dict(reservoir="SIMSIMA R1", type="Horizontal (ST2 side-tracked Q3-2024)",
                   category="High dolomitization (recent sidetrack, fastest decline)",
                   status="Active producer", completion="2024-08-11",
                   allowable=120, tr=120, sh_cap=2000, station="SHAH"),
    "SY-110": dict(reservoir="SIMSIMA R1", type="Horizontal",
                   category="PI degradation (deposition flagged)",
                   status="Active producer", completion="2023-01-31",
                   allowable=260, tr=300, sh_cap=2000, station="SHAH (CDS/RDS)"),
    "SY-120": dict(reservoir="SIMSIMA R1", type="Horizontal",
                   category="High dolomitization (best performer, declining)",
                   status="Active producer", completion="~2020",
                   allowable=350, tr=350, sh_cap=2000, station="SHAH"),
    "SY-131": dict(reservoir="SIMSIMA R1", type="Horizontal",
                   category="PI degradation (KoM example list)",
                   status="Active producer", completion="~2020",
                   allowable=270, tr=270, sh_cap=2000, station="SHAH (RDS)"),
    "SY-133": dict(reservoir="SIMSIMA R1", type="Horizontal",
                   category="PI degradation (worst performer, high WC)",
                   status="Active producer (very low rate)", completion="Original",
                   allowable=100, tr=100, sh_cap=2000, station="SHAH (RDS)"),
    "SY-146": dict(reservoir="SIMSIMA R1", type="Horizontal water injector",
                   category="Water injector — poor injectivity (KoM scope)",
                   status="Active injector (under-performing)", completion="2025-07-10",
                   allowable=1800, tr=2000, sh_cap=1800, station="SHAH WI"),
}

# ---------------------------------------------------------------------------
# Field / reservoir context (Cover tab + slide 3)
# ---------------------------------------------------------------------------
RESERVOIR_CONTEXT = {
    "STOOIP":            "3,439 MMSTB",
    "Np (12/2022)":      "590 MMBBL",
    "Recovery factor":   "17.2%",
    "Bubble point Pb":   "392 psi",
    "Solution GOR":      "100 scf/stb",
    "Oil API":           "30°",
    "Oil viscosity @ Pb":"2.3 cp",
    "Reservoir type":    "Dual-media fractured carbonate (only one in ADNOC Onshore)",
    "SH Guideline Max Qo (R1 H)":"2,000 BOPD",
    "SH Guideline Max GOR":     "450 scf/bbl",
    "SH Guideline Min BHFP":    "1,232 psia",
    "SH Guideline Max WI rate": "1,800 bwpd",
    "SH Guideline Max BHIP":    "7,400 psia",
}

# ---------------------------------------------------------------------------
# Verbatim key-findings strings (preserve exact language from prompt)
# ---------------------------------------------------------------------------
KEY_FINDINGS = {
    "SY-110": (
        "Most severe candidate: D = 53 %/yr, PI collapses 8.9 → 0.8 "
        "(−91 % over 5.6 y). Reservoir pressure stable 985→1015 psi — "
        "decline is skin/deposition-driven, not depletion."
    ),
    "SY-069": (
        "Recent-window D = 62 %/yr (shorter valid window — only one formal "
        "Pres survey in Nov-2024 limits PI calculation to ±365 d around "
        "that date). Longest history in set (135 tests, 2015-2026) ideal "
        "for benchmarking."
    ),
    "SY-074": (
        "PI NOT computable — only the 2016 pre-sidetrack GRAD survey is "
        "available and the current well is on the new ST2 lateral (Aug-2024). "
        "Qualitative case is clear: 560 → 144 BOPD (−74 %) in 18 months, "
        "WC 3.5 → 42 %. Pre-stim formal PBU mandatory."
    ),
    "SY-120": (
        "Only 6 %/yr PI decline despite ~200 psi Pres depletion "
        "(932 → 735 psi, 2021→2024). Decline is pressure-driven, not skin — "
        "stimulation gain will be modest; candidate is about sustaining peak "
        "deliverability (still producing 651 BOPD, recent peak 1486 BOPD)."
    ),
    "SY-131": (
        "PI actually INCREASED +15 % across the window. Not a PI-degradation "
        "case — the apparent Qo decline is pressure-decline only "
        "(1094 → 847 psi, 2023→2026). Defer from final stimulation list."
    ),
    "SY-133": (
        "D = 24 %/yr but WC 1.7 → 51 % — water-coning is the dominant "
        "mechanism, not skin. Stimulation alone may worsen water cut. "
        "Backup only — requires PLT + WSO before any stim design."
    ),
    "SY-146": (
        "Supporting candidate — data-only: 2 formal pressure anchors "
        "(May-2025 BHCIP 2090 psi, Sep-2025 GRAD 1790 psi). No production "
        "PI applies (water injector). Narrative pending additional "
        "post-completion injectivity data."
    ),
}

EXEC_SUMMARY_BULLETS = [
    "Five stimulation candidates selected from 7-well screen (SY-131 deferred; SY-133 backup only).",
    "SY-110 is the lead: PI collapses 8.9 → 0.8 over 5.6 years (−91 %), stable Pres → skin-driven.",
    "SY-069 recent-window decline D = 62 %/yr, longest history (135 tests, 2015-2026).",
    "SY-074 lacks post-ST2 pressure data — PI not computable; formal PBU survey mandatory pre-stim.",
    "SY-120 decline is pressure-driven (ΔPres ≈ −200 psi), only 6 %/yr PI degradation — sustain play.",
    "No formal stim-event logs in dataset: only 4 confirmed events (recompletion/ST2/startup); rest inferred from Qo step-ups.",
]

DATA_GAPS = [
    "No formal stimulation-event database — only completion/sidetrack/startup dates are confirmed.",
    "SY-074 has a single pre-ST2 (2016, R2 layer) pressure survey — cannot calibrate PI for current ST2 lateral.",
    "SY-069 has a single formal Pres survey (Nov-2024) — valid PI window is ±365 d around that date.",
    "SY-131 PI trend is positive +15 % — narrative-level examples from KoM list are not supported by the data.",
    "SY-133 decline is water-coning dominated (WC 1.7 → 51 %) — PI fit D = 24 %/yr masks the true mechanism.",
    "Shah Q2-2026 Allowable workbook was not accessible to the pipeline — survey anchors and BHFP Δ "
    "taken from the prior v1 deliverable and the resume-prompt calibration table.",
]

CONCLUSIONS = [
    "Execute SY-110 first — highest decline, stable Pres, clear skin/deposition signal, "
    "deposition-tailored recipe (scale pre-flush + HCl).",
    "Queue SY-069 second — long history + recent steep decline; 15 % HCl + naphtha 2-stage baseline.",
    "SY-074 requires a formal PBU survey before stim; pre-job PLT mandatory to map ST2 inflow.",
    "SY-120 is the sustain-play candidate — dolomite-tailored recipe, avoid over-drawdown (Pb = 392 psi).",
    "SY-146 injectivity stim: naphtha pre-flush + HCl main stage; Hall-plot analysis pre/post.",
    "Defer SY-131 (no real PI degradation); hold SY-133 as backup (needs WSO + PLT).",
    "Request Q2-2026 Allowable + formal stim-event register from operator before rig schedule finalisation.",
]
