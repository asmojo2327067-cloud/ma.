const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const core=require('../assets/drawing-native-core.js');
function harness(){
  const b=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/drawing-parts.json')));
  b.design={outer:{W:2000,H:2000,D:585},parts:{G007:{axes:['x','z','y'],instances:[{x:'0',y:'0',z:'0'}]}}};
  const unit=core.importBundle({id:'A',units:[]},b).units[0],elements=new Map();
  function el(id){if(!elements.has(id))elements.set(id,{events:{},addEventListener(k,fn){this.events[k]=fn;},append(section){this.html=section.innerHTML;},querySelectorAll(){return[];}});return elements.get(id);}
  const stateFor=()=>({customParts:structuredClone(unit.structure.customParts),partNames:{},partGrain:{},overrides:{},outer:unit.structure.outerPreview,drawingLayout:unit.structure.drawingLayout,selectedPartId:unit.structure.customParts[0].id});
  const ctx={window:{MakeItFitDrawingNative:core},state:stateFor(),cutState:{partPatterns:{}},currentUnitId:unit.id,currentProjectId:'A',document:{getElementById:el,createElement:()=>({querySelectorAll:()=>[]})},escapeAttr:String,formulas:()=>ctx.state.customParts,partGrainMode:()=> 'unset',patternFinishThickness:()=>0,getCutPattern:()=>null,update(){},invalidateCutResult(){},saveCurrentUnitIntoProject(){},queueMicrotask:fn=>fn()};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/drawing-native-ui.js'),'utf8'),ctx);
  return{ctx,el,stateFor,enhance:()=>ctx.window.MakeItFitDrawingNativeUI.enhanceEditor(ctx.state.customParts[0])};
}
test('同じ図面IDでも別案件のUndoが部材寸法を上書きしない',()=>{
  const{ctx,el,stateFor,enhance}=harness();enhance();
  el('historyEditor').events.focusin({target:{matches:()=>true}});
  ctx.state.customParts[0].lengthFormula='900';el('historyEditor').events.change({target:{matches:()=>true}});
  ctx.currentProjectId='B';ctx.state=stateFor();ctx.state.customParts[0].lengthFormula='800';ctx.cutState={partPatterns:{}};enhance();
  el('nativeUndo').events.click();assert.equal(ctx.state.customParts[0].lengthFormula,'800');
  el('historyEditor').events.focusin({target:{matches:()=>true}});ctx.state.customParts[0].lengthFormula='750';el('historyEditor').events.change({target:{matches:()=>true}});
  el('nativeUndo').events.click();assert.equal(ctx.state.customParts[0].lengthFormula,'800');
});
test('大きい使用枚数でも配置欄は100枚以内で描画する',()=>{
  const{ctx,el,enhance}=harness();ctx.state.customParts[0].qty=1000000;enhance();
  assert.equal((el('historyEditor').html.match(/data-native-position=/g)||[]).length,300);
  assert.equal(ctx.state.customParts[0].qty,1000000);
});
test('既存数量入力にInfinityとなる文字を入れても保存値を壊さない',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  const code=html.slice(html.indexOf('    const syncCustomQty=e=>{'),html.indexOf('    $("historyGenericQty")?.addEventListener("input",syncCustomQty);'));
  const p={id:'P',qty:2,drawingSource:{}},ctx={state:{customParts:[p]},part:p,window:{MakeItFitDrawingNative:core},invalidateCutResult(){},refreshActiveHistorySummary(){},scheduleUnitAutoSave(){}};
  vm.runInNewContext(code+';globalThis.handler=syncCustomQty;',ctx);
  const target={value:'1e309',setAttribute(k,v){this[k]=v;}};
  ctx.handler({target});assert.equal(p.qty,2);assert.equal(target['aria-invalid'],'true');
  target.value='4';ctx.handler({target});assert.equal(p.qty,4);assert.equal(target['aria-invalid'],'false');
});
test('外寸の手入力で確定した軸だけを式に使用し、残りは未確定に保つ',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  const code=html.slice(html.indexOf('function resolveOuterDimension('),html.indexOf('function newRegion()'));
  const inputs=Object.fromEntries(['W','H','D'].map(k=>[k,{value:`外寸${k}`,classList:{toggle(){}},setAttribute(){}}]));
  const ctx={state:{drawingLayout:{},outer:{W:940,H:940,D:940,drawingKnownAxes:{W:false,H:false,D:false}}},$:k=>inputs[k],formatFinishedMm:String};
  vm.runInNewContext(code,ctx);ctx.readOuter();
  assert.equal(core.evaluate('W-20',[],ctx.state.outer),null);
  inputs.W.value='900';ctx.readOuter();assert.equal(core.evaluate('W-20',[],ctx.state.outer),880);
  assert.equal(core.evaluate('H-20',[],ctx.state.outer),null);
});
