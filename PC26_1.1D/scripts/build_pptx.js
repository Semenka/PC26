// PC26 Obj 1.1D — Shah Field De-Bottlenecking deck
// LAYOUT_WIDE (13.3 x 7.5)  ·  pptxgenjs
const PptxGenJS = require('/opt/node22/lib/node_modules/pptxgenjs');
const path = require('path');

const OUT = path.join(__dirname, '..', 'deliverables', 'PC26_1.1D_Debottlenecking.pptx');

const pres = new PptxGenJS();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pres.author = 'TotalEnergies ALSG × ADNOC Onshore';
pres.title  = 'Shah Field De-Bottlenecking — PC26 Obj 1.1D';
pres.subject = 'PC26 1.1D';

// ---------- palette ----------
const C = {
  navy:    '0A2540', deep:    '1E3A5F',
  oil:     'F59E0B', teal:    '0891B2', mint: '34D399', water: '06B6D4',
  bg:      'FFFFFF', bgDark:  '0A2540', panel: 'F8FAFC', line: 'CBD5E1',
  text:    '0F172A', sub:     '64748B', dim: '94A3B8',
  good:    '16A34A', warn:    'F59E0B', bad: 'DC2626',
};
const F = { head: 'Georgia', body: 'Calibri', mono: 'Consolas' };

// ---------- helpers ----------
function pageFrame(slide, opts) {
  slide.background = { color: C.bg };
  // Top oil rule
  slide.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: C.oil }, line: { color: C.oil } });
  // Header band navy
  slide.addShape(pres.ShapeType.rect, { x: 0, y: 0.08, w: 13.333, h: 0.55, fill: { color: C.navy }, line: { color: C.navy } });
  slide.addText(opts.eyebrow || 'PC26 · OBJ 1.1D', {
    x: 0.4, y: 0.13, w: 4, h: 0.25,
    fontFace: F.mono, fontSize: 9, color: C.oil, bold: true, charSpacing: 2
  });
  slide.addText(opts.title || '', {
    x: 0.4, y: 0.32, w: 12.6, h: 0.32,
    fontFace: F.head, fontSize: 18, color: 'FFFFFF', bold: true
  });
  // Footer
  slide.addShape(pres.ShapeType.line, { x: 0.4, y: 7.18, w: 12.5, h: 0, line: { color: C.line, width: 0.5 } });
  slide.addText('Shah Field De-Bottlenecking · TotalEnergies ALSG × ADNOC Onshore · 2026-04-23', {
    x: 0.4, y: 7.22, w: 9, h: 0.22, fontFace: F.mono, fontSize: 8, color: C.sub
  });
  slide.addText(opts.page || '', {
    x: 12.0, y: 7.22, w: 0.9, h: 0.22, fontFace: F.mono, fontSize: 8, color: C.sub, align: 'right'
  });
}

function kpiCard(slide, x, y, w, h, label, value, unit, accent) {
  accent = accent || C.oil;
  slide.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: C.panel }, line: { color: C.line, width: 0.5 } });
  slide.addShape(pres.ShapeType.rect, { x, y, w: 0.05, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(label, { x: x+0.15, y: y+0.1, w: w-0.2, h: 0.25,
    fontFace: F.mono, fontSize: 8, color: C.sub, bold: true, charSpacing: 1 });
  slide.addText(value, { x: x+0.15, y: y+0.32, w: w-0.2, h: h-0.55,
    fontFace: F.mono, fontSize: h > 1.4 ? 28 : 22, bold: true, color: C.text });
  if (unit) slide.addText(unit, { x: x+0.15, y: y+h-0.32, w: w-0.2, h: 0.22,
    fontFace: F.body, fontSize: 10, color: C.sub });
}

function sectionTitle(slide, x, y, w, txt, color) {
  slide.addText(txt, { x, y, w, h: 0.3,
    fontFace: F.mono, fontSize: 10, color: color || C.oil, bold: true, charSpacing: 1 });
  slide.addShape(pres.ShapeType.rect, { x, y: y + 0.32, w: 0.4, h: 0.025,
    fill: { color: color || C.oil }, line: { color: color || C.oil } });
}

// ============================================================
// SLIDE 1 — TITLE
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  // Oil rule
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: C.oil }, line: { color: C.oil } });
  // Vertical oil accent
  s.addShape(pres.ShapeType.rect, { x: 0.8, y: 1.5, w: 0.06, h: 4.5, fill: { color: C.oil }, line: { color: C.oil } });
  s.addText('PC26 · OBJECTIVE 1.1D', { x: 1.1, y: 1.6, w: 8, h: 0.3,
    fontFace: F.mono, fontSize: 12, color: C.oil, bold: true, charSpacing: 4 });
  s.addText('Shah Field\nDe-Bottlenecking', { x: 1.1, y: 2.0, w: 8.3, h: 2.0,
    fontFace: F.head, fontSize: 40, color: 'FFFFFF', bold: true, lineSpacingMultiple: 1.0 });
  s.addText('Quantified opportunity catalogue — surface,\nsubsurface & water injection', {
    x: 1.1, y: 4.1, w: 8.3, h: 0.9, fontFace: F.head, italic: true, fontSize: 17, color: C.dim, lineSpacingMultiple: 1.15 });
  s.addText('TotalEnergies ALSG × ADNOC Onshore', { x: 1.1, y: 5.3, w: 6, h: 0.3,
    fontFace: F.body, fontSize: 14, color: 'FFFFFF' });
  s.addText('Asset Lead FP: Andrey Semenov', { x: 1.1, y: 5.6, w: 6, h: 0.3,
    fontFace: F.body, fontSize: 12, color: C.dim });
  s.addText('Issued 2026-04-23', { x: 1.1, y: 5.95, w: 6, h: 0.3,
    fontFace: F.mono, fontSize: 10, color: C.oil });

  // Right side stats
  const stats = [
    ['CURRENT', '75,733', 'BOPD actual'],
    ['POTENTIAL', '+10–12k', 'BOPD realistic 2026'],
    ['OPPS', '8', 'de-bottlenecking initiatives'],
  ];
  stats.forEach(([lbl, val, sub], i) => {
    const y = 1.7 + i * 1.5;
    s.addText(lbl, { x: 9.6, y, w: 3.2, h: 0.3, fontFace: F.mono, fontSize: 10,
      color: C.oil, bold: true, charSpacing: 2 });
    s.addText(val, { x: 9.6, y: y+0.32, w: 3.2, h: 0.7, fontFace: F.mono, fontSize: 38,
      color: 'FFFFFF', bold: true });
    s.addText(sub, { x: 9.6, y: y+1.0, w: 3.2, h: 0.3, fontFace: F.body, italic: true,
      fontSize: 11, color: C.dim });
  });
  // Bottom credit
  s.addShape(pres.ShapeType.rect, { x: 0, y: 7.3, w: 13.333, h: 0.2, fill: { color: C.oil }, line: { color: C.oil } });
}

