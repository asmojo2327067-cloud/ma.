from pathlib import Path
import re
p=Path('index.html')
html=p.read_text(encoding='utf-8')

def once(old,new,label):
    global html
    if old not in html:
        raise SystemExit(f'{label}: target missing')
    html=html.replace(old,new,1)

once('<title>ma.｜案件 v89</title>','<title>ma.｜案件 v91</title>','title')
once('version:89,','version:91,','version')
once('data-build="ma-project-v89"','data-build="ma-project-v91"','build')
once('const WORKSPACE_DOCK_KEY="maWorkspaceDockV89"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV91"','dock')

rlistener='''  g.querySelectorAll("[data-region]").forEach(el=>el.addEventListener("click",e=>{\n    e.stopPropagation();\n    state.selected=el.dataset.region;\n    update();\n    openContextSettings({\n      tab:"region",\n      title:`区画 ${el.dataset.region}`,\n      hint:"この区画だけの分割・位置・内背板を編集します。"\n    });\n  }));'''
if rlistener in html:
    html=html.replace(rlistener,'  // v90: illustration is display-only. No region click/tap interaction.',1)
for plistener in [
'''  g.querySelectorAll("[data-part-id]").forEach(el=>el.addEventListener("click",e=>{\n    e.stopPropagation();\n    setSelectedPart(el.dataset.partId,{rerenderFormula:true});\n  }));''',
'''  g.querySelectorAll("[data-part-id]").forEach(el=>el.addEventListener("click",e=>{\n    e.stopPropagation();\n    setSelectedPart(el.dataset.partId);\n  }));''']:
    if plistener in html:
        html=html.replace(plistener,'  // v90: illustration is display-only. No part click/tap interaction.',1)
        break

once('<button type="button" data-workspace-dock-tab="region" role="tab">区画</button>',
     '<button type="button" data-workspace-dock-tab="region" role="tab">棚・束</button>','tab')
html=html.replace('region:["区画","選択中の区画だけを編集します。"]',
                  'region:["棚・束","選択中の区画に棚・束を追加・配置します。"]',1)
html=html.replace('図面の部材や区画をタップすると、その設定を開きます。','設定は下のタブから選びます。',1)

region_start=html.find('data-workspace-dock-panel="region"')
start=html.find('    <div class="innerBackControls">',region_start)
if start<0: raise SystemExit('inner start missing')
token_re=re.compile(r'<div\b[^>]*>|</div>')
depth=0; end=None
for m in token_re.finditer(html,start):
    if m.group(0).startswith('<div'):
        depth+=1
    else:
        depth-=1
        if depth==0:
            end=m.end(); break
if end is None: raise SystemExit('inner end missing')
block=html[start:end]
html=html[:start]+html[end:]

back_start=html.find('data-workspace-dock-panel="backboard"')
anchor='    </div>\n  </div>\n            </div>\n          </section>'
pos=html.find(anchor,back_start)
if pos<0: raise SystemExit('back anchor missing')
moved='''    <div class="innerBackMoved">\n      <div class="dockSubSectionTitle">\n        <strong>内背</strong>\n        <span>選択区画ごと</span>\n      </div>\n'''+block+'''\n    </div>\n'''
html=html[:pos]+moved+html[pos:]

css='''\n/* ===== ma. v90 / illustration is display-only ===== */
#cabinet,#cabinet *,#sketchView,#sketchView *{pointer-events:none!important;cursor:default!important;}
/* ===== ma. v91 / inner backboard belongs to Backboard tab ===== */
#leftBackboardSection .innerBackMoved{margin-top:12px;padding-top:10px;border-top:1px solid var(--lineSoft);}
#leftBackboardSection .dockSubSectionTitle{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:7px;}
#leftBackboardSection .dockSubSectionTitle strong{font-size:11px;color:var(--ink);}
#leftBackboardSection .dockSubSectionTitle span{font-size:8px;color:var(--muted);}
#leftBackboardSection .innerBackControls{margin-top:0!important;}
'''
style_end=html.rfind('</style>')
if style_end<0: raise SystemExit('style end missing')
html=html[:style_end]+css+'\n'+html[style_end:]

region=html[html.find('data-workspace-dock-panel="region"'):html.find('data-workspace-dock-panel="joint"')]
back=html[html.find('data-workspace-dock-panel="backboard"'):html.find('</main>')]
if 'id="innerBackToggle"' in region: raise SystemExit('inner still in region')
if 'id="innerBackToggle"' not in back: raise SystemExit('inner missing back')
if html.count('id="innerBackToggle"')!=1: raise SystemExit('inner duplicate')
p.write_text(html,encoding='utf-8')
