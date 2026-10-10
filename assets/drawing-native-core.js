(function(root,factory){
  const api=factory(typeof module==='object'&&module.exports?require('./drawing-parts-core.js'):root.MakeItFitDrawingParts);
  if(typeof module==='object'&&module.exports)module.exports=api;else root.MakeItFitDrawingNative=api;
})(typeof globalThis==='object'?globalThis:this,function(core){
  'use strict';
  const copy=x=>JSON.parse(JSON.stringify(x));
  const keys=['lengthFormula','depthFormula','thicknessFormula'];
  const validQuantity=n=>Number.isSafeInteger(n)&&n>0&&n<=1000000;
  const idFor=(bundle,part)=>`DW_${bundle.source.sha256.slice(0,12)}_${part.id}`;
  function validateDesign(bundle){
    const design=bundle.design||{},ids=new Set(bundle.parts.map(p=>p.id));
    if(design.outer){for(const k of ['W','H','D'])if(!Number.isFinite(design.outer[k])||design.outer[k]<=0)throw new Error('図面の外寸が不正です。');}
    for(const [id,p] of Object.entries(design.parts||{})){
      if(!ids.has(id)||!p||!Array.isArray(p.axes)||p.axes.length!==3||p.axes.some(a=>a!=null&&!['x','y','z'].includes(a))||new Set(p.axes.filter(Boolean)).size!==p.axes.filter(Boolean).length)throw new Error('部材の取付方向が不正です。');
      if(!Array.isArray(p.instances)||p.instances.length>bundle.parts.find(x=>x.id===id).qty)throw new Error('配置枚数が使用枚数を超えています。');
      for(const pos of p.instances)for(const k of ['x','y','z'])if(!pos||!['string','number'].includes(typeof pos[k])||String(pos[k]).length>250)throw new Error('部材位置式が不正です。');
    }
    return design;
  }
  function dimensionFormula(d){
    if(d.result==null){try{if(core.readDimension(d.display).result!=null)return `未確定寸法（${d.display}）`;}catch(_){}return String(d.display);}
    if(d.formula){try{if(core.readDimension(d.formula).result===d.result)return d.formula;}catch(_){}}
    return String(d.result);
  }
  function importBundle(project,input){
    const bundle=core.validateBundle(input),design=validateDesign(bundle),next=copy(project);
    next.units=next.units||[];
    if(next.units.some(u=>u.structure?.drawingLayout?.sourceHash===bundle.source.sha256))return next;
    const outer=design.outer||Object.fromEntries(['W','H','D'].map(k=>[k,Math.max(100,...bundle.parts.flatMap(p=>p.dims.map(d=>d.result||0)))]));
    const parts=bundle.parts.map(p=>{
      const placement=design.parts?.[p.id]||{axes:[null,null,null],instances:[],source:'位置・方向未設定'};
      return{id:idFor(bundle,p),kind:'custom',name:`${p.id} ${p.name}`,qty:p.qty,dim2Label:'幅',grainMode:'unset',
        lengthFormula:dimensionFormula(p.dims[0]),depthFormula:dimensionFormula(p.dims[1]),thicknessFormula:dimensionFormula(p.dims[2]),placement:copy(placement),
        drawingSource:{bundleId:bundle.id,partId:p.id,sourceIds:p.sourceIds||[],zone:p.zone||'',dimensions:copy(p.dims),qty:p.qty,finish:p.finish||'',joints:p.joints||'',note:p.note||'',source:copy(bundle.source)},drawingNote:p.note||''};
    });
    const unit={version:92,id:`U-DW-${bundle.source.sha256.slice(0,16)}`,name:bundle.name,productionQuantity:bundle.productionUnits,
      structure:{outerPreview:{...copy(outer),drawingKnownAxes:Object.fromEntries(['W','H','D'].map(k=>[k,!!design.outer]))},outerFormula:Object.fromEntries(Object.entries(outer).map(([k,v])=>[k,design.outer?String(v):`外寸${k}`])),
        drawingLayout:{bundleId:bundle.id,sourceHash:bundle.source.sha256,productionUnits:bundle.productionUnits,outerSource:design.source||'表示範囲（外寸未設定）',outerConfirmed:!!design.outer},
        joints:{},plinth:{enabled:false},backboard:{enabled:false},innerBox:{top:'none',sides:'none',bottom:'none'},regionTree:{id:'R1',split:null},regionContents:{},
        customParts:copy(parts),parts:copy(parts),nextCustomPart:1,partNames:{},partGrain:{}},
      cutting:{materials:copy(next.materials||[]),patterns:copy(next.materialPatterns||[]),partPatterns:{},currentQuantity:bundle.productionUnits,additionalUnits:[],lastResult:null}};
    next.units.push(unit);if(next.cutting)next.cutting.lastResult=null;
    return next;
  }
  function evaluate(expr,rows,outer,coordinate=false,stack=[]){
    try{
      let e=String(expr??'');if(e.length>1000||stack.length>100)return null;
      e=e.replace(/\[([^#\]]+)#([A-Za-z0-9_-]+):(厚|①|②)\]/g,(_all,_label,id,axis)=>{
        const key=`${id}:${axis}`,ref=rows.find(p=>p.id===id);if(!ref||stack.includes(key))return '未確定';
        const v=evaluate(ref[keys[axis==='①'?0:axis==='②'?1:2]],rows,outer,false,[...stack,key]);return v==null?'未確定':`(${v})`;
      });
      e=e.replace(/\b(W|H|D)\b/g,(m)=>Number.isFinite(outer?.[m])&&outer?.drawingKnownAxes?.[m]!==false?String(outer[m]):'未確定');
      return core.readDimension(e,{coordinate}).result;
    }catch(_){return null;}
  }
  function dimensions(part,rows,outer){return keys.map(k=>evaluate(part[k],rows,outer));}
  function geometry(rows,outer){
    const solids=[],issues=[];
    for(const p of rows){
      if(!p.drawingSource)continue;
      const label=p.drawingSource.partId,dims=dimensions(p,rows,outer),place=p.placement||{};
      if(dims.some(d=>d==null)){issues.push(`${label}：寸法未確定`);continue;}
      if(!place.axes||place.axes.some(a=>!a)||new Set(place.axes).size!==3){issues.push(`${label}：取付方向未設定`);continue;}
      if((place.instances||[]).length<p.qty)issues.push(`${label}：位置未設定（${p.qty-(place.instances||[]).length}枚）`);
      for(const pos of place.instances||[]){
        const origin=['x','y','z'].map(k=>evaluate(pos?.[k],rows,outer,true));
        if(origin.some(d=>d==null)){issues.push(`${label}：位置式未確定`);continue;}
        const extent=Object.fromEntries(place.axes.map((a,i)=>[a,dims[i]]));
        solids.push({partId:p.id,type:'drawing',x0:origin[0],y0:origin[1],z0:origin[2],x1:origin[0]+extent.x,y1:origin[1]+extent.y,z1:origin[2]+extent.z});
      }
    }
    return{solids,issues};
  }
  function cutIssue(part,rows,outer,materialThickness){
    if(!validQuantity(part.qty))return '使用枚数が不正';
    const d=dimensions(part,rows,outer);
    if(d.some(v=>v==null))return '寸法未確定';
    if(!Number.isFinite(materialThickness)||materialThickness<=0)return '材料構成未設定';
    if(Math.abs(d[2]-materialThickness)>.01)return `厚み不一致（設計${d[2]}／材料構成${materialThickness}mm）`;
    if(part.grainMode==='unset')return '木目方向未設定';
    return '';
  }
  return{importBundle,idFor,evaluate,dimensions,geometry,cutIssue,validateDesign,validQuantity};
});