// ============================================================
// SLIDE 2 — EXECUTIVE SUMMARY
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Executive Summary', page: '02 / 12', eyebrow: 'OVERVIEW' });

  // 4 KPI strip
  const kpis = [
    { l: 'CURRENT FAR',     v: '75,733', u: 'BOPD actual', a: C.oil },
    { l: '2026 POTENTIAL',  v: '+10–12k', u: 'BOPD realistic', a: C.mint },
    { l: 'OPPORTUNITIES',   v: '8', u: '5 subsurface · 2 surface · 1 cross-cut', a: C.teal },
    { l: 'DATA GAPS',       v: '9', u: 'FCT report + IPM model top of list', a: C.bad },
  ];
  kpis.forEach((k, i) => {
    kpiCard(s, 0.4 + i*3.16, 0.9, 3.0, 1.5, k.l, k.v, k.u, k.a);
  });

  // 3-column key findings
  sectionTitle(s, 0.4, 2.7, 6, 'KEY FINDINGS');
  const findings = [
    { c: C.teal, t: 'SUBSURFACE',
      b: '• ~32 strings flagged "Low PIP / stim required" by RM; 1.1C only covers 5\n• 12 wells rate-capped to keep BHFP ≥ Pb+100 — drawdown headroom\n• Inter-reservoir water loss confirmed on 139-SS & 145-SS\n• R1 under-injected ~5 kbwpd vs sustainable VRR' },
    { c: C.oil, t: 'SURFACE',
      b: '• 22 strings ESP-limited not reservoir-limited (VSD-required)\n• 14 strings already at 55–60 Hz — ESP upsize candidates\n• Surface back-pressure: 10 psi separator reduction ≈ +800 BOPD\n• FCT report pending — biggest tractable upside still unsized' },
    { c: C.water, t: 'WATER INJECTION',
      b: '• SY-175 & SY-180 stranded (16 kbwpd capacity) — WO in plan\n• Currently 53 / 71 kbwpd vs technical rate\n• Cluster #2 hard cap 25/26 Mbwpd binds Phase 2\n• 12 high-WC producers cycle ~40 kbwpd of PW for ~960 BOPD' },
  ];
  findings.forEach((f, i) => {
    const x = 0.4 + i * 4.25;
    s.addShape(pres.ShapeType.rect, { x, y: 3.1, w: 4.1, h: 0.05, fill: { color: f.c }, line: { color: f.c } });
    s.addText(f.t, { x: x+0.1, y: 3.18, w: 4, h: 0.3,
      fontFace: F.mono, fontSize: 10, color: f.c, bold: true, charSpacing: 1.5 });
    s.addText(f.b, { x: x+0.1, y: 3.55, w: 4, h: 3.5, valign: 'top',
      fontFace: F.body, fontSize: 11, color: C.text, lineSpacingMultiple: 1.3 });
  });
}

