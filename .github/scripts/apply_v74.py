from pathlib import Path
p=Path('index.html')
h=p.read_text(encoding='utf-8')

def r(old,new):
    global h
    if old not in h:
        raise SystemExit('missing target: '+old[:80])
    h=h.replace(old,new,1)

r('<title>ma.｜案件 v72</title>','<title>ma.｜案件 v74</title>')
r('version:72,','version:74,')
r('data-build="ma-project-v72"','data-build="ma-project-v74"')
r('const WORKSPACE_DOCK_KEY="maWorkspaceDockV72"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV74"')

# left tabs: remove structural region from sidebar
r('''  <div class="sideTabs leftStructureTabs" data-side-tabs="left">\n    <button class="sideTab active" data-side-tab="region" type="button">区画</button>\n    <button class="sideTab" data-side-tab="dimensions" type="button">寸法</button>\n    <button class="sideTab" data-side-tab="materials" type="button">材料</button>\n    <button class="sideTab" data-side-tab="composition" type="button">部材構成</button>\n  </div>''','''  <div class="sideTabs leftStructureTabs" data-side-tabs="left">\n    <button class="sideTab active" data-side-tab="dimensions" type="button">寸法</button>\n    <button class="sideTab" data-side-tab="materials" type="button">材料</button>\n    <button class="sideTab" data-side-tab="composition" type="button">部材構成</button>\n  </div>''')

# extract structural region editor from sidebar
s=h.index('  <div class="section sidePanel" id="leftRegionSection" data-left-panel="region">')
e=h.index('  <div class="section sidePanel regionDimensionsPanel',s)
region=h[s:e]
h=h[:s]+h[e:]
region=region.replace('<div class="section sidePanel" id="leftRegionSection" data-left-panel="region">','<div class="section sidePanel dockRegionStructure" id="leftRegionSection">')

# center dock region tab
r('''            <button type="button" class="active" data-workspace-dock-tab="box" role="tab">箱の構成</button>\n            <button type="button" data-workspace-dock-tab="joint" role="tab">四隅</button>''','''            <button type="button" class="active" data-workspace-dock-tab="box" role="tab">箱の構成</button>\n            <button type="button" data-workspace-dock-tab="region" role="tab">区画</button>\n            <button type="button" data-workspace-dock-tab="joint" role="tab">四隅</button>''')

# replace old hidden drawer/door/movable shelf dock with structural editor, but keep old controls in a hidden compatibility host
ls=h.index('          <section class="workspaceDockPanel legacyRegionContentPanel" data-workspace-dock-panel="region" hidden>')
le=h.index('          <section class="workspaceDockPanel" data-workspace-dock-panel="joint">',ls)
legacy=h[ls:le]
legacy_inner=legacy.split('>',1)[1].rsplit('</section>',1)[0]
newdock='          <section class="workspaceDockPanel" data-workspace-dock-panel="region">\n'+region+'          </section>\n\n'
h=h[:ls]+newdock+h[le:]
compat='<div id="legacyRegionContentHost" hidden aria-hidden="true">'+legacy_inner+'</div>\n'
mi=h.index('<div id="mobileInputToolbar"')
h=h[:mi]+compat+h[mi:]

# dock state accepts region
h=h.replace('["box","joint","plinth","backboard"]','["box","region","joint","plinth","backboard"]')
h=h.replace('    else if(saved.tab==="region")workspaceDockState.tab="box";\n','')

# mobile sidebar no longer moves region editor
h=h.replace('    {node:document.getElementById("leftRegionSection"),target:"left"},\n','')
h=h.replace('grid-template-columns:repeat(4,minmax(0,1fr))!important;','grid-template-columns:repeat(3,minmax(0,1fr))!important;',1)

# replace legacy hidden css with dock layout + formula styles
h=h.replace('''/* ===== legacy front-content panel removed from UI / v71 ===== */\n#workspaceDock .legacyRegionContentPanel{display:none!important}\n''','')
css='''\n/* ===== structural region editor moved to center dock / v74 ===== */\n#workspaceDock .dockRegionStructure{height:100%;min-height:0;margin:0;padding:2px 4px;border:0;background:transparent;display:grid;grid-template-columns:minmax(150px,.7fr) minmax(160px,.85fr) minmax(170px,.95fr) minmax(220px,1.25fr);gap:7px 10px;align-content:start;overflow:auto}\n#workspaceDock .dockRegionStructure>h3{grid-column:1/-1;margin:0;font-size:10px}\n#workspaceDock .dockRegionStructure>.selectedBox{grid-column:1}\n#workspaceDock .dockRegionStructure>.innerBackControls{grid-column:2 / 4;grid-row:2 / span 3}\n#workspaceDock .dockRegionStructure>.field{margin:0}\n#workspaceDock .dockRegionStructure>.addButtons{grid-column:4;grid-row:2}\n#workspaceDock .dockRegionStructure>p.note{grid-column:4;grid-row:3;margin:0;font-size:8px;line-height:1.45}\n#workspaceDock .dockRegionStructure>#undoSplit{grid-column:4;grid-row:4;margin-top:0!important}\n#workspaceDock .dockRegionStructure input{min-width:0}\n#legacyRegionContentHost{display:none!important}\n.centerOuter input.formulaInvalid{border-color:#b77872!important;box-shadow:inset 0 0 0 1px rgba(160,75,65,.12)}\n.centerOuter input[type="text"]{font-variant-numeric:tabular-nums}\n@media(max-width:760px){#workspaceDock .dockRegionStructure{height:auto;display:block;padding:4px 1px;overflow:visible}#workspaceDock .dockRegionStructure>.field,#workspaceDock .dockRegionStructure>.innerBackControls,#workspaceDock .dockRegionStructure>.addButtons{margin-top:9px}}\n'''
h=h.replace('</style>',css+'</style>',1)

