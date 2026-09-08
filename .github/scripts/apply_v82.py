from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        if new in s:
            return
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

rep('<title>ma.｜案件 v81</title>','<title>ma.｜案件 v82</title>','title')
rep('version:81,','version:82,','version')
rep('data-build="ma-project-v81"','data-build="ma-project-v82"','build')
rep('const WORKSPACE_DOCK_KEY="maWorkspaceDockV81"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV82"','dock')

css=r'''\n/* ===== v82 / image-button system ===== */\n:root{\n  --btn-img-normal:url("assets/btn-normal.svg");\n  --btn-img-selected:url("assets/btn-selected.svg");\n  --btn-img-primary:url("assets/btn-primary.svg");\n  --btn-img-danger:url("assets/btn-danger.svg");\n}\n#workspaceDock .seg button,#workspaceDock .edgeBtn,#workspaceDock .toggleBtn,#workspaceDock .innerBoxButtons button,#workspaceDock .jointTextChoices button,#workspaceDock .step button,.left .seg button,.left .edgeBtn,.left .toggleBtn,.left .step button,.right .seg button,.right .edgeBtn,.right .toggleBtn,.right .step button,.mobileSidebar .seg button,.mobileSidebar .edgeBtn,.mobileSidebar .toggleBtn,.mobileSidebar .step button,.ghost{background-color:transparent!important;background-image:var(--btn-img-normal)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;border:0!important;box-shadow:none!important;color:#2D2925!important}\n#workspaceDock .seg button.active,#workspaceDock .edgeBtn.on,#workspaceDock .toggleBtn.on,#workspaceDock .innerBoxButtons button.active,#workspaceDock .jointTextChoices button.active,.left .seg button.active,.left .edgeBtn.on,.left .toggleBtn.on,.right .seg button.active,.right .edgeBtn.on,.right .toggleBtn.on,.mobileSidebar .seg button.active,.mobileSidebar .edgeBtn.on,.mobileSidebar .toggleBtn.on{background-image:var(--btn-img-selected)!important;color:#874722!important}\n#workspaceDock .addButtons button[id],.left button.structureAddButton,.mobileSidebar button.structureAddButton,#rightHistorySection button.historyAddPartButton,.homePrimaryAction,.projectPrimaryButton{background-color:transparent!important;background-image:var(--btn-img-primary)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;border:0!important;box-shadow:none!important;color:#874722!important}\n#workspaceDock .ghost.danger,#rightHistorySection .historyDeletePart,.projectDangerButton{background-color:transparent!important;background-image:var(--btn-img-danger)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;border:0!important;box-shadow:none!important;color:#B85C5C!important}\n.centerSaveButton,.cutSaveButton,.cutGenerateButton{background-color:transparent!important;background-image:var(--btn-img-selected)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;border:0!important;box-shadow:none!important;color:#874722!important}\n#workspaceDock button,.left button,.right button,.mobileSidebar button{background-origin:border-box!important;background-clip:border-box!important}\n'''

if 'v82 / image-button system' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

p.write_text(s,encoding='utf-8')