// ============================================================
// SLIDE 3 — FIELD BASELINE
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Field Baseline — Q2-2026 Allowable', page: '03 / 12', eyebrow: 'BASELINE' });

  // Left: oil chart
  sectionTitle(s, 0.4, 0.9, 6, 'OIL PRODUCTION (BOPD)');
  s.addChart(pres.ChartType.bar, [
    { name: 'BOPD', labels: ['FAR (actual)','Allowable','TR','Allow incl. inactive','Ceiling'],
      values: [75733, 76671, 79983, 80591, 102752] }
  ], {
    x: 0.4, y: 1.3, w: 6.2, h: 4.5,
    chartColors: [C.oil],
    showLegend: false,
    showValue: true, dataLabelFontSize: 10, dataLabelColor: C.text,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
    catAxisLabelColor: C.text, valAxisLabelColor: C.sub,
    barDir: 'bar',
    barGapWidthPct: 40,
  });

  // Right: WI table
  sectionTitle(s, 7.2, 0.9, 6, 'WATER INJECTION (bwpd)');
  const wiRows = [
    [{text:'Scenario',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:10}},
     {text:'Cluster #1',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:10,align:'right'}},
     {text:'Cluster #2',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:10,align:'right'}},
     {text:'Total',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:10,align:'right'}},
     {text:'Actual',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:10,align:'right'}}],
    [{text:'With SY-175 + 180',options:{fontSize:10}},
     {text:'26,000',options:{fontSize:10,align:'right',fontFace:F.mono}},
     {text:'24,600',options:{fontSize:10,align:'right',fontFace:F.mono}},
     {text:'50,600',options:{fontSize:10,align:'right',fontFace:F.mono,bold:true}},
     {text:'—',options:{fontSize:10,align:'right',color:C.sub}}],
    [{text:'Without SY-175/180',options:{fontSize:10,fill:'F1F5F9'}},
     {text:'26,000',options:{fontSize:10,align:'right',fontFace:F.mono,fill:'F1F5F9'}},
     {text:'19,000',options:{fontSize:10,align:'right',fontFace:F.mono,fill:'F1F5F9'}},
     {text:'45,000',options:{fontSize:10,align:'right',fontFace:F.mono,bold:true,fill:'F1F5F9'}},
     {text:'53,000',options:{fontSize:10,align:'right',fontFace:F.mono,color:C.oil,bold:true,fill:'F1F5F9'}}],
    [{text:'Technical rate',options:{fontSize:10}},
     {text:'42,200',options:{fontSize:10,align:'right',fontFace:F.mono}},
     {text:'28,800',options:{fontSize:10,align:'right',fontFace:F.mono}},
     {text:'71,000',options:{fontSize:10,align:'right',fontFace:F.mono,bold:true}},
     {text:'—',options:{fontSize:10,align:'right',color:C.sub}}],
    [{text:'Cluster physical cap',options:{fontSize:10,fill:'F1F5F9',italic:true}},
     {text:'26,000',options:{fontSize:10,align:'right',fontFace:F.mono,fill:'F1F5F9'}},
     {text:'25,000',options:{fontSize:10,align:'right',fontFace:F.mono,fill:'F1F5F9'}},
     {text:'hard cap',options:{fontSize:10,align:'right',fontFace:F.mono,fill:'F1F5F9',color:C.bad,italic:true}},
     {text:'—',options:{fontSize:10,align:'right',color:C.sub,fill:'F1F5F9'}}],
  ];
  s.addTable(wiRows, { x: 7.2, y: 1.3, w: 5.9, colW: [1.9, 0.9, 0.9, 1.1, 1.1],
    border: { type: 'solid', color: C.line, pt: 0.5 }, fontFace: F.body, valign: 'middle' });

  // Bottom commentary band
  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 6.1, w: 12.6, h: 0.95,
    fill: { color: 'FEF3C7' }, line: { color: C.oil, width: 1 } });
  s.addText([
    { text: 'BASELINE READ  ', options: { fontFace: F.mono, fontSize: 9, color: C.oil, bold: true, charSpacing: 1.5 } },
    { text: 'Gap vs TR is 4,250 BOPD (5.6 %). Bigger prize sits between Allowable and the ', options: { fontSize: 11, color: C.text } },
    { text: 'deliverability ceiling of ~102,752 BOPD', options: { fontSize: 11, color: C.text, bold: true } },
    { text: ', which represents the sum of estimated max rates for all active strings — and is unlocked only by capacity uplifts in subsurface and surface infrastructure. WI under-delivery (53 / 71 kbwpd vs technical rate) is the single biggest binding constraint at sector level.', options: { fontSize: 11, color: C.text } },
  ], { x: 0.55, y: 6.18, w: 12.3, h: 0.8 });
}

