from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def rep(old,new,label):
    global s
    if old not in s:
        if new in s:return
        raise SystemExit('missing '+label)
    s=s.replace(old,new,1)
rep('<title>ma.｜案件 v82</title>','<title>ma.｜案件 v83</title>','title')
rep('version:82,','version:83,','version')
rep('data-build="ma-project-v82"','data-build="ma-project-v83"','build')
rep('const WORKSPACE_DOCK_KEY="maWorkspaceDockV82"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV83"','dock')
for n in ('normal','selected','primary','danger'):
    s=s.replace(f'assets/btn-{n}.svg',f'assets/btn-{n}.svg?v=83')
css='''\n/* ===== v83 / visibly rough Sketch Craft buttons ===== */\n#workspaceDock .seg button,#workspaceDock .edgeBtn,#workspaceDock .toggleBtn,#workspaceDock .innerBoxButtons button,#workspaceDock .jointTextChoices button,#workspaceDock .step button,.left .seg button,.left .edgeBtn,.left .toggleBtn,.left .step button,.right .seg button,.right .edgeBtn,.right .toggleBtn,.right .step button,.mobileSidebar .seg button,.mobileSidebar .edgeBtn,.mobileSidebar .toggleBtn,.mobileSidebar .step button,#workspaceDock .addButtons button[id],.left button.structureAddButton,.mobileSidebar button.structureAddButton,#rightHistorySection button.historyAddPartButton,#workspaceDock .ghost.danger,#rightHistorySection .historyDeletePart{min-height:34px!important;height:34px!important;padding:4px 11px 6px!important;background-size:100% 100%!important;background-position:center!important;background-repeat:no-repeat!important}\n'''
if 'v83 / visibly rough Sketch Craft buttons' not in s:
    s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf-8')
