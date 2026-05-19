// PC26 Obj 1.1D — Shah Field De-Bottlenecking deck
// pptxgenjs 13.3 × 7.5 wide; palette navy/oil/teal/mint; Georgia + Calibri.

const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';   // 13.333 × 7.5 in
pres.title  = 'PC26 1.1D — Shah De-Bottlenecking';
pres.author = 'TotalEnergies ALSG × ADNOC Onshore';

const NAVY  = '0A2540';
const DEEP  = '1E3A5F';
const OIL   = 'F59E0B';
const OIL_S = 'FBBF24';
const TEAL  = '0891B2';
const MINT  = '34D399';
const WATER = '06B6D4';
const BAD   = 'DC2626';
const GOOD  = '16A34A';
const INK   = '0F172A';
const BG    = 'F8FAFC';
const LINE  = 'CBD5E1';
const TEXT  = '0F172A';
const SUB   = '475569';
const DIM   = '94A3B8';

const FONT_HEAD = 'Georgia';
const FONT_BODY = 'Calibri';

const W = 13.333, H = 7.5;
const M = 0.45;            // page margin
const HDR_H = 0.55;        // top band height
const FTR_Y = H - 0.34;    // footer y

function addBase(s, title, opts = {}) {
  // top navy band
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: W, h: HDR_H, fill: { color: NAVY } });
  s.addShape(pres.ShapeType.rect, { x: 0, y: HDR_H, w: W, h: 0.04, fill: { color: OIL }, line: { type: 'none' } });
  // title text
  s.addText(title, {
    x: M, y: 0.05, w: W - 2*M, h: HDR_H - 0.10,
    fontFace: FONT_HEAD, fontSize: opts.titleSize || 22, bold: true, color: 'FFFFFF',
    valign: 'middle'
  });
  // small section label (right side of header)
  if (opts.section) {
    s.addText(opts.section, {
      x: W - M - 3.6, y: 0.05, w: 3.5, h: HDR_H - 0.10,
      fontFace: FONT_BODY, fontSize: 11, color: OIL_S, align: 'right', valign: 'middle'
    });
  }
  // footer
  s.addShape(pres.ShapeType.line, { x: M, y: FTR_Y - 0.06, w: W - 2*M, h: 0,
    line: { color: LINE, width: 0.5 } });
  s.addText('PC26 · Obj 1.1D · Shah De-Bottlenecking · TotalEnergies ALSG × ADNOC Onshore', {
    x: M, y: FTR_Y, w: 9, h: 0.28,
    fontFace: FONT_BODY, fontSize: 9, color: DIM, valign: 'middle'
  });
  s.addText(`${opts.page || ''}`, {
    x: W - M - 1.20, y: FTR_Y, w: 1.15, h: 0.28,
    fontFace: FONT_BODY, fontSize: 9, color: DIM, align: 'right', valign: 'middle'
  });
}

function statCard(s, x, y, w, h, value, label, sub, accent = OIL) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h,
    fill: { color: 'FFFFFF' }, line: { color: LINE, width: 0.5 }, rectRadius: 0.06 });
  s.addShape(pres.ShapeType.rect, { x, y, w, h: 0.06,
    fill: { color: accent }, line: { type: 'none' } });
  s.addText(label.toUpperCase(), { x: x + 0.18, y: y + 0.16, w: w - 0.3, h: 0.30,
    fontFace: FONT_BODY, fontSize: 9, color: SUB, charSpacing: 1, bold: true });
  s.addText(value, { x: x + 0.18, y: y + 0.42, w: w - 0.3, h: 0.70,
    fontFace: FONT_HEAD, fontSize: 28, bold: true, color: NAVY });
  s.addText(sub, { x: x + 0.18, y: y + 1.12, w: w - 0.3, h: 0.35,
    fontFace: FONT_BODY, fontSize: 10, color: SUB });
}

function band(s, x, y, w, h, fill, text, color = 'FFFFFF', size = 11) {
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { type: 'none' } });
  s.addText(text, { x: x + 0.14, y, w: w - 0.2, h, fontFace: FONT_BODY, fontSize: size,
    bold: true, color, valign: 'middle' });
}

// ----------------------------------------------------------------
// 1. TITLE
const s1 = pres.addSlide();
s1.background = { color: NAVY };
s1.addShape(pres.ShapeType.rect, { x: 0, y: H - 0.18, w: W, h: 0.18, fill: { color: OIL }, line: { type: 'none' } });
// decorative diagonal accent
s1.addShape(pres.ShapeType.rect, { x: W - 3.4, y: 0, w: 3.4, h: 0.06, fill: { color: OIL }, line: { type: 'none' } });
s1.addText('PC26 · Objective 1.1D', {
  x: M, y: 1.3, w: W - 2*M, h: 0.5,
  fontFace: FONT_BODY, fontSize: 13, bold: true, color: OIL_S, charSpacing: 4
});
s1.addText('Shah Field De-Bottlenecking', {
  x: M, y: 1.9, w: W - 2*M, h: 1.1,
  fontFace: FONT_HEAD, fontSize: 44, bold: true, color: 'FFFFFF'
});
s1.addText('Surface & subsurface opportunities · quantified catalogue · 2026 envelope', {
  x: M, y: 3.05, w: W - 2*M, h: 0.45,
  fontFace: FONT_HEAD, italic: true, fontSize: 18, color: OIL_S
});
s1.addShape(pres.ShapeType.line, { x: M, y: 3.7, w: 2.5, h: 0,
  line: { color: OIL, width: 2 } });
s1.addText([
  { text: 'TotalEnergies ALSG × ADNOC Onshore\n', options: { fontSize: 13, bold: true, color: 'FFFFFF' } },
  { text: 'Asset Lead FP: Andrey Semenov\n', options: { fontSize: 12, color: 'CBD5E1' } },
  { text: 'Issued 19-May-2026', options: { fontSize: 11, color: '94A3B8' } }
], { x: M, y: 3.85, w: W - 2*M, h: 1.4, fontFace: FONT_BODY });