// ============================================================
// SLIDE 4 — BOTTLENECK MAP
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Bottleneck Map — 9 root-cause categories', page: '04 / 12', eyebrow: 'CLASSIFICATION' });

  sectionTitle(s, 0.4, 0.9, 6, 'BOTTOM-UP FROM RM COMMENT COLUMN');

  // 3-column band: subsurface / surface / WI
  const cols = [
    { x: 0.4, c: C.teal, title: 'SUBSURFACE',
      rows: [
        ['S1', 'Low PIP / stim candidate', '32 wells', '12,000 BOPD'],
        ['S2', 'High water cut (>60 %)',  '38 wells', '7,000 BOPD'],
        ['S3', 'Low BHFP — Pb risk',       '12 wells', '1,800 BOPD'],
        ['S4', 'Inactive — WO backlog',    '14 wells', '3,920 BOPD'],
        ['S5', 'Reservoir P depletion',    '8 wells',  '5,000 BOPD'],
      ] },
    { x: 4.65, c: C.oil, title: 'SURFACE / COMPLETION',
      rows: [
        ['C1', 'Low DP / VSD required',    '22 wells', '6,500 BOPD'],
        ['C2', 'ESP at max frequency',     '14 wells', '3,500 BOPD'],
        ['C3', 'Back-pressure (flowline)', 'TBD',      '~2–4 kBOPD est.'],
      ] },
    { x: 8.9, c: C.water, title: 'WATER INJECTION',
      rows: [
        ['W1', 'Cluster cap 26 Mbwpd',     '—',  'physical ceiling'],
        ['W2', 'WI integrity 175/180',     '2 wells', '16 kbwpd stranded'],
        ['W3', 'R1↔R2 water loss',         '2 wells', 'tracer needed'],
        ['W4', 'High-WC producers',        '12 wells', 'PW loading'],
      ] },
  ];
  cols.forEach(col => {
    const x = col.x, w = 4.0;
    s.addShape(pres.ShapeType.rect, { x, y: 1.3, w, h: 0.4, fill: { color: col.c }, line: { color: col.c } });
    s.addText(col.title, { x: x+0.15, y: 1.34, w: w-0.3, h: 0.32,
      fontFace: F.mono, fontSize: 11, color: 'FFFFFF', bold: true, charSpacing: 1.5 });
    col.rows.forEach((r, i) => {
      const y = 1.8 + i * 0.65;
      s.addShape(pres.ShapeType.rect, { x, y, w, h: 0.6, fill: { color: i%2 ? C.panel : 'FFFFFF' }, line: { color: C.line, width: 0.4 } });
      s.addShape(pres.ShapeType.rect, { x, y, w: 0.04, h: 0.6, fill: { color: col.c }, line: { color: col.c } });
      s.addText(r[0], { x: x+0.12, y: y+0.05, w: 0.45, h: 0.25,
        fontFace: F.mono, fontSize: 11, color: col.c, bold: true });
      s.addText(r[1], { x: x+0.55, y: y+0.05, w: w-0.6, h: 0.25,
        fontFace: F.body, fontSize: 10.5, color: C.text, bold: true });
      s.addText(r[2], { x: x+0.12, y: y+0.32, w: 1.2, h: 0.22,
        fontFace: F.mono, fontSize: 9, color: C.sub });
      s.addText(r[3], { x: x+1.35, y: y+0.32, w: w-1.4, h: 0.22,
        fontFace: F.mono, fontSize: 9, color: C.oil, bold: true, align: 'right' });
    });
  });

  // Bottom note
  s.addText('Note: Counts and BOPD-lost figures are RM-classified analytical estimates (§ANALYSIS BLOCK). C3 surface back-pressure pending Jan-2026 FCT report.', {
    x: 0.4, y: 6.85, w: 12.6, h: 0.25, fontFace: F.body, italic: true, fontSize: 9, color: C.sub });
}