# outer inputs accept formulas
r('''        <label>W <input id="W" type="number" value="1800" min="1"></label>\n        <label>H <input id="H" type="number" value="900" min="1"></label>\n        <label>D <input id="D" type="number" value="450" min="1"></label>''','''        <label>W <input id="W" type="text" inputmode="decimal" value="1800" autocomplete="off"></label>\n        <label>H <input id="H" type="text" inputmode="decimal" value="900" autocomplete="off"></label>\n        <label>D <input id="D" type="text" inputmode="decimal" value="450" autocomplete="off"></label>''')

r('''const state={\n  outer:{W:1800,H:900,D:450},''','''const state={\n  outer:{W:1800,H:900,D:450},\n  outerFormula:{W:"1800",H:"900",D:"450"},''')
r('''function readOuter(){\n  state.outer.W=+($("W").value||1);\n  state.outer.H=+($("H").value||1);\n  state.outer.D=+($("D").value||1);\n}''','''function resolveOuterDimension(axis,formulas=state.outerFormula,stack=[]){\n  if(stack.includes(axis))return NaN;\n  let e=String(formulas?.[axis]??"").trim();\n  if(!e)return NaN;\n  e=e.replace(/\\b([WHD])\\b/g,(_all,ref)=>{const v=resolveOuterDimension(ref,formulas,[...stack,axis]);return Number.isFinite(v)?`(${v})`:"NaN"});\n  if(!/^[0-9+\\-*/().\\s]+$/.test(e))return NaN;\n  try{const v=Function(`"use strict";return (${e})`)();return Number.isFinite(v)&&v>0?v:NaN}catch(_){return NaN}\n}\nfunction readOuter(){\n  const formulas={W:$("W").value,H:$("H").value,D:$("D").value};\n  state.outerFormula={...formulas};\n  ["W","H","D"].forEach(axis=>{const input=$(axis);const v=resolveOuterDimension(axis,formulas,[]);const valid=Number.isFinite(v)&&v>0;input.classList.toggle("formulaInvalid",!valid);input.setAttribute("aria-invalid",valid?"false":"true");input.title=valid?`計算結果 ${formatFinishedMm(v)} mm`:"計算式を確認してください";if(valid)state.outer[axis]=Math.round(v*1000)/1000});\n}''')

# persist formula strings
r('''      outerPreview:{...state.outer},\n      variables:''','''      outerPreview:{...state.outer},\n      outerFormula:{...state.outerFormula},\n      variables:''')
r('''      outerPreview:{...(s.outerPreview||{W:1800,H:900,D:450})},\n      joints:''','''      outerPreview:{...(s.outerPreview||{W:1800,H:900,D:450})},\n      outerFormula:{W:String(s.outerPreview?.W??1800),H:String(s.outerPreview?.H??900),D:String(s.outerPreview?.D??450),...(s.outerFormula||{})},\n      joints:''')
r('''  state.outer={...(s.outerPreview||{W:1800,H:900,D:450})};\n  state.joints=''','''  state.outer={...(s.outerPreview||{W:1800,H:900,D:450})};\n  state.outerFormula={W:String(state.outer.W),H:String(state.outer.H),D:String(state.outer.D),...(s.outerFormula||{})};\n  state.joints=''')
r('''  $("patternName").value=data.name||"ユニット 01";$("W").value=state.outer.W;$("H").value=state.outer.H;$("D").value=state.outer.D;$("plinthHeight").value=''','''  $("patternName").value=data.name||"ユニット 01";$("W").value=state.outerFormula.W;$("H").value=state.outerFormula.H;$("D").value=state.outerFormula.D;$("plinthHeight").value=''')
r('''    outerPreview:{W:1800,H:900,D:450},\n    joints:''','''    outerPreview:{W:1800,H:900,D:450},\n    outerFormula:{W:"1800",H:"900",D:"450"},\n    joints:''')

# region -> new unit resets formulas to numeric strings
old='''    state.outer={W:dims.W,H:dims.H,D:dims.D};\n    $("W").value=formatFinishedMm(dims.W);\n    $("H").value=formatFinishedMm(dims.H);\n    $("D").value=formatFinishedMm(dims.D);'''
new='''    state.outer={W:dims.W,H:dims.H,D:dims.D};\n    state.outerFormula={W:formatFinishedMm(dims.W),H:formatFinishedMm(dims.H),D:formatFinishedMm(dims.D)};\n    $("W").value=state.outerFormula.W;\n    $("H").value=state.outerFormula.H;\n    $("D").value=state.outerFormula.D;'''
if h.count(old)!=2: raise SystemExit('region unit target count mismatch')
h=h.replace(old,new)

# delay initial dimensions tab until cutState exists
r('setSideTab("left","region");','/* v74 side tab init after cutState */')
r('''let cutState=migrateStandardMaterialsInState(defaultCutState());\nsanitizeFinishMaterialsInPatterns(cutState.patterns,cutState.materials);\nlet lastCutResult=null;''','''let cutState=migrateStandardMaterialsInState(defaultCutState());\nsanitizeFinishMaterialsInPatterns(cutState.patterns,cutState.materials);\nlet lastCutResult=null;\nsetSideTab("left","dimensions");''')

p.write_text(h,encoding='utf-8')
print('v74 applied')