// stat strip at bottom
const cw = 2.8, cy = 5.4, cx0 = M;
const stats = [
  ['75,733', 'BOPD field actual', OIL],
  ['+10–12k', 'BOPD 2026 envelope', MINT],
  ['8',      'opportunities', WATER],
  ['9',      'data gaps blocking final', BAD],
];
stats.forEach((st, i) => {
  const x = cx0 + i * (cw + 0.2);
  s1.addShape(pres.ShapeType.rect, { x, y: cy, w: cw, h: 1.2,
    fill: { color: '0F172A' }, line: { color: OIL, width: 0.5 } });
  s1.addText(st[0], { x: x + 0.15, y: cy + 0.05, w: cw - 0.3, h: 0.7,
    fontFace: FONT_HEAD, fontSize: 30, bold: true, color: st[2] });
  s1.addText(st[1], { x: x + 0.15, y: cy + 0.75, w: cw - 0.3, h: 0.42,
    fontFace: FONT_BODY, fontSize: 11, color: 'CBD5E1' });
});

// ----------------------------------------------------------------
// 2. EXECUTIVE SUMMARY
const s2 = pres.addSlide();
addBase(s2, 'Executive Summary', { section: 'PC26 · Obj 1.1D', page: '2 / 12' });

const sy = 0.85;
const stats2 = [
  ['75,733',  'BOPD current FAR',       'Q1-2026 · vs 79,983 TR (–5.6%)', OIL],
  ['+10–12k', 'BOPD 2026 uplift',       '+13% field oil within 12 months', MINT],
  ['8',       'opportunities catalogued','5 subsurface · 2 surface · 1 cross', TEAL],
  ['9',       'critical data gaps',      'FCT + IPM model top of list', BAD],
];
stats2.forEach((st, i) => {
  statCard(s2, M + i * 3.10, sy, 2.95, 1.55, st[0], st[1], st[2], st[3]);
});

// findings panel
s2.addShape(pres.ShapeType.rect, { x: M, y: sy + 1.85, w: W - 2*M, h: 0.05,
  fill: { color: OIL }, line: { type: 'none' } });
s2.addText('KEY FINDINGS', { x: M, y: sy + 1.95, w: 4, h: 0.30,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: NAVY, charSpacing: 1.5 });

const colW = (W - 2*M - 0.4) / 3, colY = sy + 2.40, colH = 3.45;
const findings = [
  ['Sub-surface levers dominate',
   ['Of 124 active strings, 36 are stim candidates (S1) and 55 are >60% WC (S2).',
    'Reservoir VRR is the upstream control variable — restoring SY-175 + SY-180 unlocks +16,000 bwpd of stranded injection.',
    'Saih Rawl analog (SPE 68222): +12% oil per +30% WI at mature waterflood.'], MINT],
  ['Surface side under-quantified — pending FCT',
   ['§4.7 back-pressure estimate (+1.5–2.5 kBOPD) carries widest uncertainty.',
    'Each 10 psi separator-pressure cut ≈ +800 BOPD across 80 R1 producers.',
    'GAP/Prosper IPM model + Jan-2026 FCT report are blocking inputs.'], OIL],
  ['Execution path: front-load WI uplift + VSD retrofits',
   ['Top 3 by 2026 gain: §4.5 WI capacity, §4.7 back-pressure, §4.6 PW redistribution.',
    'VSD/PWS retrofit (§4.3) is highest-confidence — proven on 10 wells already.',
    'After 25% overlap deduction, realistic 2026 envelope ~10,000–12,000 BOPD.'], TEAL],
];
findings.forEach((f, i) => {
  const x = M + i * (colW + 0.2);
  s2.addShape(pres.ShapeType.rect, { x, y: colY, w: colW, h: colH,
    fill: { color: 'FFFFFF' }, line: { color: LINE, width: 0.5 } });
  s2.addShape(pres.ShapeType.rect, { x, y: colY, w: colW, h: 0.05,
    fill: { color: f[2] }, line: { type: 'none' } });
  s2.addText(f[0], { x: x + 0.15, y: colY + 0.15, w: colW - 0.3, h: 0.55,
    fontFace: FONT_HEAD, fontSize: 13, bold: true, color: NAVY });
  s2.addText(f[1].map(b => ({ text: b, options: { bullet: { code: '25AA' } } })),
    { x: x + 0.18, y: colY + 0.78, w: colW - 0.32, h: colH - 0.85,
      fontFace: FONT_BODY, fontSize: 11, color: TEXT, paraSpaceAfter: 6, valign: 'top' });
});

// ----------------------------------------------------------------
// 3. FIELD BASELINE
const s3 = pres.addSlide();
addBase(s3, 'Field baseline — Allowable, TR, Actual', { section: '§ Baseline', page: '3 / 12' });

// Oil chart
s3.addText('OIL PRODUCTION (BOPD)', { x: M, y: 0.75, w: 6.0, h: 0.32,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: SUB, charSpacing: 1 });
s3.addChart(pres.ChartType.bar, [
  { name: 'BOPD',
    labels: ['Actual (FAR)', 'Allowable', 'TR', 'Allow w/ Inactive', 'Deliv. ceiling'],
    values: [75733, 76671, 79983, 80591, 102752] }
], {
  x: M, y: 1.10, w: 6.2, h: 4.0,
  chartColors: [OIL, TEAL, MINT, WATER, DEEP],
  chartColorsOpacity: 100,
  barDir: 'col', barGapWidthPct: 40,
  showLegend: false, showValue: true,
  dataLabelFontSize: 9, dataLabelColor: TEXT,
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
  valAxisHidden: false, catAxisHidden: false,
  showTitle: false, plotArea: { fill: { color: 'FFFFFF' } }
});