// ============================================================
// SLIDE 5 — RANKING & GAIN BRIDGE (combined)
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Consolidated Ranking & Gain Bridge', page: '05 / 12', eyebrow: 'PRIORITIZATION' });

  // Left: ranked table
  sectionTitle(s, 0.4, 0.9, 6, 'RANKED BY 2026 REALISTIC GAIN');
  const ranked = [
    ['1', '§4.5', 'WI capacity (SY-175/180 + cluster)', '2,500–4,000', 'M-H', '$2–28M'],
    ['2', '§4.7', 'Surface back-pressure optimization',  '1,500–2,500', 'M',   '$0.2–8M'],
    ['3', '§4.6', 'PW redistribution + R1/R2 rebalance', '2,000–2,400', 'M',   '$0.5–1.5M'],
    ['4', '§4.1', 'Stimulation roll-out beyond 1.1C',    '2,500',       'M',   '$8–12M'],
    ['5', '§4.3', 'VSD / PWS retrofit campaign',         '1,600',       'H',   '$2.4–4.8M'],
    ['6', '§4.4', 'ESP upsize (piggyback WOs)',          '800',         'M',   '$2.0–3.2M'],
    ['7', '§4.2', 'BHFP rate-cap relaxation',            '900',         'M-H', '$0.2–0.5M'],
    ['8', '§4.8', 'Inactive-string reactivation',        '1,000',       'H',   '$0.5–1.0M'],
  ];
  const rkHead = [{text:'#',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9,align:'center'}},
                  {text:'ID',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9}},
                  {text:'Opportunity',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9}},
                  {text:'2026 BOPD',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9,align:'right'}},
                  {text:'Conf.',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9,align:'center'}},
                  {text:'Capex',options:{bold:true,fill:C.navy,color:'FFFFFF',fontSize:9,align:'right'}}];
  const rkBody = ranked.map((r,i) => {
    const fill = i%2 ? 'F1F5F9' : 'FFFFFF';
    const confColor = r[4]==='H' ? C.good : r[4]==='M-H' ? C.teal : C.warn;
    return [
      {text:r[0],options:{fontFace:F.mono,fontSize:9,bold:true,color:C.oil,align:'center',fill}},
      {text:r[1],options:{fontFace:F.mono,fontSize:9,bold:true,color:C.navy,fill}},
      {text:r[2],options:{fontSize:9.5,fill}},
      {text:r[3],options:{fontFace:F.mono,fontSize:9,align:'right',fill}},
      {text:r[4],options:{fontFace:F.mono,fontSize:9,align:'center',color:confColor,bold:true,fill}},
      {text:r[5],options:{fontFace:F.mono,fontSize:9,align:'right',color:C.sub,fill}},
    ];
  });
  s.addTable([rkHead, ...rkBody], { x: 0.4, y: 1.3, w: 6.3, colW: [0.4, 0.7, 2.4, 1.3, 0.6, 0.9],
    border: { type:'solid', color: C.line, pt: 0.4 }, valign: 'middle' });

  // Total row
  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 5.8, w: 6.3, h: 0.4, fill: { color: C.oil }, line: { color: C.oil } });
  s.addText('TOTAL realistic envelope (×0.75 overlap deduction)', {
    x: 0.5, y: 5.83, w: 4.6, h: 0.34, fontFace: F.mono, fontSize: 10, color: 'FFFFFF', bold: true });
  s.addText('~9,600 BOPD', {
    x: 5.0, y: 5.83, w: 1.6, h: 0.34, fontFace: F.mono, fontSize: 12, color: 'FFFFFF', bold: true, align: 'right' });

  // Right: gain bridge waterfall
  sectionTitle(s, 6.9, 0.9, 6, 'GAIN BRIDGE — 75,733 → ~87,000 BOPD');
  const waterfallData = [
    { name: 'Start',     labels: ['Start','§4.5','§4.7','§4.6','§4.1','§4.3','§4.4','§4.2','§4.8','Target'],
      values: [75733, 0, 0, 0, 0, 0, 0, 0, 0, 0] },
    { name: 'Gains',     labels: ['Start','§4.5','§4.7','§4.6','§4.1','§4.3','§4.4','§4.2','§4.8','Target'],
      values: [0, 2500, 1500, 2000, 1875, 1200, 600, 900, 1000, 0] },
    { name: 'Target',    labels: ['Start','§4.5','§4.7','§4.6','§4.1','§4.3','§4.4','§4.2','§4.8','Target'],
      values: [0, 0, 0, 0, 0, 0, 0, 0, 0, 87308] },
    { name: 'Stack',     labels: ['Start','§4.5','§4.7','§4.6','§4.1','§4.3','§4.4','§4.2','§4.8','Target'],
      values: [0, 75733, 78233, 79733, 81733, 83608, 84808, 85408, 86308, 0] },
  ];
  // Build waterfall as stacked column: invisible base + gain segment
  const wfLabels = ['Start','§4.5','§4.7','§4.6','§4.1','§4.3','§4.4','§4.2','§4.8','Target'];
  const baseVals = [0, 75733, 78233, 79733, 81733, 83608, 84808, 85408, 86308, 0];
  const incrVals = [75733, 2500, 1500, 2000, 1875, 1200, 600, 900, 1000, 87308];
  s.addChart(pres.ChartType.bar, [
    { name: 'base', labels: wfLabels, values: baseVals },
    { name: 'value', labels: wfLabels, values: incrVals },
  ], {
    x: 6.9, y: 1.3, w: 6.2, h: 4.5,
    barDir: 'col', barGrouping: 'stacked',
    chartColors: ['FFFFFF', C.oil],
    chartColorsOpacity: 0,
    showLegend: false,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 8,
    catAxisLabelColor: C.text, valAxisLabelColor: C.sub,
    valAxisMinVal: 70000, valAxisMaxVal: 92000,
    showValue: false,
  });

  // Bridge commentary
  s.addText([
    { text: '+11,575 BOPD ', options: { bold: true, color: C.mint, fontFace: F.mono, fontSize: 12 } },
    { text: 'cumulative — within 10–12 kBOPD realistic envelope. §4.1+§4.3+§4.4 deflated ×0.75 for overlap.', options: { fontSize: 10, color: C.text } },
  ], { x: 6.9, y: 5.85, w: 6.2, h: 0.4, fontFace: F.body });

  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 6.5, w: 12.6, h: 0.55, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText('Saih Rawl Shuaiba analog (SPE 68222): +6,300 BOPD on smaller system via WI rebalancing + automation — directly supports the §4.5/§4.6/§4.7 envelope.', {
    x: 0.55, y: 6.55, w: 12.3, h: 0.45, fontFace: F.body, italic: true, fontSize: 11, color: 'FFFFFF' });
}

// ============================================================
// SLIDES 6–9 — TOP 4 OPP DEEP-DIVES
// ============================================================
function oppSlide(opp, page) {
  const s = pres.addSlide();
  pageFrame(s, { title: `§${opp.id} — ${opp.title}`, page, eyebrow: 'OPPORTUNITY DEEP-DIVE' });

  // Left column — 3 KPI cards stacked
  kpiCard(s, 0.4, 0.9, 3.7, 1.35, '2026 REALISTIC GAIN', opp.gainLabel, 'BOPD', C.mint);
  kpiCard(s, 0.4, 2.4, 3.7, 1.35, 'FULL POTENTIAL', opp.fullLabel, 'BOPD', C.teal);
  kpiCard(s, 0.4, 3.9, 3.7, 1.35, 'CAPEX BRACKET', opp.capexLabel, '$M · ' + opp.conf, C.oil);

  // Right column — story
  sectionTitle(s, 4.4, 0.9, 6, 'MECHANISM');
  s.addText(opp.mechanism, { x: 4.4, y: 1.3, w: 8.6, h: 2.3,
    fontFace: F.body, fontSize: 11.5, color: C.text, lineSpacingMultiple: 1.4 });

  sectionTitle(s, 4.4, 3.8, 6, 'PREREQUISITE');
  s.addText(opp.prereq, { x: 4.4, y: 4.2, w: 8.6, h: 1.2,
    fontFace: F.body, italic: true, fontSize: 11, color: C.sub });

  // Bottom recommendation band
  const recColor = opp.recColor || C.navy;
  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 5.5, w: 12.6, h: 1.55, fill: { color: recColor }, line: { color: recColor } });
  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 5.5, w: 0.08, h: 1.55, fill: { color: C.oil }, line: { color: C.oil } });
  s.addText('RECOMMENDATION', { x: 0.6, y: 5.58, w: 4, h: 0.28,
    fontFace: F.mono, fontSize: 10, color: C.oil, bold: true, charSpacing: 2 });
  s.addText(opp.recommendation, { x: 0.6, y: 5.85, w: 12.3, h: 1.15,
    fontFace: F.body, fontSize: 12, color: 'FFFFFF', lineSpacingMultiple: 1.35 });
}

