from pathlib import Path

p=Path("index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        if new in s:
            return
        raise SystemExit(f"missing target: {label}")
    s=s.replace(old,new,1)

rep("<title>ma.｜案件 v80</title>","<title>ma.｜案件 v81</title>","title")
rep("version:80,","version:81,","version")
rep('data-build="ma-project-v80"','data-build="ma-project-v81"',"build")
rep('const WORKSPACE_DOCK_KEY="maWorkspaceDockV80"','const WORKSPACE_DOCK_KEY="maWorkspaceDockV81"',"dock")

rep("""      <button data-view="diagram" class="active">構造図</button>
      <button data-view="three">3D</button>""","""      <button data-view="diagram" class="active">構造図</button>
      <button data-view="sketch">スケッチ</button>
      <button data-view="three">3D</button>""","view-tabs")

rep("""      <div id="threeView" class="hidden">""",'      <div id="sketchView" class="hidden">\n        <div class="cardHead">\n          <div>\n            <strong>スケッチ</strong>\n            <div class="handSub">the original sketch craft image.</div>\n          </div>\n          <span>参考イラスト / 計算とは独立</span>\n        </div>\n        <div class="sketchReferenceStage">\n          <div class="sketchReferencePaper">\n            <img id="sketchCraftCabinetImage" src="assets/sketch-craft-cabinet.jpg" alt="Sketch Craft 家具スケッチ">\n          </div>\n          <div class="sketchReferenceNote">\n            <span class="sketchReferenceArrow">↳</span>\n            <span>画像案で使った家具スケッチを、そのまま表示しています。</span>\n          </div>\n        </div>\n      </div>\n\n'+"""      <div id="threeView" class="hidden">""","sketch-view")

rep("""  $("diagramView").classList.toggle("hidden",state.view!=="diagram");
  $("threeView").classList.toggle("hidden",state.view!=="three");
  if(state.view==="three"){""","""  $("diagramView").classList.toggle("hidden",state.view!=="diagram");
  $("sketchView").classList.toggle("hidden",state.view!=="sketch");
  $("threeView").classList.toggle("hidden",state.view!=="three");
  if(state.view==="three"){""","view-switch")

rep("""<div id="mobileOverflowMenu" class="mobileOverflowMenu" hidden>
  <button type="button" data-mobile-menu-action="save">ユニットを保存</button>""","""<div id="mobileOverflowMenu" class="mobileOverflowMenu" hidden>
  <button type="button" data-mobile-menu-action="sketch">スケッチを見る</button>
  <button type="button" data-mobile-menu-action="save">ユニットを保存</button>""","mobile-menu")

rep("""  if(action==="save"){
    document.getElementById("savePattern")?.click();
    return;
  }""","""  if(action==="sketch"){
    document.querySelector('.viewTabs [data-view="sketch"]')?.click();
    return;
  }
  if(action==="save"){
    document.getElementById("savePattern")?.click();
    return;
  }""","mobile-handler")

if "v81 / Sketch Craft reference image" not in s:
    s=s.replace("</style>",'\n/* ===== v81 / Sketch Craft reference image ===== */\n.viewTabs{grid-template-columns:repeat(3,1fr)!important}\nbody:not(.page-home):not(.page-cut):not(.page-project) #sketchView{flex:1 1 auto;min-height:0;overflow:hidden}\nbody:not(.page-home):not(.page-cut):not(.page-project) #sketchView:not(.hidden){display:flex;flex-direction:column}\n#sketchView .cardHead{flex:0 0 auto}\n.sketchReferenceStage{\n  flex:1 1 auto;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;\n  gap:11px;padding:18px 24px 22px;\n  background:linear-gradient(rgba(111,86,61,.018) 1px,transparent 1px),\n             linear-gradient(90deg,rgba(111,86,61,.018) 1px,transparent 1px),#FCF9F2;\n  background-size:30px 30px;\n}\n.sketchReferencePaper{\n  display:flex;align-items:center;justify-content:center;width:min(440px,70%);aspect-ratio:390/380;padding:10px;\n  background:#FCF9F2;border:1px solid #D7CCBE;border-radius:5px 8px 6px 4px;\n  box-shadow:0 10px 18px rgba(76,58,43,.13),0 2px 4px rgba(76,58,43,.08);transform:rotate(-.18deg);\n}\n#sketchCraftCabinetImage{display:block;width:100%;height:100%;object-fit:contain;filter:none!important;mix-blend-mode:normal!important;opacity:1!important}\n.sketchReferenceNote{\n  display:flex;align-items:center;gap:7px;max-width:440px;color:#6F675F;\n  font-family:"Segoe Print","Bradley Hand","Comic Sans MS",cursive;font-size:10px;line-height:1.45;transform:rotate(-.45deg)\n}\n.sketchReferenceArrow{font-size:15px;color:#A85F32}\n@media(max-width:760px){\n  .viewTabs{grid-template-columns:repeat(3,1fr)!important}\n  body:not(.page-home):not(.page-cut):not(.page-project) #sketchView{overflow:visible}\n  .sketchReferenceStage{min-height:430px;padding:16px 14px 20px}\n  .sketchReferencePaper{width:min(340px,92%);padding:8px}\n  .sketchReferenceNote{max-width:340px;font-size:9px}\n}\n'+"\n</style>",1)

p.write_text(s,encoding="utf-8")