// WI table
s3.addText('WATER INJECTION (bwpd)', { x: 7.0, y: 0.75, w: 6.0, h: 0.32,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: SUB, charSpacing: 1 });
const wiHead = [['Scenario', 'Cluster #1', 'Cluster #2', 'Total target', 'Actual']];
const wiBody = [
  ['w/ SY-175 + SY-180', '26,000', '24,600', '50,600', '—'],
  ['w/o SY-175 + SY-180', '26,000', '19,000', '45,000', '53,000'],
  ['Technical rate',     '42,200', '28,800', '71,000', '—'],
  ['Cluster physical cap','26,000', '25,000', '—',     '—'],
];
const wiRows = wiHead.concat(wiBody);
s3.addTable(wiRows.map((r, ri) => r.map((c, ci) => ({
  text: c,
  options: {
    fontFace: FONT_BODY, fontSize: 10,
    bold: ri === 0 || ci === 0,
    color: ri === 0 ? 'FFFFFF' : TEXT,
    fill: { color: ri === 0 ? DEEP : (ri % 2 === 0 ? BG : 'FFFFFF') },
    align: ci === 0 ? 'left' : 'right',
    valign: 'middle',
  }
}))), {
  x: 7.0, y: 1.10, w: 5.95,
  colW: [1.75, 1.05, 1.05, 1.05, 1.05],
  rowH: 0.33, border: { type: 'solid', pt: 0.5, color: LINE }
});

// Insights band
band(s3, M, 5.30, W - 2*M, 0.35, NAVY,
  'Gap analysis: 4,250 BOPD under-TR (5.6%). WI under-injecting by ~18,000 bwpd vs technical — SY-175/180 alone recovers ~16,000.',
  'FFFFFF', 11);
s3.addText([
  { text: 'Source: ', options: { bold: true, color: NAVY } },
  { text: 'Q2-2026 Allowable file, sheet ', options: { color: TEXT } },
  { text: 'Q2-2026 OP Allowable RM_Upd', options: { color: TEXT, fontFace: 'Consolas' } },
  { text: ' (rows 11–134) and ', options: { color: TEXT } },
  { text: 'Q2-2026 WI Allowable', options: { color: TEXT, fontFace: 'Consolas' } },
  { text: '. Inactive strings booked at 3,920 BOPD.', options: { color: TEXT } }
], { x: M, y: 5.85, w: W - 2*M, h: 0.40,
     fontFace: FONT_BODY, fontSize: 10, color: TEXT });

// Mini KPI strip
const kpiX = M, kpiY = 6.30, kpiW = (W - 2*M) / 4;
const mkpi = [
  ['Gap vs TR',     '4,250 BOPD', OIL],
  ['Under-WI',      '18,000 bwpd', WATER],
  ['Wells classed', '124 active', TEAL],
  ['Inactive booked','3,920 BOPD', MINT],
];
mkpi.forEach((k, i) => {
  const x = kpiX + i * kpiW;
  s3.addShape(pres.ShapeType.rect, { x, y: kpiY, w: kpiW - 0.1, h: 0.65,
    fill: { color: 'FFFFFF' }, line: { color: k[2], width: 0.7 } });
  s3.addText(k[0], { x: x + 0.1, y: kpiY + 0.05, w: kpiW - 0.3, h: 0.22,
    fontFace: FONT_BODY, fontSize: 9, color: SUB, charSpacing: 0.8 });
  s3.addText(k[1], { x: x + 0.1, y: kpiY + 0.25, w: kpiW - 0.3, h: 0.38,
    fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY });
});

// ----------------------------------------------------------------
// 4. BOTTLENECK MAP
const s4 = pres.addSlide();
addBase(s4, 'Bottleneck map — 9 root causes from RM comments', { section: '§ Classification', page: '4 / 12' });

const catRows = [
  ['S1', 'Low PIP / stim candidate',                'Subsurface',         '36', '~12,000', '§4.1'],
  ['S2', 'High WC (>60%)',                          'Subsurface',         '55', '~7,000',  '§4.6 + 1.2A'],
  ['S3', 'Low BHFP / close to Pb',                  'Subsurface',         '10', '~1,800',  '§4.2'],
  ['S4', 'Inactive — WO backlog',                   'Subsurface',         '9',  '~3,920',  '§4.8 + 1.1B'],
  ['S5', 'Reservoir P depletion',                   'Subsurface',         '1',  '~5,000',  '§4.5'],
  ['C1', 'Low ΔP choke / VSD req.',                 'Surface/Completion', '17', '~6,500',  '§4.3'],
  ['C2', 'ESP at max frequency',                    'Completion',         '13', '~3,500',  '§4.4'],
  ['C3', 'Surface back-pressure (proxy)',           'Surface',            '12', 'TBD',     '§4.7'],
  ['W1', 'Cluster cap 25/26 Mbwpd',                 'Water Injection',    '—',  '—',       '§4.5 Ph2'],
  ['W2', 'WI integrity (SY-175, SY-180)',           'Water Injection',    '2',  '16k bwpd', '§4.5 Ph1'],
  ['W3', 'R1↔R2 inter-reservoir loss',             'Water Injection',    '2',  '—',       '§4.6 (a)'],
  ['W4', 'High-WC producers loading PW',            'Water Injection',    '13', '—',       '§4.6 (c)'],
];
const grpColor = g => g.includes('Water') ? WATER : g.includes('Surface') ? OIL : g === 'Completion' ? DEEP : MINT;
const head = ['ID', 'Category', 'Group', 'Wells', 'BOPD lost', 'Opp.'];
const tbl = [ head.map(h => ({ text: h, options: {
  fontFace: FONT_BODY, fontSize: 10, bold: true, color: 'FFFFFF',
  fill: { color: DEEP }, align: 'center', valign: 'middle'
}})) ].concat(catRows.map((r, ri) => r.map((c, ci) => ({
  text: c,
  options: {
    fontFace: FONT_BODY, fontSize: 10,
    bold: ci === 0,
    color: ci === 2 ? grpColor(c) : TEXT,
    fill: { color: ri % 2 === 0 ? BG : 'FFFFFF' },
    align: ci === 3 || ci === 4 ? 'right' : (ci === 0 ? 'center' : 'left'),
    valign: 'middle'
  }
}))));
s4.addTable(tbl, {
  x: M, y: 0.78, w: 7.6,
  colW: [0.55, 2.55, 1.65, 0.75, 1.05, 1.05],
  rowH: 0.30, border: { type: 'solid', pt: 0.5, color: LINE }
});