// 6 — §4.5
oppSlide({
  id: '4.5', title: 'WI capacity uplift (SY-175 + SY-180 + cluster review)',
  gainLabel: '2,500–4,000', fullLabel: '4,000–5,500', capexLabel: '$2–28M', conf: 'Med-High',
  mechanism: 'Phase 1 (Q2/Q3-2026): Complete WO on SY-175 & SY-180 to recover 16,000 bwpd stranded capacity. RM-mandated prerequisite: FCT in Cluster #2 / SY-148 WS before SY-180 commissioning to confirm Cluster #2 can handle the additional load (currently 19/28.8 kbwpd).\n\nPhase 2 (2027): Cluster #2 capacity uplift study — if FCT confirms hard ceiling at 26 Mbwpd, evaluate pump/manifold capacity to lift to 35 Mbwpd.\n\nPhase 3 (long-term): New WI well drilling if VRR confirms additional voidage to fill. Saih Rawl analog (SPE 68222): ~12 % oil rate uplift per 30 % WI rate increase.',
  prereq: 'Cluster #2 / SY-148 WS FCT (single most important data request) · G2V2 ML#5 reservoir model · Voidage Replacement Ratio analysis',
  recommendation: 'Approve Phase 1 SY-175/180 WO execution immediately (capex already in plan). Commission FCT in CL02/SY-148 as RM-mandated prerequisite before SY-180 start-up. Stage Phase 2 cluster uplift decision pending FCT results.',
  recColor: C.deep
}, '06 / 12');

// 7 — §4.7
oppSlide({
  id: '4.7', title: 'Surface back-pressure optimization',
  gainLabel: '1,500–2,500', fullLabel: '2,300–3,300', capexLabel: '$0.2–8M', conf: 'Medium',
  mechanism: 'Phase 1: Station header pressure setpoint review at CDS / RDS-1 / RDS-2. Each 10 psi separator reduction across 80 R1 producers ≈ +800 BOPD via reduced WHFP and improved IPR/VLP intersection.\n\nPhase 2: Selective flowline looping on 2-3 worst segments (>200 psi/km ΔP). Phase 3: Choke-on-test vs production-choke alignment — many wells tested at higher chokes than routinely operated.\n\nDirect evidence pending FCT, but proxy indicators (full choke + ESP at 50 Hz + rate plateau, WHFT 150-162 °F) point to downstream restriction.',
  prereq: 'January-2026 FCT report (single most important data request after Cluster #2 FCT) · GAP/Prosper IPM model · WHIP/WHFP-vs-time per well',
  recommendation: 'Hold quantification at pending-FCT estimate. Once FCT report lands, commission GAP/Prosper rerun with revised separator setpoints. Phase 1 is near-zero capex — pursue setpoint review as fast win.',
  recColor: '8B4513'
}, '07 / 12');

// 8 — §4.6
oppSlide({
  id: '4.6', title: 'Produced-water redistribution + R1↔R2 rebalancing',
  gainLabel: '2,000–2,400', fullLabel: '2,400–3,200', capexLabel: '$0.5–1.5M', conf: 'Medium',
  mechanism: '(a) Inter-reservoir tracer + integrity diagnosis on 139-SS and 145-SS — RM explicitly flagged R1→R2 water loss; if confirmed, cement squeeze to restore zonal isolation.\n\n(b) Rebalance injection R1/R2: R1 currently under-injected ~5 kbwpd vs sustainable VRR. Redirect 3-5 kbwpd from R2 to R1 once Cluster #2 integrity allows.\n\n(c) Selective shut-in of 6 worst high-WC producers (>85% WC) — collectively producing ~960 BOPD oil but consuming 40 kbwpd PW handling capacity. Net benefit: +1,200 BOPD elsewhere via better VRR.',
  prereq: 'PW lab analysis (TDS, scaling, particulates, H₂S) · Injector PLT / CBL on 139-SS, 145-SS · G2V2 rerun with rebalanced injection',
  recommendation: 'Greenlight low-capex tracer campaign immediately ($0.5-1.5M). Concurrent: identify the 6 high-WC shut-in candidates from the Wells table for FY-2026 decision. PW lab work is independent and can start at any time.',
  recColor: C.teal
}, '08 / 12');

