const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const file = path.join(__dirname,'../assets/drawing-native-core.js');
const native = fs.existsSync(file) ? require(file) : {};
function api(name) { assert.equal(typeof native[name],'function',`${name}: 既存設計への接続が未実装`); return native[name]; }
function bundle() {
  const b=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/drawing-parts.json')));
  b.parts=b.parts.slice(0,2); b.parts[0].qty=2;
  b.views.forEach(v=>v.marks=v.marks.filter(m=>b.parts.some(p=>p.id===m.id)));
  b.productionUnits=18;
  b.design={outer:{W:2000,H:2000,D:585},source:'合成外寸',parts:{
    G007:{axes:['x','z','y'],instances:[{x:'150',y:'502-35',z:'0'},{x:'W-940',y:'502-35',z:'0'}],source:'合成位置'},
    G010:{axes:['z','y','x'],instances:[{x:'150',y:'230',z:'0'}],source:'合成未確定部材'}
  }};
  return b;
}
test('既存設計部材に取り込み、旧ユニットと材料を保持する',()=>{
  const p={id:'p',units:[{id:'old',structure:{old:true}}],materials:[{id:'M'}],materialPatterns:[{id:'P'}],cutting:{lastResult:{old:true}}};
  const before=JSON.stringify(p),next=api('importBundle')(p,bundle());
  assert.equal(JSON.stringify(p),before);
  assert.deepEqual(next.units[0],p.units[0]);assert.deepEqual(next.materials,p.materials);
  const u=next.units[1];
  assert.equal(u.structure.customParts.length,2);assert.equal(u.structure.parts.length,2);
  assert.equal(u.structure.parts[0].drawingSource.partId,'G007');
  assert.equal(u.structure.parts[0].thicknessFormula,'20');
  assert.equal(u.structure.parts[0].qty,2);assert.equal(u.structure.drawingLayout.productionUnits,18);
  assert.deepEqual(u.cutting.partPatterns,{});
});
test('同じ図面の再取込で元アプリの編集を上書きしない',()=>{
  const p=api('importBundle')({id:'p',units:[]},bundle());
  p.units[0].structure.customParts[0].lengthFormula='900';
  assert.deepEqual(api('importBundle')(p,bundle()),p);
});
test('実寸と位置式で各枚の3Dを生成し、未確定部材に18mmを入れない',()=>{
  const u=api('importBundle')({id:'p',units:[]},bundle()).units[0];
  const g=api('geometry')(u.structure.customParts,u.structure.outerPreview);
  assert.equal(g.solids.length,2);
  assert.equal(g.solids[0].x0,150);assert.equal(g.solids[0].y0,467);assert.equal(g.solids[0].z0,0);
  assert.equal(g.solids[0].x1,1090);assert.equal(g.solids[0].y1,487);assert.equal(g.solids[0].z1,545);
  assert.equal(g.solids[1].x0,1060);
  assert.match(g.issues.join(' '),/G010.*寸法/);
  assert.equal(api('dimensions')(u.structure.parts[1],u.structure.parts,u.structure.outerPreview)[2],null);
});
test('座標の0は許可し、寸法の0とコード・循環参照は拒否する',()=>{
  const ev=api('evaluate');const rows=[];const outer={W:900,H:850,D:450};
  assert.equal(ev('0',rows,outer,true),0);assert.equal(ev('W/2-10',rows,outer),440);
  assert.equal(ev('0',rows,outer),null);assert.equal(ev('globalThis.process.exit(1)',rows,outer,true),null);
  rows.push({id:'A',lengthFormula:'[B#B:①]',depthFormula:'20',thicknessFormula:'18',drawingSource:{}},{id:'B',lengthFormula:'[A#A:①]',depthFormula:'20',thicknessFormula:'18',drawingSource:{}});
  assert.equal(ev('[A#A:①]',rows,outer),null);
});
test('未知の厚みを参照しても既存の既定板厚へ置換しない',()=>{
  const rows=[{id:'A',thicknessFormula:'箱板厚',drawingSource:{}},{id:'B',lengthFormula:'500-[側#A:厚]',depthFormula:'50',thicknessFormula:'20',drawingSource:{}}];
  assert.equal(api('dimensions')(rows[1],rows,{W:500,H:900,D:450})[0],null);
});
test('木取りは未設定材料・未確定寸法・厚み不一致を理由付きで止める',()=>{
  const u=api('importBundle')({id:'p',units:[]},bundle()).units[0],p=u.structure.parts[0];
  assert.match(api('cutIssue')(p,u.structure.parts,u.structure.outerPreview,null),/材料構成/);
  assert.match(api('cutIssue')(p,u.structure.parts,u.structure.outerPreview,18),/厚み/);
  assert.match(api('cutIssue')(p,u.structure.parts,u.structure.outerPreview,20),/木目/);
  p.grainMode='none';
  assert.equal(api('cutIssue')(p,u.structure.parts,u.structure.outerPreview,20),'');
  assert.match(api('cutIssue')(u.structure.parts[1],u.structure.parts,u.structure.outerPreview,20),/寸法/);
});
test('不正な配置情報を案件に保存しない',()=>{
  const imp=api('importBundle');
  const b=bundle();b.design.parts.G007.axes=['x','x','z'];
  assert.throws(()=>imp({id:'p',units:[]},b));
});
test('未入力の配置行を0位置にせず、入力済みの別の枚は表示する',()=>{
  const u=api('importBundle')({id:'p',units:[]},bundle()).units[0],p=u.structure.customParts[0];
  p.placement.instances[0]=null;
  const g=api('geometry')([p],u.structure.outerPreview);
  assert.equal(g.solids.length,1);
  assert.match(g.issues.join(' '),/位置/);
});
test('数値が図面に見えても未確定の単体寸法を確定値に昇格しない',()=>{
  const b=bundle();b.parts[0].dims[2].result=null;b.parts[0].dims[2].method='単体板厚未確認';
  const u=api('importBundle')({id:'p',units:[]},b).units[0];
  assert.equal(api('dimensions')(u.structure.parts[0],u.structure.parts,u.structure.outerPreview)[2],null);
  assert.equal(u.structure.parts[0].drawingSource.dimensions[2].display,20);
});
test('外寸が未設定なら仮の表示範囲をWの確定値として式に使わない',()=>{
  const b=bundle();delete b.design.outer;b.parts[1].dims[0]={display:'W-20',result:null};
  b.parts[1].dims[1]={display:100,result:100};b.parts[1].dims[2]={display:20,result:20};
  b.design.parts.G010={axes:['x','y','z'],instances:[{x:'0',y:'0',z:'0'}]};
  const u=api('importBundle')({id:'p',units:[]},b).units[0];
  assert.equal(api('dimensions')(u.structure.parts[1],u.structure.parts,u.structure.outerPreview)[0],null);
  assert.equal(api('geometry')(u.structure.parts,u.structure.outerPreview).solids.filter(p=>p.partId.endsWith('G010')).length,0);
});
test('図面側の寸法並べ替えでもXYZ方向を同時に移す',()=>{
  const core=require('../assets/drawing-parts-core.js');
  const b=core.editPart(bundle(),'G007',{dimensions:['100','545','20'],qty:2,note:''});
  const u=api('importBundle')({id:'p',units:[]},b).units[0];
  const p=u.structure.parts[0],g=api('geometry')([p],u.structure.outerPreview).solids[0];
  assert.deepEqual(p.placement.axes,['z','x','y']);
  assert.equal(g.x1-g.x0,100);assert.equal(g.z1-g.z0,545);
});
test('数量は有限の上限付き整数として扱う',()=>{
  const valid=api('validQuantity');
  for(const v of [Infinity,NaN,0,-1,1.5,1000001])assert.equal(valid(v),false);
  assert.equal(valid(4),true);
});
test('図面側で枚数を減らすと対応する配置だけを取り込む',()=>{
  const core=require('../assets/drawing-parts-core.js');
  const b=core.editPart(bundle(),'G007',{dimensions:['940','545','20'],qty:1,note:''});
  const u=api('importBundle')({id:'p',units:[]},b).units[0];
  assert.equal(api('geometry')(u.structure.parts,u.structure.outerPreview).solids.length,1);
});