// Side panel — wells chart
s4.addText('Wells per category', { x: 8.4, y: 0.78, w: 4.4, h: 0.28,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: SUB, charSpacing: 1 });
s4.addChart(pres.ChartType.bar, [
  { name: 'wells',
    labels: catRows.map(r => r[0]),
    values: catRows.map(r => parseInt(r[3]) || 0)
  }
], {
  x: 8.4, y: 1.10, w: 4.5, h: 3.4,
  chartColors: catRows.map(r => grpColor(r[2])),
  barDir: 'bar', showLegend: false, showValue: true,
  dataLabelFontSize: 9, dataLabelColor: TEXT,
  catAxisLabelFontSize: 9, valAxisLabelFontSize: 8,
  plotArea: { fill: { color: 'FFFFFF' } }
});

// Bottom takeaway band
band(s4, M, 5.50, W - 2*M, 0.40, NAVY,
  '8 producer-side categories + 4 WI-side categories. Strings can fall into multiple categories — counts are not mutually exclusive.',
  'FFFFFF', 11);
s4.addText([
  { text: 'Highest-leverage category: ', options: { bold: true, color: NAVY } },
  { text: 'S1 (stim candidates) at 36 wells × ~12,000 BOPD lost vs SH cap; addressed by §4.1 (Obj 1.1C extension) + selective §4.2 work. ', options: { color: TEXT } },
  { text: 'Surface category C3 ', options: { bold: true, color: OIL } },
  { text: '(back-pressure proxy) is unquantified pending the Jan-2026 FCT report — represents the largest analytical uncertainty.', options: { color: TEXT } }
], { x: M, y: 6.05, w: W - 2*M, h: 0.85,
     fontFace: FONT_BODY, fontSize: 11, color: TEXT, valign: 'top' });

// ----------------------------------------------------------------
// 5. CATEGORY QUANTIFICATION (concept-equivalent of "PI Decline Ranking" — bottleneck stack)
const s5 = pres.addSlide();
addBase(s5, 'Bottleneck stack — wells & BOPD lost by category', { section: '§ Quantification', page: '5 / 12' });

s5.addText('Where the 4,250 BOPD TR-gap (+ further upside) comes from', {
  x: M, y: 0.70, w: 9, h: 0.35,
  fontFace: FONT_HEAD, italic: true, fontSize: 13, color: SUB });

// BOPD lost chart
s5.addChart(pres.ChartType.bar, [
  { name: 'BOPD lost vs SH cap',
    labels: ['S1 stim', 'S2 high WC', 'S3 low BHFP', 'S4 inactive', 'S5 depletion', 'C1 VSD req', 'C2 ESP max', 'C3 back-pres.'],
    values: [12000, 7000, 1800, 3920, 5000, 6500, 3500, 3000] }
], {
  x: M, y: 1.20, w: 7.5, h: 4.7,
  chartColors: [MINT, WATER, OIL, GOOD, TEAL, OIL, DEEP, BAD],
  barDir: 'bar', showLegend: false, showValue: true,
  dataLabelFontSize: 10, dataLabelColor: TEXT,
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
  showTitle: false, plotArea: { fill: { color: 'FFFFFF' } }
});
s5.addText('* C3 surface back-pressure is a midpoint proxy (2,000-4,000 BOPD), pending FCT',
  { x: M, y: 5.95, w: 7.5, h: 0.30,
    fontFace: FONT_BODY, italic: true, fontSize: 9, color: SUB });

// right side — categorical map
const sx = 8.4, syy = 1.10;
band(s5, sx, syy, 4.45, 0.36, NAVY, 'CATEGORY → OPPORTUNITY MAP', 'FFFFFF', 10);
const mapRows = [
  ['S1 + S3', '→ §4.1 stim + §4.2 BHFP', MINT],
  ['S2 + W4', '→ §4.6 PW redistribution', WATER],
  ['S4',      '→ §4.8 reactivation accel.', GOOD],
  ['S5 + W1-3','→ §4.5 WI capacity uplift', TEAL],
  ['C1',      '→ §4.3 VSD/PWS retrofit', DEEP],
  ['C2',      '→ §4.4 ESP upsize', INK],
  ['C3',      '→ §4.7 back-pressure (FCT)', OIL],
];
mapRows.forEach((r, i) => {
  const ry = syy + 0.55 + i * 0.55;
  s5.addShape(pres.ShapeType.rect, { x: sx, y: ry, w: 4.45, h: 0.50,
    fill: { color: 'FFFFFF' }, line: { color: LINE, width: 0.4 } });
  s5.addShape(pres.ShapeType.rect, { x: sx, y: ry, w: 0.08, h: 0.50,
    fill: { color: r[2] }, line: { type: 'none' } });
  s5.addText(r[0], { x: sx + 0.18, y: ry + 0.05, w: 1.5, h: 0.42,
    fontFace: FONT_BODY, fontSize: 11, bold: true, color: NAVY, valign: 'middle' });
  s5.addText(r[1], { x: sx + 1.7, y: ry + 0.05, w: 2.7, h: 0.42,
    fontFace: FONT_BODY, fontSize: 10.5, color: TEXT, valign: 'middle' });
});

// bottom callout
band(s5, M, 6.40, W - 2*M, 0.40, OIL,
  'Each Allowable RM-comment row maps to ≥1 category. 124 strings → ~210 category hits → 8 quantified opportunities.',
  INK, 11);

