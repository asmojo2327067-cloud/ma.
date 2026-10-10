(function(){
  'use strict';
  const core=window.MakeItFitDrawingNative,copy=x=>JSON.parse(JSON.stringify(x));
  const esc=escapeAttr,keys=['lengthFormula','depthFormula','thicknessFormula'];
  const histories=new Map();
  let baseline=null;
  const saved=()=>({customParts:copy(state.customParts),partNames:copy(state.partNames),partGrain:copy(state.partGrain),overrides:copy(state.overrides),partPatterns:copy(cutState.partPatterns)});
  const historyKey=()=>`${currentProjectId||'standalone'}/${currentUnitId}`;
  const capture=()=>({key:historyKey(),value:saved()});
  const history=()=>{const key=historyKey();if(!histories.has(key))histories.set(key,{past:[],future:[]});return histories.get(key);};
  const persist=()=>{invalidateCutResult();if(currentProjectId)saveCurrentUnitIntoProject({silent:true});else scheduleUnitAutoSave();};
  function sortPart(p){
    const dims=core.dimensions(p,formulas(),state.outer);if(dims.some(d=>d==null))return;
    const order=[0,1,2].sort((a,b)=>dims[b]-dims[a]),values=keys.map(k=>p[k]),axes=p.placement?.axes||[null,null,null];
    keys.forEach((k,i)=>p[k]=values[order[i]]);p.placement.axes=order.map(i=>axes[i]);delete state.overrides[p.id];
  }
  function undo(redo=false){
    const h=history(),from=redo?h.future:h.past,to=redo?h.past:h.future;if(!from.length)return;
    to.push(saved());const v=from.pop();Object.assign(state,{customParts:v.customParts,partNames:v.partNames,partGrain:v.partGrain,overrides:v.overrides});cutState.partPatterns=v.partPatterns;
    update();persist();baseline=capture();
  }
  function openUnit(bundle,partId){
    const p=core.importBundle(activeProject(),bundle);saveProject(p);
    const unit=p.units.find(u=>u.structure?.drawingLayout?.sourceHash===bundle.source.sha256);
    openProjectUnit(unit.id);
    const id=core.idFor(bundle,{id:partId||bundle.parts[0].id});
    state.historySelection=`part:${id}`;state.selectedPartId=id;renderTree();renderCabinet();
    showEditorPage('structure');
  }
  function renderFront(){
    const g=document.getElementById('cabinet'),f=cabinetPreviewFrame(),model=core.geometry(formulas(),state.outer);
    const sx=f.w/state.outer.W,sy=f.h/state.outer.H;
    g.innerHTML=`<rect x="${f.x}" y="${f.y}" width="${f.w}" height="${f.h}" fill="none" stroke="#c2b9aa" stroke-dasharray="5 4"/>`+
      [...model.solids].sort((a,b)=>b.z0-a.z0).map(p=>`<rect data-drawing-native-part="${esc(p.partId)}" x="${f.x+p.x0*sx}" y="${f.y+f.h-p.y1*sy}" width="${(p.x1-p.x0)*sx}" height="${(p.y1-p.y0)*sy}" fill="${isPartSelected(p.partId)?'#a8cf86':'#d7cfc2'}" stroke="#554f45" stroke-width="1"><title>${esc(partDisplayName(p.partId))}</title></rect>`).join('')+
      `<text x="${f.x}" y="${f.y-12}" font-size="11" fill="#8b5426">表示 ${model.solids.length}枚 / 要確認 ${model.issues.length}件${Object.values(state.outer.drawingKnownAxes||{}).includes(false)?' / 外寸未設定':''}</text>`;
    g.querySelectorAll('[data-drawing-native-part]').forEach(el=>el.addEventListener('click',()=>{state.selectedPartId=el.dataset.drawingNativePart;state.historySelection=`part:${state.selectedPartId}`;renderTree();renderCabinet();draw3D();}));
  }
  function enhanceEditor(p){
    if(!p.drawingSource)return;
    const root=document.getElementById('historyEditor'),h=history(),dims=core.dimensions(p,formulas(),state.outer),place=p.placement||{axes:[null,null,null],instances:[]};
    const nodes=[],count=core.validQuantity(p.qty)?Math.min(p.qty,100):0;
    for(let i=0;i<count;i++)nodes.push(place.instances[i]||{x:'',y:'',z:''});
    const field=(label,id,value)=>`<div class="field"><label>${label}</label><input id="${id}" type="text" value="${esc(value??'')}" autocomplete="off"></div>`;
    const section=document.createElement('section');section.className='nativeDrawingFields';
    section.innerHTML=`${field('厚みの式','historyNativeThickness',p.thicknessFormula)}<div class="nativeEvidence"><strong>図面 ${esc(p.drawingSource.partId)}</strong> / ${esc(p.drawingSource.zone)}<br>${p.drawingSource.dimensions.map((d,i)=>`${['長さ','幅','厚み'][i]}：${esc(d.display)} ／ ${esc(d.method)} ／ ${esc(d.source)}`).join('<br>')}<br>材料・仕上げ：${esc(p.drawingSource.finish)}<br>接合：${esc(p.drawingSource.joints||'未設定')}</div>
      <h4>取付方向と位置</h4><p class="nativeHint">X＝左からの位置、Y＝下からの高さ、Z＝前からの奥行。各部材の左下前端を基準にします。位置と方向が揃った部材を3Dに表示します。</p>
      <div class="historyEditorGrid">${['長さ','幅','厚み'].map((label,i)=>`<div class="field"><label>${label}の取付方向</label><select data-native-axis="${i}"><option value="">未設定</option>${['x','y','z'].map(a=>`<option value="${a}" ${place.axes[i]===a?'selected':''}>${a.toUpperCase()}</option>`).join('')}</select></div>`).join('')}</div>
      <div class="nativePositions">${nodes.map((pos,i)=>`<div class="nativePositionRow"><small>${i+1}枚目</small>${['x','y','z'].map(a=>`<label>${a.toUpperCase()}<input data-native-position="${i}" data-native-coordinate="${a}" type="text" value="${esc(pos[a]??'')}" aria-label="${i+1}枚目の${a.toUpperCase()}位置"></label>`).join('')}</div>`).join('')}</div>
      <p class="nativeHint">${p.qty>100?'配置欄は先頭100枚を表示しています。保存済みの全配置は保持します。<br>':''}配置根拠：${esc(place.source||'未設定')}</p>
      <div class="field"><label>製作メモ・確認事項</label><textarea id="nativeDrawingNote">${esc(p.drawingNote||'')}</textarea></div>
      <div class="nativeWarning">${core.geometry(formulas(),state.outer).issues.filter(x=>x.startsWith(p.drawingSource.partId+'：')).map(esc).join('<br>')||'寸法・取付方向・位置を3Dに反映しています。'}<br>${esc(core.cutIssue({...p,grainMode:partGrainMode(p.id)},formulas(),state.outer,patternFinishThickness(getCutPattern(cutState.partPatterns[p.id]))))}</div>
      <div class="nativeButtons"><button id="nativeSourceDrawing" type="button">元図面を開く</button><button id="nativeSave" type="button">設計を保存</button><button id="nativeUndo" type="button" ${h.past.length?'':'disabled'}>元に戻す</button><button id="nativeRedo" type="button" ${h.future.length?'':'disabled'}>やり直す</button></div>`;
    root.append(section);
    document.getElementById('historyNativeThickness').addEventListener('input',e=>{p.thicknessFormula=e.target.value;updateLivePreview();});
    section.querySelectorAll('[data-native-axis]').forEach(el=>el.addEventListener('change',()=>{p.placement.axes[+el.dataset.nativeAxis]=el.value||null;}));
    section.querySelectorAll('[data-native-position]').forEach(el=>el.addEventListener('input',()=>{const i=+el.dataset.nativePosition;while(p.placement.instances.length<=i)p.placement.instances.push({x:'',y:'',z:''});p.placement.instances[i][el.dataset.nativeCoordinate]=el.value;updateLivePreview();}));
    document.getElementById('nativeDrawingNote').addEventListener('input',e=>p.drawingNote=e.target.value);
    document.getElementById('nativeUndo').addEventListener('click',()=>undo());document.getElementById('nativeRedo').addEventListener('click',()=>undo(true));
    document.getElementById('nativeSave').addEventListener('click',()=>{persist();toast('元アプリの設計を保存しました');});
    document.getElementById('nativeSourceDrawing').addEventListener('click',()=>{persist();window.MakeItFitDrawingUI.openLinked(p.drawingSource.bundleId,p.drawingSource.partId);});
    baseline=capture();
  }
  const editor=document.getElementById('historyEditor');
  editor.addEventListener('focusin',e=>{if(state.drawingLayout&&e.target.matches('input,select,textarea'))baseline=capture();});
  editor.addEventListener('change',e=>{
    if(!state.drawingLayout||!e.target.matches('input,select,textarea'))return;
    if(e.target.id==='historyGenericQty'&&(!/^\d+$/.test(e.target.value.trim())||!core.validQuantity(Number(e.target.value))))return;
    const key=historyKey(),before=baseline?.key===key?baseline.value:saved(),id=state.selectedPartId;
    queueMicrotask(()=>{
      if(historyKey()!==key)return;
      const p=state.customParts.find(p=>p.id===id);if(p?.drawingSource){sortPart(p);p.placement.instances=p.placement.instances.slice(0,p.qty);}
      const after=saved();if(JSON.stringify(before)!==JSON.stringify(after)){const h=history();h.past.push(before);if(h.past.length>50)h.past.shift();h.future=[];}
      update();persist();baseline=capture();
    });
  },true);
  window.MakeItFitDrawingNativeUI={enhanceEditor,renderFront,openUnit};
})();
