from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'data-build="ma-project-v79"' in s:
    print('v79 already applied')
    raise SystemExit(0)
for old,new in [
    ('<title>ma.｜案件 v77</title>','<title>ma.｜案件 v79</title>'),
    ('version:77,','version:79,'),
    ('data-build="ma-project-v77"','data-build="ma-project-v79"'),
    ('const WORKSPACE_DOCK_KEY="maWorkspaceDockV77"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV79"')]:
    if old not in s: raise SystemExit(f'missing marker: {old}')
    s=s.replace(old,new,1)
css=r'''
/* ===== ma. v79 / Sketch Craft ===== */
:root{
 --paper:#F1ECE3;--paper2:#F2ECE2;--panelPaper:#FCF9F2;--ink:#2D2925;--muted:#6F675F;
 --line:#DED4C6;--line-strong:#C8B9A5;--craft:#A85F32;--craft-deep:#874722;--craft-warm:#C7783D;
 --craft-soft:#C7783D1F;--craft-green:#667C58;--danger:#B85C5C;
 --shadow-craft:0 3px 7px rgba(74,58,45,.13),0 1px 1px rgba(74,58,45,.10);
 --shadow-paper:0 7px 18px rgba(74,58,45,.08);--sketch-radius:4px 6px 5px 3px;
 --accent:#A85F32;--accentSoft:#C7783D1F;
}
html,body{background-color:var(--paper)!important;color:var(--ink)!important}
body{background-image:radial-gradient(circle at 18% 24%,rgba(168,95,50,.018) 0 1px,transparent 1.4px),radial-gradient(circle at 76% 63%,rgba(45,41,37,.014) 0 1px,transparent 1.5px)!important;background-size:23px 19px,31px 27px!important}
.left,.right,.workspaceDock,.mobileSidebar,.projectModalCard,.modalCard,.homeCard,.projectCard,.unitCard{background:rgba(252,249,242,.96)!important;border-color:var(--line)!important}
.left,.right,.workspaceDock{box-shadow:var(--shadow-paper)!important}.workspaceDock{border-radius:6px 5px 7px 4px!important}
h1,h2,h3,h4,.panelTitle,.sectionTitle{color:var(--ink)!important}.note,.muted,.small,.hint{color:var(--muted)!important}
input,select,textarea{background:#FCF9F2!important;color:var(--ink)!important;border-color:var(--line-strong)!important;border-radius:var(--sketch-radius)!important;box-shadow:inset 0 1px 1px rgba(74,58,45,.035)!important}
input:focus,select:focus,textarea:focus{outline:none!important;border-color:var(--craft)!important;box-shadow:0 0 0 2px rgba(168,95,50,.10),inset 0 1px 1px rgba(74,58,45,.035)!important}
.sideTab,.workspaceDockTabs button{background:transparent!important;color:var(--muted)!important;border:0!important;border-bottom:1px solid transparent!important;border-radius:0!important;box-shadow:none!important}
.sideTab.active,.workspaceDockTabs button.active{color:var(--ink)!important;background:rgba(199,120,61,.055)!important;border-bottom:2px solid var(--craft)!important}
#workspaceDock button:not(.workspaceDockTabs button),.left button:not(.sideTab),.right button,.mobileSidebar button:not(.sideTab),button.historyAddPartButton{border-color:var(--line-strong)!important;border-radius:var(--sketch-radius)!important}
#workspaceDock .seg button,#workspaceDock .edgeBtn,#workspaceDock .toggleBtn,#workspaceDock .innerBoxButtons button,#workspaceDock .jointTextChoices button,#workspaceDock .step button,.left .seg button,.left .edgeBtn,.left .toggleBtn,.left .step button,.mobileSidebar .seg button,.mobileSidebar .edgeBtn,.mobileSidebar .toggleBtn,.mobileSidebar .step button{background:#FCF9F2!important;color:var(--ink)!important;border:1px solid var(--line-strong)!important;box-shadow:0 2px 4px rgba(74,58,45,.09)!important;transition:transform .08s ease,box-shadow .08s ease,background .12s ease,border-color .12s ease!important}
#workspaceDock .seg button.active,#workspaceDock .edgeBtn.on,#workspaceDock .toggleBtn.on,#workspaceDock .innerBoxButtons button.active,#workspaceDock .jointTextChoices button.active,.left .seg button.active,.left .edgeBtn.on,.left .toggleBtn.on,.mobileSidebar .seg button.active,.mobileSidebar .edgeBtn.on,.mobileSidebar .toggleBtn.on{color:var(--craft-deep)!important;border-color:var(--craft)!important;background-color:#EAD8C5!important;background-image:repeating-linear-gradient(135deg,rgba(168,95,50,.055) 0 1px,transparent 1px 5px)!important;box-shadow:0 2px 5px rgba(74,58,45,.13)!important}
#workspaceDock .addButtons button[id],.left button.structureAddButton,.mobileSidebar button.structureAddButton,#rightHistorySection button.historyAddPartButton{background:#FCF9F2!important;color:var(--craft-deep)!important;border:1px solid var(--craft)!important;box-shadow:var(--shadow-craft)!important}
#workspaceDock .addButtons button:hover,.left .structureAddButton:hover,.mobileSidebar .structureAddButton:hover,#rightHistorySection .historyAddPartButton:hover{background:var(--craft-soft)!important}
#workspaceDock button:active,.left button:active,.right button:active,.mobileSidebar button:active{transform:translateY(1px)!important;box-shadow:0 1px 2px rgba(74,58,45,.09)!important}
#workspaceDock .ghost.danger,#rightHistorySection .historyDeletePart{background:#FCF9F2!important;color:var(--danger)!important;border:1px solid rgba(184,92,92,.62)!important;box-shadow:0 2px 4px rgba(100,50,45,.07)!important}
.materialCard,.compositionCard,.historyItem,.regionDimensionRow,.innerBoxCard,.dockCard,.settingsCard{background:rgba(252,249,242,.82)!important;border-color:var(--line)!important;box-shadow:0 1px 3px rgba(74,58,45,.045)!important}
.historyItem.active,.materialCard.active,.compositionCard.active{border-color:var(--craft)!important;background:var(--craft-soft)!important}
.stage,.drawingStage,.modelStage,.workspaceCanvas,.canvasWrap{background:#FCF9F2!important}a,.accentText{color:var(--craft)!important}
.desktopNav .shellNavBtn.active{color:var(--craft)!important;background:var(--craft-soft)!important;box-shadow:inset 0 0 0 1px rgba(168,95,50,.10)!important}.mobileBottomNav .shellNavBtn.active{color:var(--craft)!important}
.centerSaveButton,.cutSaveButton{background:var(--craft-deep)!important;color:#FCF9F2!important;border-color:var(--craft-deep)!important;border-radius:var(--sketch-radius)!important;box-shadow:var(--shadow-craft)!important}.centerSaveButton:active,.cutSaveButton:active{transform:translateY(1px)!important}
'''
if '</style>' not in s: raise SystemExit('style end missing')
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
print('applied v79 Sketch Craft')