// ----------------------------------------------------------------
// Helper for opportunity deep-dive slides
function opportunitySlide(id, num, opp, page) {
  const s = pres.addSlide();
  addBase(s, `§${opp.id} — ${opp.title}`, { section: `Deep-dive ${num}/4`, page: `${page} / 12` });
  s.addText(opp.category + ' · Confidence: ' + opp.conf, {
    x: M, y: 0.72, w: 10, h: 0.34,
    fontFace: FONT_HEAD, italic: true, fontSize: 13, color: SUB });

  // LEFT — 3 KPI cards
  const cx = M, cy = 1.20, cw = 3.20, ch = 1.55;
  const kpis = [
    ['2026 realistic gain', opp.lo === opp.hi ? `+${opp.lo.toLocaleString()} BOPD` : `+${opp.lo.toLocaleString()}–${opp.hi.toLocaleString()} BOPD`, MINT],
    ['Full potential',      opp.full_lo === opp.full_hi ? `+${opp.full_lo.toLocaleString()} BOPD` : `+${opp.full_lo.toLocaleString()}–${opp.full_hi.toLocaleString()} BOPD`, TEAL],
    ['Capex bracket',       `$${opp.capex_lo}–${opp.capex_hi}M`, OIL],
  ];
  kpis.forEach((k, i) => {
    const y = cy + i * (ch + 0.18);
    s.addShape(pres.ShapeType.rect, { x: cx, y, w: cw, h: ch,
      fill: { color: 'FFFFFF' }, line: { color: LINE, width: 0.5 } });
    s.addShape(pres.ShapeType.rect, { x: cx, y, w: 0.06, h: ch,
      fill: { color: k[2] }, line: { type: 'none' } });
    s.addText(k[0].toUpperCase(), { x: cx + 0.18, y: y + 0.12, w: cw - 0.3, h: 0.30,
      fontFace: FONT_BODY, fontSize: 10, color: SUB, charSpacing: 1, bold: true });
    s.addText(k[1], { x: cx + 0.18, y: y + 0.42, w: cw - 0.3, h: 0.95,
      fontFace: FONT_HEAD, fontSize: 22, bold: true, color: NAVY, valign: 'top' });
  });

  // RIGHT — story
  const rx = cx + cw + 0.45, rw = W - rx - M;
  s.addText('MECHANISM', { x: rx, y: 1.20, w: rw, h: 0.32,
    fontFace: FONT_BODY, fontSize: 11, bold: true, color: OIL, charSpacing: 1 });
  s.addShape(pres.ShapeType.line, { x: rx, y: 1.52, w: rw, h: 0,
    line: { color: OIL, width: 0.8 } });
  s.addText(opp.mech, { x: rx, y: 1.62, w: rw, h: 2.8,
    fontFace: FONT_BODY, fontSize: 12, color: TEXT, valign: 'top', paraSpaceAfter: 6 });

  s.addText('PREREQUISITE DATA / WORK', { x: rx, y: 4.55, w: rw, h: 0.32,
    fontFace: FONT_BODY, fontSize: 11, bold: true, color: OIL, charSpacing: 1 });
  s.addShape(pres.ShapeType.line, { x: rx, y: 4.87, w: rw, h: 0,
    line: { color: OIL, width: 0.8 } });
  s.addText(opp.prereq, { x: rx, y: 4.97, w: rw, h: 1.3,
    fontFace: FONT_BODY, fontSize: 11.5, color: TEXT, valign: 'top' });

  // Bottom recommendation band
  band(s, M, 6.40, W - 2*M, 0.40, NAVY, 'RECOMMENDATION  ·  ' + opp.reco, 'FFFFFF', 11);
}

const OPP_DETAILS = {
  '4.5': {
    id: '4.5', title: 'WI capacity uplift (SY-175 + SY-180 + cluster review)',
    category: 'Subsurface / Water Injection', conf: 'Med-High',
    lo: 2500, hi: 4000, full_lo: 4000, full_hi: 5500,
    capex_lo: 2.0, capex_hi: 28.0,
    mech: 'Phase 1 (Q2/Q3-2026): complete the WO on SY-175 + SY-180 to recover 16,000 bwpd of stranded injection capacity. RM warns to run an FCT in Cluster #2 / SY-148 WS before SY-180 commissioning (current 19,000 bwpd vs 28,800 bwpd technical).\n\nPhase 2 (2027): Cluster #2 capacity uplift study if FCT confirms 26 Mbwpd ceiling — evaluate manifold/pump capacity addition to 35 Mbwpd.\n\nPhase 3: new WI well drilling if reservoir VRR analysis confirms incremental voidage to fill. Saih Rawl analog (SPE 68222): +12% oil rate per +30% WI rate at mature waterflood.',
    prereq: 'Cluster #2 / SY-148 WS FCT (RM-mandated before SY-180 commissioning) · G2V2 ML#5 reservoir forecast · sector VRR breakdown',
    reco: 'Front-load Phase 1 in Q2/Q3-2026 — single largest 2026 gain ($2-3M capex, +2,500-4,000 BOPD). Phase 2 conditional on FCT outcome.'
  },
  '4.7': {
    id: '4.7', title: 'Surface back-pressure optimization',
    category: 'Surface · KoM focus area', conf: 'Medium',
    lo: 1500, hi: 2500, full_lo: 2300, full_hi: 3300,
    capex_lo: 0.2, capex_hi: 8.0,
    mech: 'KoM explicit ask — proxy indicators from Allowable: wells at full choke, ESP at 50 Hz with rate plateauing (downstream restriction); WHFT 150-162°F (high flowline pressure); non-uniform separator pressure.\n\nPhase 1: station header setpoint review (CDS / RDS-1 / RDS-2). Each 10 psi separator cut ≈ +800 BOPD across 80 R1 producers.\nPhase 2: flowline looping on 2-3 worst segments (>200 psi/km ΔP).\nPhase 3: choke-on-test vs production-choke bias alignment.',
    prereq: 'January-2026 FCT report (BLOCKING) · GAP/Prosper IPM surface model · WHIP/WHFP-vs-time per well · CDS/RDS PFD & PIDs',
    reco: 'Phase 1 ($0.2M control changes) achievable in <90 days once FCT lands. Surface CapEx slate for Phase 2 to be scoped after Q3-2026 WS.'
  },
  '4.6': {
    id: '4.6', title: 'Produced-water redistribution + R1↔R2 rebalancing',
    category: 'Subsurface / WI', conf: 'Medium',
    lo: 2000, hi: 2400, full_lo: 2400, full_hi: 3200,
    capex_lo: 0.5, capex_hi: 1.5,
    mech: '(a) Tracer + integrity diagnosis on 139-SS & 145-SS — RM flagged "Water loss to R2 likely occurring due to communication between reservoir units". Confirm with chemical tracers, remediate with cement squeeze if zonal isolation lost.\n\n(b) Rebalance 3,000-5,000 bwpd from R2 → R1 (R2 receives 27,000 vs 34,500 target; R1-C only at 18,000 vs 20,500 target).\n\n(c) Selective shut-in / rate reduction on 6 worst >85% WC producers — frees ~20,000 bwpd PW capacity, improves sector VRR.',
    prereq: 'PW lab analysis (TDS, scaling, particulates, H₂S) · injector PLT/CBL on 139-SS and 145-SS · G2V2 rerun with re-balanced injection',
    reco: 'Low-cost / high-leverage. Sequence tracer campaign Q3-2026 — integrity findings drive cement-squeeze scope.'
  },
  '4.1': {
    id: '4.1', title: 'Stimulation roll-out beyond Obj 1.1C',
    category: 'Subsurface', conf: 'Medium',
    lo: 2500, hi: 2500, full_lo: 5000, full_hi: 6000,
    capex_lo: 8.0, capex_hi: 12.0,
    mech: '32+ R1 strings flagged "Low intake / Low PIP / stim required" by RM. Obj 1.1C scopes only 5. Apply proven Naphtha + HCl recipe to 8-10 additional R1 wells per year as a sustained program.\n\nTarget wells with PI degradation D > 30%/yr (extend the 1.1C dashboard methodology). Average gain +150-400 BOPD per well, 30%/yr decline post-job. Backlog of 25 candidates × 250 BOPD avg ≈ +6,000 BOPD at peak.',
    prereq: 'Per-well PI screening across 32 stim candidates (1.1C dashboard extension) · workover-rig availability schedule',
    reco: 'Commission 10-well stim program for Q3-2026 → Q4-2027. Coordinate with Obj 1.1C to avoid double-counting the 5 wells already in plan.'
  }
};

