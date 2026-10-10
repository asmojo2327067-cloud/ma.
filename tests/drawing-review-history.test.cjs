const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const core=require('../assets/drawing-parts-core.js');
test('図面側のUndo/Redoで寸法とXYZ方向を一緒に復元する',()=>{
  const b=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/drawing-parts.json')));
  b.design={parts:{G007:{axes:['x','z','y'],instances:[]}}};
  let project=core.addBundle({id:'A'},b),elements=new Map();
  function el(id){if(!elements.has(id))elements.set(id,{value:'',events:{},classList:{toggle(){}},addEventListener(k,fn){this.events[k]=fn;}});return elements.get(id);}
  const ctx={window:{MakeItFitDrawingParts:core},document:{getElementById:el},activeProject:()=>structuredClone(project),saveProject:p=>project=structuredClone(p),renderProjectView(){}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/drawing-parts-ui.js'),'utf8'),ctx);
  ctx.window.MakeItFitDrawingUI.render(project);
  const fields=()=>{const p=project.drawingParts.bundles[0].parts[0];['dpLength','dpWidth','dpThickness'].forEach((id,i)=>el(id).value=String(p.dims[i].display));el('dpQuantity').value=String(p.qty);el('dpNote').value=p.note||'';};
  const click=id=>el('drawingPartsRoot').events.click({target:{closest:()=>({id,dataset:{},hasAttribute:()=>false})}});
  fields();el('dpLength').value='100';el('drawingPartsRoot').events.submit({preventDefault(){}});
  assert.deepEqual(project.drawingParts.bundles[0].design.parts.G007.axes,['z','x','y']);
  fields();click('dpUndo');
  assert.equal(project.drawingParts.bundles[0].parts[0].dims[0].result,940);
  assert.deepEqual(project.drawingParts.bundles[0].design.parts.G007.axes,['x','z','y']);
  fields();click('dpRedo');
  assert.equal(project.drawingParts.bundles[0].parts[0].dims[0].result,545);
  assert.deepEqual(project.drawingParts.bundles[0].design.parts.G007.axes,['z','x','y']);
});