// 9 — §4.1
oppSlide({
  id: '4.1', title: 'Stimulation roll-out beyond Obj 1.1C',
  gainLabel: '2,500', fullLabel: '5,000–6,000', capexLabel: '$8–12M', conf: 'Medium',
  mechanism: '32+ R1 strings flagged "Low intake / Low PIP / stim required" by RM. Obj 1.1C delivers stimulation on only 5 wells in 2026.\n\nApply proven Naphtha+HCl recipe to 8-10 additional R1 wells per year as sustained program. Target wells with PI degradation D > 30 %/yr (1.1C methodology). Average gain +150 to +400 BOPD per well, declining 30 %/yr post-job.\n\nFull backlog of 25 incremental candidates × 250 BOPD avg ≈ +6,000 BOPD at peak if all done within 18 months. Realistic 2026 deliverable: 10 incremental wells = +2,500 BOPD.',
  prereq: 'Per-well PI screening across 32 stim candidates (extension of 1.1C dashboard methodology)',
  recommendation: 'Extend the Obj 1.1C dashboard with PI-degradation screening across all 32 RM-flagged candidates. Build Q3-2026 stim queue from top-D ranking. Schedule 10 wells for 2026, decision-gate the remaining 15 against 2026 results.',
  recColor: '0E7F3F'
}, '09 / 12');

// ============================================================
// SLIDE 10 — DATA GAPS + NEXT STEPS (timeline)
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Data Gaps & Next Steps', page: '10 / 12', eyebrow: 'EXECUTION PLAN' });

  // Left — data gaps list
  sectionTitle(s, 0.4, 0.9, 6, 'CRITICAL DATA GAPS');
  const gaps = [
    ['01','January-2026 FCT report','§4.7 cannot move past estimate'],
    ['02','GAP/Prosper IPM model','Back-pressure sensitivities'],
    ['03','G2V2 reservoir model — ML#5','§4.5 oil response · §4.6 rebalancing'],
    ['04','Cluster #2 / SY-148 WS FCT','RM-mandated for SY-180 commissioning'],
    ['05','PIDs / PFDs / vendor sheets','CDS, RDS-1/2, WI clusters'],
    ['06','Produced water lab analysis','§4.6 chemical design'],
    ['07','WHIP/WHFP-vs-time per well','§4.7 flowline hypothesis'],
    ['08','Injector PLT/CBL (139-SS, 145-SS)','§4.6 (a) integrity diagnosis'],
    ['09','Per-well PI screening (32 candidates)','§4.1 backlog scoping'],
  ];
  gaps.forEach((g, i) => {
    const y = 1.3 + i * 0.42;
    s.addText(g[0], { x: 0.4, y, w: 0.45, h: 0.38, fontFace: F.mono, fontSize: 12, color: C.oil, bold: true });
    s.addText(g[1], { x: 0.9, y, w: 3.2, h: 0.2, fontFace: F.body, fontSize: 10.5, color: C.text, bold: true });
    s.addText(g[2], { x: 0.9, y: y+0.2, w: 5.5, h: 0.2, fontFace: F.body, italic: true, fontSize: 9.5, color: C.sub });
  });

  // Right — timeline strip
  sectionTitle(s, 6.9, 0.9, 6, 'EXECUTION TIMELINE');
  const phases = [
    { lbl: 'Q2-26', items: ['SY-175/180 WO start','PW lab campaign','FCT submission'], color: C.oil },
    { lbl: 'Q3-26', items: ['Tracer 139/145-SS','VSD retrofit kick-off','Tech WS sign-off'], color: C.teal },
    { lbl: 'Q4-26', items: ['SY-180 commissioning','Setpoint pilot','Stim batch 1 (5 wells)'], color: C.mint },
    { lbl: '2027',  items: ['Cluster #2 uplift','Stim batch 2 (5 wells)','ESP upsizes'], color: C.water },
  ];
  phases.forEach((p, i) => {
    const y = 1.3 + i * 1.32;
    s.addShape(pres.ShapeType.rect, { x: 6.9, y, w: 1.05, h: 1.2, fill: { color: p.color }, line: { color: p.color } });
    s.addText(p.lbl, { x: 6.9, y: y+0.4, w: 1.05, h: 0.4,
      fontFace: F.mono, fontSize: 16, color: 'FFFFFF', bold: true, align: 'center' });
    p.items.forEach((it, j) => {
      const yy = y + j * 0.36;
      s.addShape(pres.ShapeType.rect, { x: 8.0, y: yy+0.05, w: 5.0, h: 0.3, fill: { color: 'FFFFFF' }, line: { color: p.color, width: 0.7 } });
      s.addShape(pres.ShapeType.ellipse, { x: 8.05, y: yy+0.15, w: 0.1, h: 0.1, fill: { color: p.color }, line: { color: p.color } });
      s.addText(it, { x: 8.25, y: yy+0.06, w: 4.7, h: 0.28, fontFace: F.body, fontSize: 10, color: C.text });
    });
  });
}