// 6-9. Top-4 opportunity deep-dives
opportunitySlide(1, 1, OPP_DETAILS['4.5'], 6);
opportunitySlide(2, 2, OPP_DETAILS['4.7'], 7);
opportunitySlide(3, 3, OPP_DETAILS['4.6'], 8);
opportunitySlide(4, 4, OPP_DETAILS['4.1'], 9);

// ----------------------------------------------------------------
// 10. CONSOLIDATED RANKING + GAIN BRIDGE
const s10 = pres.addSlide();
addBase(s10, 'Consolidated ranking & gain bridge', { section: '§ Roadmap', page: '10 / 12' });

// LEFT — ranking table
const rankRows = [
  ['1', '§4.5 WI capacity (SY-175/180 + cluster)', '+2,500–4,000', '+4,000–5,500', 'M-H', '$$'],
  ['2', '§4.7 Surface back-pressure',              '+1,500–2,500', '+2,300–3,300', 'M',   '$ → $$$'],
  ['3', '§4.6 PW redistribution + R1/R2',          '+2,000',       '+2,400–3,200', 'M',   '$'],
  ['4', '§4.1 Stim roll-out beyond 1.1C',          '+2,500',       '+5,000–6,000', 'M',   '$$$'],
  ['5', '§4.3 VSD/PWS retrofit',                   '+1,600',       '+3,300–5,500', 'H',   '$$'],
  ['6', '§4.4 ESP upsize (piggyback WO)',          '+800',         '+2,800',       'M',   '$$'],
  ['7', '§4.2 BHFP cap relaxation',                '+900',         '+1,800',       'M-H', 'low'],
  ['8', '§4.8 Inactive-string reactivation',       '+1,000',       'booked in TR', 'H',   'low'],
];
const rankHead = ['#', 'Opportunity', '2026 realistic', 'Full pot.', 'Conf', 'Capex'];
const tbl10 = [ rankHead.map(h => ({ text: h, options: {
  fontFace: FONT_BODY, fontSize: 10, bold: true, color: 'FFFFFF',
  fill: { color: DEEP }, align: 'center', valign: 'middle'
}})) ].concat(rankRows.map((r, ri) => r.map((c, ci) => ({
  text: c,
  options: {
    fontFace: FONT_BODY, fontSize: 10,
    bold: ci === 0 || ci === 1,
    color: ci === 4 ? (c === 'H' ? GOOD : c === 'M-H' ? OIL : BAD) : TEXT,
    fill: { color: ri % 2 === 0 ? BG : 'FFFFFF' },
    align: ci === 0 || ci === 4 ? 'center' : (ci >= 2 ? 'right' : 'left'),
    valign: 'middle'
  }
}))));
s10.addTable(tbl10, {
  x: M, y: 0.80, w: 7.4,
  colW: [0.35, 2.65, 1.45, 1.35, 0.65, 0.95],
  rowH: 0.34, border: { type: 'solid', pt: 0.5, color: LINE }
});

// RIGHT — gain bridge chart
s10.addText('GAIN BRIDGE — current → 2026 envelope', { x: 8.10, y: 0.78, w: 4.8, h: 0.32,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: SUB, charSpacing: 1 });

