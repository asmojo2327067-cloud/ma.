"""Exercise the original application's unit, part, 3D, material and cutting flow."""
import json,sys,threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
APP=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'index.html'
FIXTURE=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'tests/fixtures/drawing-parts.json'
b=json.loads(FIXTURE.read_text())
if 'design' not in b:
 b['design']={'outer':{'W':2000,'H':2000,'D':585},'source':'合成外寸','parts':{'G007':{'axes':['x','z','y'],'instances':[{'x':'150','y':'502-35','z':'0'}],'source':'合成位置'}}}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(APP.parent)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/{APP.name}'
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1680,'height':1050})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url,wait_until='load')
 legacy=page.evaluate('''() => {const p=createProjectObject('既存設計との接続検証');p.units=[snapshot()];p.units[0].id='old';saveProject(p);openProject(p.id);setProjectTab('drawings');return p;}''')
 page.locator('#drawingPartsFile').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(b,ensure_ascii=False).encode()})
 page.locator('[data-dp-part="G007"]').wait_for()
 page.locator('#dpNativeImport').click(timeout=3000)
 native_id=f"DW_{b['source']['sha256'][:12]}_G007"
 page.locator(f'[data-history-key="part:{native_id}"]').wait_for(timeout=5000)
 page.locator(f'[data-history-key="part:{native_id}"]').click()
 assert page.locator('#historyGenericLength').input_value()=='940'
 assert page.locator('#historyNativeThickness').input_value()=='20'
 data=page.evaluate('''() => ({p:activeProject(),rows:formulas(),model:build3DParts(),snapshot:snapshot()})''')
 assert data['p']['units'][0]==legacy['units'][0]
 assert len(data['rows'])==len(b['parts'])
 assert sum(p['qty'] for p in data['rows'])==sum(p['qty'] for p in b['parts'])
 assert not any(p['id'] in ['LEFT','RIGHT','TOP','BOTTOM','BACKBOARD'] for p in data['rows'])
 assert any(p['partId']==native_id for p in data['model']['parts'])
 assert data['snapshot']['structure']['drawingLayout']['sourceHash']==b['source']['sha256']
 # Invalid quantity is rejected before it can reach placement rendering.
 qty=page.locator('#historyGenericQty').input_value()
 page.locator('#historyGenericQty').fill('1e309')
 assert page.locator('#historyGenericQty').get_attribute('aria-invalid')=='true'
 assert page.evaluate('formulas().find(p=>p.drawingSource.partId==="G007").qty')==int(qty)
 page.locator('#historyGenericQty').fill(qty)
 page.locator('#historyGenericDepth').click()
 # Native dimension edits, Undo/Redo and persistence.
 page.locator('#historyGenericLength').fill('900')
 page.locator('#historyGenericDepth').click()
 page.locator('#nativeUndo').click()
 assert page.locator('#historyGenericLength').input_value()=='940'
 page.locator('#nativeRedo').click()
 assert page.locator('#historyGenericLength').input_value()=='900'
 page.evaluate('saveCurrentUnitIntoProject({silent:true})')
 unit_id=data['snapshot']['id']
 page.reload(wait_until='load')
 page.evaluate('v => {openProject(v.p);openProjectUnit(v.u);}',{'p':legacy['id'],'u':unit_id})
 page.locator(f'[data-history-key="part:{native_id}"]').click()
 assert page.locator('#historyGenericLength').input_value()=='900'
 # Known material is assigned through the original inspector, not a parallel list.
 page.evaluate('''() => {cutState.materials.push({id:'TEST20',type:'custom',name:'合成テスト板20',thickness:20,species:'',grain:'none',sheets:['custom'],customW:2400,customH:1200,color:'#ddd'});cutState.patterns.push({id:'TESTP20',name:'合成20mm単板',cores:[{materialId:'TEST20',count:1}],face:null,back:null});renderHistoryEditor();}''')
 page.locator('#historyGenericPattern').select_option('TESTP20')
 page.locator('#historyGenericGrain').select_option('none')
 page.evaluate('saveCurrentUnitIntoProject({silent:true});showProjectCutting();')
 assert page.locator('#cutPartKinds').inner_text()==str(len(b['parts'])+5) # legacy automatic box still present
 assert str(sum(p['qty'] for p in b['parts'])+5) in page.locator('#cutTotalQty').inner_text()
 page.locator('#runCutting').click()
 result=page.evaluate('lastCutResult')
 pieces=[p for r in result['results'] for p in r['pieces'] if p['partId']==native_id]
 assert len(pieces)==1 and pieces[0]['finishL']==900 and pieces[0]['finishW']==545
 assert any('寸法未確定' in e or '材料構成未設定' in e for e in result['errors'])
 # Drawing link opens the corresponding G number, and reimport preserves edits.
 page.evaluate('id=>openProjectUnit(id)',unit_id)
 page.locator(f'[data-history-key="part:{native_id}"]').click()
 page.locator('#nativeSourceDrawing').click()
 assert page.locator('#dpPartId').inner_text()=='G007'
 page.locator('#dpNativeImport').click()
 page.locator(f'[data-history-key="part:{native_id}"]').click()
 assert page.locator('#historyGenericLength').input_value()=='900'
 # Undo histories must not cross projects containing the same source/unit IDs.
 page.evaluate('''b=>{let p=createProjectObject('別案件の履歴検証');p=MakeItFitDrawingNative.importBundle(p,b);p.units[0].structure.customParts.find(x=>x.drawingSource.partId==='G007').lengthFormula='800';saveProject(p);openProject(p.id);openProjectUnit(p.units[0].id);}''',b)
 page.locator(f'[data-history-key="part:{native_id}"]').click()
 assert page.locator('#historyGenericLength').input_value()=='800'
 assert page.locator('#nativeUndo').is_disabled()
 page.locator('#historyGenericLength').fill('750')
 page.locator('#historyGenericDepth').click()
 page.locator('#nativeUndo').click()
 assert page.locator('#historyGenericLength').input_value()=='800'
 assert not errors,errors
 browser.close();server.shutdown()
 print(json.dumps({'native_flow':'passed','parts':len(b['parts']),'quantity':sum(p['qty'] for p in b['parts']),'page_errors':errors}))