// ============================================================
// SLIDE 11 — CAPEX vs GAIN matrix
// ============================================================
{
  const s = pres.addSlide();
  pageFrame(s, { title: 'Capex vs Gain — Prioritization Matrix', page: '11 / 12', eyebrow: 'INVESTMENT VIEW' });

  // KPI strip - total $ per BOPD
  kpiCard(s, 0.4, 0.9, 3.0, 1.3, 'TOTAL CAPEX RANGE', '$16–58M', 'across 8 opportunities', C.oil);
  kpiCard(s, 3.55, 0.9, 3.0, 1.3, '2026 GAIN MIDPOINT', '~11,575', 'BOPD with overlap', C.mint);
  kpiCard(s, 6.7, 0.9, 3.0, 1.3, '$ / BOPD AVERAGE', '$3,200', 'weighted across all opps', C.teal);
  kpiCard(s, 9.85, 0.9, 3.0, 1.3, 'PAYBACK @ $80/bbl', '< 6 mo', 'on top 4 opportunities', C.mint);

  // Bubble chart (scatter)
  sectionTitle(s, 0.4, 2.6, 6, 'CAPEX (X) vs GAIN (Y) — bubble = $/BOPD');
  s.addChart(pres.ChartType.scatter, [
    { name: 'X', values: [15.0, 4.1, 1.0, 10.0, 3.6, 2.6, 0.35, 0.75] },
    { name: 'Y', values: [3250, 2000, 2200, 2500, 1600, 800,  900,  1000] },
  ], {
    x: 0.4, y: 3.0, w: 12.6, h: 3.7,
    chartColors: [C.oil],
    showLegend: false,
    catAxisTitle: 'Capex midpoint ($M)',
    valAxisTitle: '2026 gain midpoint (BOPD)',
    catAxisTitleFontSize: 10, valAxisTitleFontSize: 10,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9,
    catAxisLabelColor: C.text, valAxisLabelColor: C.text,
    lineDataSymbol: 'circle', lineDataSymbolSize: 16,
    lineSize: 0,
  });

  // Note
  s.addText('§4.6 (PW redistribution) and §4.2 (BHFP relaxation) sit in the sweet spot: low capex, fast gain. §4.5 has the widest capex range because Phase 2 cluster uplift is contingent on FCT.', {
    x: 0.4, y: 6.85, w: 12.6, h: 0.25, fontFace: F.body, italic: true, fontSize: 10, color: C.sub });
}

// ============================================================
// SLIDE 12 — CONCLUSIONS
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: C.oil }, line: { color: C.oil } });

  s.addText('CONCLUSIONS', { x: 0.6, y: 0.4, w: 6, h: 0.4,
    fontFace: F.mono, fontSize: 14, color: C.oil, bold: true, charSpacing: 4 });
  s.addText('Shah field can lift 10–12 kBOPD within 12 months', {
    x: 0.6, y: 0.85, w: 12, h: 0.7, fontFace: F.head, fontSize: 30, color: 'FFFFFF', bold: true });
  s.addText('with the right sequencing of subsurface, surface, and WI initiatives', {
    x: 0.6, y: 1.55, w: 12, h: 0.4, fontFace: F.head, italic: true, fontSize: 16, color: C.dim });

  const findings = [
    { n: '01', c: C.oil,   t: 'BIGGEST ABSOLUTE PRIZE IS WATER INJECTION',
      b: '§4.5 SY-175/180 + cluster review delivers 2.5–4 kBOPD realistic — the largest single contribution and a pre-requisite for sustained R1 pressure support. Already partially budgeted via WO plan.' },
    { n: '02', c: C.teal,  t: 'SURFACE BACK-PRESSURE IS THE NEXT-LARGEST AND CHEAPEST WIN',
      b: '§4.7 phase-1 setpoint review costs ~$0.2M and could deliver 1.5–2.5 kBOPD. But the entire envelope is hostage to the Jan-2026 FCT report and GAP/Prosper IPM model — both still missing. Single biggest data request.' },
    { n: '03', c: C.mint,  t: 'PRODUCED-WATER REDISTRIBUTION IS A NEAR-ZERO-CAPEX OPP',
      b: '§4.6 R1↔R2 rebalancing + tracer integrity diagnosis on 139-SS/145-SS delivers ~2 kBOPD at $0.5–1.5M. Lowest-friction commercial recommendation — can start before FCT report lands.' },
    { n: '04', c: C.water, t: 'STIMULATION BACKLOG IS DEEPER THAN OBJ 1.1C SCOPE',
      b: '~32 R1 strings flagged "Low PIP / stim required" by RM. Obj 1.1C addresses 5. Sustained program of 8-10 wells/year via Naphtha+HCl recipe builds a +6 kBOPD asset over 18 months at $8-12M capex.' },
    { n: '05', c: C.bad,   t: 'NINE CRITICAL DATA GAPS — FCT REPORT IS #1',
      b: 'Until the Jan-2026 FCT report, the GAP/Prosper IPM model, and the G2V2 ML#5 forecast are received, §4.7 stays at "pending-FCT estimate" and §4.5 Phase 2 cluster uplift decision cannot be quantified.' },
  ];
  findings.forEach((f, i) => {
    const y = 2.2 + i * 0.95;
    s.addText(f.n, { x: 0.6, y, w: 0.5, h: 0.85, fontFace: F.mono, fontSize: 26, color: f.c, bold: true });
    s.addShape(pres.ShapeType.rect, { x: 1.2, y, w: 0.04, h: 0.85, fill: { color: f.c }, line: { color: f.c } });
    s.addText(f.t, { x: 1.4, y, w: 11.5, h: 0.3,
      fontFace: F.mono, fontSize: 11, color: f.c, bold: true, charSpacing: 1.5 });
    s.addText(f.b, { x: 1.4, y: y+0.32, w: 11.5, h: 0.55,
      fontFace: F.body, fontSize: 11, color: 'FFFFFF', lineSpacingMultiple: 1.3 });
  });

  // Bottom band
  s.addShape(pres.ShapeType.rect, { x: 0, y: 7.3, w: 13.333, h: 0.2, fill: { color: C.oil }, line: { color: C.oil } });
}

// ---------- Save ----------
pres.writeFile({ fileName: OUT }).then(fn => console.log('Saved:', fn));