const overlap = ['4.1', '4.3', '4.4'];
const ordered = [
  ['Start', '4.5', '4.1', '4.7', '4.3', '4.6', '4.8', '4.2', '4.4', 'End'],
];
// Build cumulative
const incrLookup = {
  '4.5': 2500, '4.7': 1500, '4.6': 2000, '4.1': 2500, '4.3': 1600,
  '4.4': 800, '4.2': 900, '4.8': 1000
};
let cum = 75733;
const labels = ['Start'];
const cumValues = [cum];
[['4.5', 2500], ['4.7', 1500], ['4.6', 2000], ['4.1', 2500], ['4.3', 1600],
 ['4.6', 0], // placeholder; we'll redo cleaner
].length;
// Cleaner: use ranking order
const seq = [
  ['§4.5', 2500],
  ['§4.7', 1500],
  ['§4.6', 2000],
  ['§4.1', Math.round(2500 * 0.75)],
  ['§4.3', Math.round(1600 * 0.75)],
  ['§4.4', Math.round(800 * 0.75)],
  ['§4.2', 900],
  ['§4.8', 1000],
];
const bridgeLabels = ['Start'];
const bridgeCum = [75733];
let c = 75733;
seq.forEach(([k, v]) => { bridgeLabels.push(k); c += v; bridgeCum.push(c); });
bridgeLabels.push('Envelope');
bridgeCum.push(c);

s10.addChart(pres.ChartType.line, [
  { name: 'Cumulative BOPD',
    labels: bridgeLabels,
    values: bridgeCum }
], {
  x: 8.10, y: 1.12, w: 4.9, h: 4.55,
  chartColors: [OIL],
  lineSize: 2.5,
  showLegend: false, showValue: true,
  dataLabelFontSize: 8, dataLabelColor: NAVY,
  catAxisLabelFontSize: 9, valAxisLabelFontSize: 9,
  valAxisMinVal: 75000,
  plotArea: { fill: { color: 'FFFFFF' } }
});

// envelope band
band(s10, M, 5.80, W - 2*M, 0.42, OIL,
  `2026 realistic envelope (after 25% overlap deduction on §4.1+§4.3+§4.4): ${(bridgeCum[bridgeCum.length-1] - 75733).toLocaleString()} BOPD uplift → ${bridgeCum[bridgeCum.length-1].toLocaleString()} BOPD total (+${Math.round((bridgeCum[bridgeCum.length-1]-75733)/75733*100)}%)`,
  INK, 12);
s10.addText('Comparable to Saih Rawl Shuaiba debottlenecking (SPE 68222 analog): +6,300 BOPD on a smaller system via choke automation + WI redistribution.',
  { x: M, y: 6.30, w: W - 2*M, h: 0.40,
    fontFace: FONT_BODY, italic: true, fontSize: 11, color: SUB });

// ----------------------------------------------------------------
// 11. DATA GAPS + NEXT STEPS
const s11 = pres.addSlide();
addBase(s11, 'Data gaps & next steps', { section: '§ Roadmap', page: '11 / 12' });

// LEFT — gap list
s11.addText('9 CRITICAL DATA ITEMS REQUIRED', { x: M, y: 0.78, w: 7, h: 0.32,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: OIL, charSpacing: 1 });
const gaps = [
  ['1', 'January-2026 FCT report',           'Blocking §4.7'],
  ['2', 'GAP/Prosper IPM surface model',     'Blocking §4.7 & §4.2'],
  ['3', 'G2V2 reservoir model — ML#5',       'Blocking §4.5 & §4.6 oil response'],
  ['4', 'Cluster #2 / SY-148 WS FCT',        'Blocking SY-180 commissioning'],
  ['5', 'PIDs / PFDs / vendor capacity',     'CDS, RDS-1, RDS-2, WI clusters'],
  ['6', 'Produced water lab analysis',       'TDS, scaling, particulates, H₂S'],
  ['7', 'WHIP/WHFP-vs-time per well',        '§4.7 validation'],
  ['8', 'Injector PLT/CBL (139-SS, 145-SS)', '§4.6 (a) integrity hypothesis'],
  ['9', 'Per-well PI screening (32 cands.)', '§4.1 scoping'],
];
const gh = ['#', 'Item', 'Why'];
const gtab = [ gh.map(h => ({ text: h, options: {
  fontFace: FONT_BODY, fontSize: 10, bold: true, color: 'FFFFFF',
  fill: { color: DEEP }, align: 'center', valign: 'middle'
}})) ].concat(gaps.map((r, ri) => r.map((c, ci) => ({
  text: c,
  options: {
    fontFace: FONT_BODY, fontSize: 10,
    bold: ci === 1,
    color: ri < 4 ? BAD : TEXT,
    fill: { color: ri % 2 === 0 ? BG : 'FFFFFF' },
    align: ci === 0 ? 'center' : 'left',
    valign: 'middle'
  }
}))));
s11.addTable(gtab, {
  x: M, y: 1.18, w: 7.0,
  colW: [0.40, 3.40, 3.20],
  rowH: 0.34, border: { type: 'solid', pt: 0.5, color: LINE }
});

// RIGHT — timeline strip
s11.addText('TIMELINE — NEXT 90 DAYS', { x: 7.7, y: 0.78, w: 5.2, h: 0.32,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: OIL, charSpacing: 1 });
// Use inner geometry so first & last labels don't fall off the slide
const tlOuterX = 7.7, tlOuterW = 5.20, tlInsetX = 0.75; // inset on each side
const tlx = tlOuterX + tlInsetX, tly = 1.18, tlw = tlOuterW - 2 * tlInsetX;
// rail
s11.addShape(pres.ShapeType.rect, { x: tlx, y: tly + 0.30, w: tlw, h: 0.06,
  fill: { color: NAVY }, line: { type: 'none' } });
const ts = [
  ['Now',    'Pull FCT\n+ PIDs', OIL],
  ['+30 d',  'Per-well PI\nscreen (§4.1)', MINT],
  ['+60 d',  'GAP/Prosper\nrerun', TEAL],
  ['+90 d',  'Q3 Technical\nWorkshop', BAD],
];
ts.forEach((t, i) => {
  const x = tlx + i * (tlw / (ts.length - 1));
  s11.addShape(pres.ShapeType.ellipse, { x: x - 0.15, y: tly + 0.20, w: 0.30, h: 0.30,
    fill: { color: t[2] }, line: { color: NAVY, width: 1 } });
  s11.addText(t[0], { x: x - 0.60, y: tly + 0.55, w: 1.20, h: 0.30,
    fontFace: FONT_BODY, fontSize: 10, color: SUB, align: 'center', bold: true });
  s11.addText(t[1], { x: x - 0.70, y: tly + 0.85, w: 1.40, h: 0.85,
    fontFace: FONT_BODY, fontSize: 10, color: TEXT, align: 'center', valign: 'top' });
});

// Workshop block — uses full tlOuterW for breathing room; extended height so bullets don't overflow
s11.addShape(pres.ShapeType.rect, { x: tlOuterX, y: 3.10, w: tlOuterW, h: 3.20,
  fill: { color: 'FFFFFF' }, line: { color: LINE, width: 0.5 } });
s11.addShape(pres.ShapeType.rect, { x: tlOuterX, y: 3.10, w: tlOuterW, h: 0.06,
  fill: { color: OIL }, line: { type: 'none' } });
s11.addText('Q3-2026 Technical WS — agenda highlights', { x: tlOuterX + 0.15, y: 3.20, w: tlOuterW - 0.3, h: 0.36,
  fontFace: FONT_HEAD, fontSize: 13, bold: true, color: NAVY });
s11.addText([
  'Validate the 9-category bottleneck map vs AON internal view',
  'Approve §4.3 VSD retrofit shortlist & 2026 execution sequence',
  'Confirm FCT findings; align on §4.7 surface back-pressure priorities',
  'Decide §4.6 tracer campaign scope (139-SS, 145-SS first)',
  'Cross-reference §4.1 stim backlog with Obj 1.1C selected 5',
  'Sign off opportunity list with executive owners per item',
].map(t => ({ text: t, options: { bullet: { code: '25AA' } } })),
  { x: tlOuterX + 0.25, y: 3.60, w: tlOuterW - 0.50, h: 2.55,
    fontFace: FONT_BODY, fontSize: 10.5, color: TEXT, paraSpaceAfter: 4, valign: 'top' });

// Bottom callout
band(s11, M, 6.40, W - 2*M, 0.40, NAVY,
  'Items #1–4 are blockers for tightening the §4.5 and §4.7 estimates — the two largest 2026 opportunities.',
  'FFFFFF', 11);

// ----------------------------------------------------------------
// 12. CONCLUSIONS
const s12 = pres.addSlide();
s12.background = { color: NAVY };
s12.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.55,
  fill: { color: NAVY }, line: { type: 'none' } });
s12.addShape(pres.ShapeType.rect, { x: 0, y: 0.55, w: W, h: 0.04,
  fill: { color: OIL }, line: { type: 'none' } });
s12.addText('Conclusions', {
  x: M, y: 0.05, w: W - 2*M, h: 0.45,
  fontFace: FONT_HEAD, fontSize: 22, bold: true, color: 'FFFFFF', valign: 'middle' });
s12.addText('PC26 · Obj 1.1D · Shah De-Bottlenecking', {
  x: W - M - 4, y: 0.05, w: 3.9, h: 0.45,
  fontFace: FONT_BODY, fontSize: 11, color: OIL_S, align: 'right', valign: 'middle' });

// 5 numbered findings, two columns
const concl = [
  ['1', 'Field is under-delivering TR by 4,250 BOPD (5.6%) — bottleneck spread across subsurface (60%) and surface/WI (40%).'],
  ['2', '2026 realistic uplift envelope is +10,000–12,000 BOPD (+13%), comparable to Saih Rawl Shuaiba (SPE 68222) outcome.'],
  ['3', 'Largest single 2026 lever is §4.5 WI capacity uplift (SY-175/180 + Cluster #2): +2,500–4,000 BOPD at $2–3M Phase 1 capex.'],
  ['4', 'Highest-confidence quick win is §4.3 VSD/PWS retrofit: +1,600 BOPD at $2.4–4.8M, mechanism proven on 10 Shah wells.'],
  ['5', 'Final quantification blocked by 4 data items — Jan-2026 FCT report is the single most important data request.'],
];
const cw2 = (W - 2*M) / 2 - 0.20, ch2 = 1.10;
concl.forEach((f, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = M + col * (cw2 + 0.40);
  const y = 1.00 + row * (ch2 + 0.30);
  s12.addShape(pres.ShapeType.roundRect, { x, y, w: cw2, h: ch2,
    fill: { color: '0F1B2E' }, line: { color: OIL, width: 0.4 }, rectRadius: 0.04 });
  s12.addShape(pres.ShapeType.ellipse, { x: x + 0.15, y: y + 0.15, w: 0.65, h: 0.65,
    fill: { color: OIL }, line: { type: 'none' } });
  s12.addText(f[0], { x: x + 0.15, y: y + 0.15, w: 0.65, h: 0.65,
    fontFace: FONT_HEAD, fontSize: 22, bold: true, color: NAVY,
    align: 'center', valign: 'middle' });
  s12.addText(f[1], { x: x + 0.95, y: y + 0.12, w: cw2 - 1.10, h: ch2 - 0.20,
    fontFace: FONT_BODY, fontSize: 12.5, color: 'F5F7FA', valign: 'middle' });
});

// 5th finding spans the bottom (only 5 items; row 2 has 2; row 3 has 1, centered)
// We rendered finding #5 at i=4 -> row=2, col=0 — fine, leaves right column empty for breathing room.

// closing band
s12.addShape(pres.ShapeType.rect, { x: 0, y: H - 0.65, w: W, h: 0.65,
  fill: { color: '08182B' }, line: { type: 'none' } });
s12.addShape(pres.ShapeType.rect, { x: 0, y: H - 0.65, w: W, h: 0.04,
  fill: { color: OIL }, line: { type: 'none' } });
s12.addText('Next checkpoint: Q3-2026 Technical Workshop — opportunity sign-off + owner assignment', {
  x: M, y: H - 0.55, w: W - 2*M, h: 0.45,
  fontFace: FONT_HEAD, italic: true, fontSize: 13, color: OIL_S, valign: 'middle' });

// ----------------------------------------------------------------
pres.writeFile({ fileName: '/home/user/pc26_1_1D/deliverables/PC26_1.1D_Debottlenecking.pptx' })
   .then(f => console.log('Wrote ' + f));
