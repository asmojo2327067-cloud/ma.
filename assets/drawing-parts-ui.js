(function () {
  'use strict';
  const core = window.MakeItFitDrawingParts;
  const root = document.getElementById('drawingPartsRoot');
  if (!root || !core) return;
  const esc = value => String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  const copy = value => JSON.parse(JSON.stringify(value));
  const ui = { projectId: null, bundleId: null, partId: null, viewId: null, search: '', zone: '', status: '', zoom: 1, message: '', error: false };
  const histories = new Map();
  let currentProject = null;
  const bundle = () => currentProject?.drawingParts?.bundles?.find(b => b.id === ui.bundleId);
  const part = () => bundle()?.parts.find(p => p.id === ui.partId);
  const history = () => {
    const key = `${ui.projectId}/${ui.bundleId}`;
    if (!histories.has(key)) histories.set(key, { past: [], future: [] });
    return histories.get(key);
  };
  function message(value, error = false) {
    ui.message = value; ui.error = error;
    const el = document.getElementById('dpMessage');
    if (el) { el.textContent = value; el.hidden = !value; el.classList.toggle('error', error); }
  }
  function stateLabel(p) {
    if (p.dims.some(d => d.result == null)) return ['要確認', 'unknown'];
    if (p.editedAt) return ['編集あり', 'edited'];
    return ['寸法あり', ''];
  }
  function dimension(d) {
    return d.formula && d.result != null ? `${d.formula} = ${d.result}` : String(d.display);
  }
  function render(project) {
    currentProject = project;
    if (ui.projectId !== project.id) {
      Object.assign(ui, { projectId: project.id, bundleId: null, partId: null, viewId: null, search: '', zone: '', status: '', zoom: 1, message: '', error: false });
    }
    const bundles = project.drawingParts?.bundles || [];
    if (!bundles.some(b => b.id === ui.bundleId)) ui.bundleId = bundles[0]?.id || null;
    const b = bundle();
    if (b) {
      if (!b.parts.some(p => p.id === ui.partId)) ui.partId = b.parts[0].id;
      if (!b.views.some(v => v.id === ui.viewId)) ui.viewId = core.markersFor(b, ui.partId)[0]?.viewId || b.views[0].id;
    }
    root.innerHTML = `<div class="dp-toolbar"><div><h2 class="dp-title">図面と部材を照合</h2><p class="dp-subtitle">部材番号を選ぶと、図面の該当箇所と寸法の根拠を確認できます。</p></div><div class="dp-actions">
      ${window.MakeItFitDrawingDemo ? '<button class="dp-button dp-demo" id="dpDemo" type="button">今回の図面を開く</button>' : ''}
      <button class="dp-button" id="dpImport" type="button">部材データを読み込む</button>
      <button class="dp-button" id="dpExport" type="button" ${b ? '' : 'disabled'}>部材データを保存</button>
      </div><input id="drawingPartsFile" type="file" accept=".json,application/json" hidden></div>
      <div id="dpMessage" class="dp-message ${ui.error ? 'error' : ''}" role="status" aria-live="polite" ${ui.message ? '' : 'hidden'}>${esc(ui.message)}</div>
      ${b ? `<div class="dp-bundle-bar"><span>図面</span><select id="dpBundle" class="dp-select" aria-label="図面データ">${bundles.map(x => `<option value="${esc(x.id)}" ${x.id === b.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select><span class="dp-source-title">${esc(b.source.name)} · ${b.source.pages}ページ</span></div>
      <div id="dpSummary" class="dp-summary"></div><div class="dp-layout"><aside class="dp-list" aria-label="部材一覧"><div class="dp-list-head"><h3>部材一覧 <span id="dpListCount" class="dp-list-count"></span></h3>
      <input id="dpSearch" class="dp-search" type="search" placeholder="部材名・G番号で検索" aria-label="部材を検索" value="${esc(ui.search)}"><div class="dp-list-filters"><select id="dpZone" class="dp-select" aria-label="家具区分"><option value="">すべての家具</option>${[...new Set(b.parts.map(p => p.zone))].map(z => `<option value="${esc(z)}" ${z === ui.zone ? 'selected' : ''}>${esc(z)}</option>`).join('')}</select><select id="dpStatus" class="dp-select" aria-label="寸法の状態"><option value="">すべての状態</option><option value="unknown" ${ui.status === 'unknown' ? 'selected' : ''}>要確認</option><option value="known" ${ui.status === 'known' ? 'selected' : ''}>寸法あり</option></select></div></div><div id="dpPartList" class="dp-part-list"></div></aside>
      <section id="dpViewer" class="dp-viewer" aria-label="部材に対応する図面"></section><aside id="dpInspector" class="dp-inspector" aria-label="選択部材の寸法と根拠"></aside></div>` : '<div class="dp-empty"><h3>図面と部材を同じ画面で確認</h3><p>図面の位置情報を含む部材データを読み込むと、<br>部材一覧・図面・寸法と根拠を表示します。</p><button class="dp-button primary" data-dp-import type="button">部材データを選ぶ</button></div>'}`;
    if (b) { renderSummary(); renderList(); renderViewer(); renderInspector(); }
    const meta = document.getElementById('projectMeta');
    if (meta && bundles.length) meta.textContent += `　/　図面 ${bundles.length}件・部材 ${bundles.reduce((n,x) => n + core.summary(x).pieceCount, 0)}点`;
  }
  function renderSummary() {
    const b = bundle(), s = core.summary(b), el = document.getElementById('dpSummary');
    el.innerHTML = `<div><strong>${b.productionUnits}</strong><span>製作台数</span></div><div><strong>${s.rowCount}</strong><span>部材の行</span></div><div><strong>${s.totalCount}</strong><span>仕上がり部材の総数</span></div><div><strong>${s.unresolvedCount}</strong><span>寸法に要確認あり</span></div><span class="dp-summary-note">長さ → 幅 → 厚み ／ mm<br>設計部材の集計。材料構成・製作用部材への展開は別途確認。</span>`;
  }
  function renderList() {
    const b = bundle();
    const query = ui.search.trim().toLocaleLowerCase();
    const filtered = b.parts.filter(p => (!ui.zone || p.zone === ui.zone) && (!query || `${p.id} ${p.name} ${p.zone}`.toLocaleLowerCase().includes(query)) && (!ui.status || (ui.status === 'unknown') === p.dims.some(d => d.result == null)));
    document.getElementById('dpListCount').textContent = `${filtered.length} / ${b.parts.length}`;
    document.getElementById('dpPartList').innerHTML = filtered.length ? filtered.map(p => {
      const [label, status] = stateLabel(p);
      return `<button class="dp-part ${p.id === ui.partId ? 'is-selected' : ''}" data-dp-part="${esc(p.id)}" type="button" aria-pressed="${p.id === ui.partId}"><span class="dp-part-top"><span class="dp-part-id">${esc(p.id)}</span><span class="dp-status ${status}">${label}</span></span><span class="dp-part-name">${esc(p.name)}</span><span class="dp-part-size">${p.dims.map(d => esc(dimension(d))).join(' × ')}</span><span class="dp-part-qty">${esc(p.zone)} · ${p.qty}枚／1台</span></button>`;
    }).join('') : '<div class="dp-no-match">該当する部材がありません。</div>';
  }
  function renderViewer() {
    const b = bundle(), v = b.views.find(v => v.id === ui.viewId);
    const related = b.views.filter(v => v.marks.some(m => m.id === ui.partId));
    document.getElementById('dpViewer').innerHTML = `<div class="dp-view-head"><select id="dpView" class="dp-select" aria-label="視図">${b.views.map(x => `<option value="${esc(x.id)}" ${x.id === v.id ? 'selected' : ''}>${esc(x.id)} ${esc(x.title)}</option>`).join('')}</select><div class="dp-zoom"><button class="dp-button" id="dpZoomOut" type="button" aria-label="図面を縮小">−</button><span class="dp-zoom-value">${Math.round(ui.zoom * 100)}%</span><button class="dp-button" id="dpZoomIn" type="button" aria-label="図面を拡大">＋</button><button class="dp-button" id="dpZoomFit" type="button">全体</button></div></div>
    <div class="dp-related"><span>${esc(ui.partId)}の対応図</span>${related.map(x => `<button class="dp-button ${x.id === v.id ? 'is-selected' : ''}" data-dp-view="${esc(x.id)}" type="button">${esc(x.id)}</button>`).join('') || 'この部材の対応図は未設定'}</div>
    <div class="dp-canvas-scroll"><div class="dp-canvas" style="width:${ui.zoom * 100}%"><img class="dp-drawing" src="${esc(v.image)}" alt="${esc(v.source)} ${esc(v.title)}"><svg class="dp-overlay" viewBox="0 0 ${v.width} ${v.height}" aria-label="図面上の部材番号">${v.marks.map(m => {
      const x = m.x * v.width, y = m.y * v.height, lx = Math.min(m.labelX * v.width, v.width - 48), ly = Math.min(m.labelY * v.height, v.height - 21);
      return `<g class="dp-marker ${m.id === ui.partId ? 'is-selected' : ''}" data-dp-marker="${esc(m.id)}" tabindex="0" role="button" aria-label="部材${esc(m.id)}を選択"><line x1="${lx+24}" y1="${ly+10}" x2="${x}" y2="${y}"/><circle cx="${x}" cy="${y}" r="3"/><rect x="${lx}" y="${ly}" width="48" height="21"/><text x="${lx+5}" y="${ly+14}">${esc(m.id)}</text></g>`;
    }).join('')}</svg></div></div><div class="dp-view-foot"><strong id="dpViewSource">${esc(v.source)}</strong>黄色の指示点が選択部材です。同じ番号が複数ある場合は同じ寸法でまとめた部材を示します。</div>`;
  }
  function renderInspector() {
    const p = part(), b = bundle(), [status, className] = stateLabel(p);
    const labels = ['長さ', '幅', '厚み'], ids = ['dpLength', 'dpWidth', 'dpThickness'];
    const h = history();
    document.getElementById('dpInspector').innerHTML = `<header class="dp-inspector-head"><small id="dpPartId">${esc(p.id)}</small><h3>${esc(p.name)}</h3><p>${esc(p.zone)}　<span class="dp-status ${className}">${status}</span>　元ID ${esc((p.sourceIds || []).join(' / '))}</p></header>
    <form id="dpForm" class="dp-form">${p.dims.map((d,i) => `<label class="dp-field"><span class="dp-field-label">${labels[i]} <span class="dp-method">${esc(d.method)}</span></span><input id="${ids[i]}" class="dp-input" type="text" value="${esc(d.display)}" autocomplete="off" spellcheck="false"><span id="dpDimensionResult${i}" class="dp-result">${d.result == null ? '数値結果：未確定（式・図面値を保持）' : `結果：${d.result} mm`}${d.formula ? `<br>式：${esc(d.formula)}` : ''}</span><span class="dp-evidence">取付方向：${esc(d.axis)}<br>根拠：${esc(d.source)}</span></label>`).join('')}
    <label class="dp-field"><span class="dp-field-label">使用枚数／1台</span><input id="dpQuantity" class="dp-input" type="text" inputmode="numeric" value="${p.qty}" autocomplete="off"><span class="dp-result">案件合計：${p.qty} × ${b.productionUnits}台 = ${p.qty * b.productionUnits}枚</span></label>
    <div class="dp-wide"><div class="dp-section-label">材料・接合</div><div class="dp-facts">${esc(p.finish || '材料構成は未設定')}${p.joints ? '\n接合：'+esc(p.joints) : ''}</div></div>
    <label class="dp-field dp-wide"><span class="dp-section-label" style="display:block">読取メモ・確認事項</span><textarea id="dpNote" class="dp-note">${esc(p.note || '')}</textarea></label>
    <details class="dp-wide"><summary>元の図面読取を確認</summary><div class="dp-original">${(p.original?.dims || p.dims).map((d,i) => `${labels[i]}：${esc(dimension(d))}\n${esc(d.method)} ／ ${esc(d.source)}`).join('\n\n')}\n\n${esc(p.original?.note ?? p.note ?? '')}</div></details>
    <div class="dp-wide"><div class="dp-save-row"><button id="dpApply" class="dp-button primary" type="submit">変更を保存</button><button id="dpUndo" class="dp-button" type="button" ${h.past.length ? '' : 'disabled'}>元に戻す</button><button id="dpRedo" class="dp-button" type="button" ${h.future.length ? '' : 'disabled'}>やり直す</button></div><div class="dp-save-hint">数値欄で計算できます。入力した値は「編集値」として元図面と区別して保存します。すべて数値になると、寸法と取付方向を長い順に並べ直します。</div></div></form>`;
  }
  function draft() {
    return { dimensions: ['dpLength','dpWidth','dpThickness'].map(id => document.getElementById(id).value), qty: document.getElementById('dpQuantity').value, note: document.getElementById('dpNote').value };
  }
  function draftChanged() {
    const p = part();
    if (!p || !document.getElementById('dpLength')) return false;
    const d = draft();
    return d.dimensions.some((x,i) => String(p.dims[i].display) !== x) || String(p.qty) !== d.qty || (p.note || '') !== d.note;
  }
  function saveBundle(next) {
    const p = activeProject();
    if (!p || p.id !== ui.projectId) throw new Error('案件を開き直してください。');
    const index = p.drawingParts?.bundles.findIndex(b => b.id === next.id);
    if (index == null || index < 0) throw new Error('図面データが見つかりません。');
    p.drawingParts.bundles[index] = next;
    saveProject(p);
    currentProject = p;
  }
  function applyPart(silent = false) {
    try {
      if (!draftChanged()) { if (!silent) message('保存済みです。'); return true; }
      const b = bundle(), next = core.editPart(b, ui.partId, draft()), h = history();
      saveBundle(next);
      h.past.push(copy(b.parts)); if (h.past.length > 50) h.past.shift(); h.future = [];
      renderSummary(); renderList(); renderInspector();
      if (!silent) message(`${ui.partId}の変更を案件に保存しました。`);
      return true;
    } catch (error) { message(error.message || '保存できませんでした。', true); return false; }
  }
  function selectPart(id) {
    if (!bundle().parts.some(p => p.id === id)) return;
    if (!applyPart(true)) return;
    ui.partId = id;
    const matches = core.markersFor(bundle(), id);
    if (!matches.some(m => m.viewId === ui.viewId)) ui.viewId = matches[0]?.viewId || ui.viewId;
    ui.zoom = 1;
    renderList(); renderViewer(); renderInspector();
  }
  function undo(redo = false) {
    if (draftChanged() && !applyPart(true)) return;
    const h = history(), from = redo ? h.future : h.past, to = redo ? h.past : h.future;
    if (!from.length) return;
    try {
      const b = bundle(), parts = from[from.length-1];
      saveBundle({ ...b, parts: copy(parts) });
      from.pop(); to.push(copy(b.parts));
      renderSummary(); renderList(); renderInspector();
      message(redo ? '変更をやり直しました。' : '変更を元に戻しました。');
    } catch (error) { message(error.message, true); }
  }
  async function importFile(file) {
    if (!file) return;
    try {
      if (file.size > 20000000) throw new Error('20MB以内の部材データを選んでください。');
      const data = JSON.parse(await file.text()), parsed = core.validateBundle(data);
      if (!applyPart(true)) return;
      const p = core.addBundle(activeProject(), parsed);
      saveProject(p);
      Object.assign(ui, { bundleId: parsed.id, partId: parsed.parts[0].id, viewId: null, search: '', zone: '', status: '' });
      renderProjectView();
      message(`${parsed.name}を読み込みました。${core.summary(parsed).pieceCount}点／${parsed.productionUnits}台です。`);
    } catch (error) { message(error instanceof SyntaxError ? 'JSON形式の部材データを選んでください。' : error.message, true); }
  }
  function exportBundle() {
    if (!applyPart(true)) return;
    const b = bundle(), blob = new Blob([JSON.stringify(b, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = `${b.name.replace(/[<>:"/\\|?*]/g, '_')}.drawing-parts.json`;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    message('図面・部材データをファイルに保存しました。');
  }
  function openDemo() {
    try {
      const b = core.validateBundle(window.MakeItFitDrawingDemo);
      if (!applyPart(true)) return;
      const id = `PRJ-DRAWING-${b.source.sha256.slice(0,16)}`;
      let p = loadProject(id);
      if (!p) { p = createProjectObject(b.name); p.id = id; p = core.addBundle(p, b); saveProject(p); }
      openProject(id); setProjectTab('drawings');
      message('今回の図面を開きました。部材番号を選んで確認できます。');
    } catch (error) { message(error.message, true); }
  }
  root.addEventListener('click', event => {
    const button = event.target.closest('button, [data-dp-marker]');
    if (!button) return;
    if (button.dataset.dpPart) return selectPart(button.dataset.dpPart);
    if (button.dataset.dpMarker) return selectPart(button.dataset.dpMarker);
    if (button.dataset.dpView) { ui.viewId = button.dataset.dpView; ui.zoom = 1; return renderViewer(); }
    if (button.hasAttribute('data-dp-import') || button.id === 'dpImport') return document.getElementById('drawingPartsFile').click();
    if (button.id === 'dpDemo') return openDemo();
    if (button.id === 'dpExport') return exportBundle();
    if (button.id === 'dpUndo') return undo();
    if (button.id === 'dpRedo') return undo(true);
    if (button.id === 'dpZoomIn') ui.zoom = Math.min(3, ui.zoom + .25);
    else if (button.id === 'dpZoomOut') ui.zoom = Math.max(.5, ui.zoom - .25);
    else if (button.id === 'dpZoomFit') ui.zoom = 1;
    else return;
    renderViewer();
  });
  root.addEventListener('submit', event => { event.preventDefault(); applyPart(); });
  root.addEventListener('input', event => {
    if (event.target.id === 'dpSearch') { ui.search = event.target.value; renderList(); }
  });
  root.addEventListener('change', event => {
    event.stopPropagation(); // Analysis inputs are separate from the native unit auto-save timer.
    const target = event.target;
    if (target.id === 'drawingPartsFile') { importFile(target.files[0]); target.value = ''; }
    else if (target.id === 'dpZone') { ui.zone = target.value; renderList(); }
    else if (target.id === 'dpStatus') { ui.status = target.value; renderList(); }
    else if (target.id === 'dpView') { ui.viewId = target.value; ui.zoom = 1; renderViewer(); }
    else if (target.id === 'dpBundle') {
      if (!applyPart(true)) { target.value = ui.bundleId; return; }
      ui.bundleId = target.value; ui.partId = null; ui.viewId = null; ui.search = ''; ui.zone = ''; ui.status = '';
      renderProjectView();
    }
  });
  root.addEventListener('keydown', event => {
    const marker = event.target.closest('[data-dp-marker]');
    if (marker && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); selectPart(marker.dataset.dpMarker); }
    if (!(event.ctrlKey || event.metaKey) || !['z','y'].includes(event.key.toLowerCase())) return;
    if (event.target.matches('input, textarea')) return; // Keep native text undo inside a field.
    event.preventDefault(); event.stopPropagation(); undo(event.shiftKey || event.key.toLowerCase() === 'y');
  });
  window.MakeItFitDrawingUI = { render, openDemo };
  if (window.MakeItFitDrawingDemo) {
    const host = document.getElementById('newProjectForm');
    if (host) {
      const link = document.createElement('button'); link.type = 'button'; link.className = 'dp-button dp-demo';
      link.id = 'drawingDemoHome'; link.textContent = '今回のミニバー・ワードローブを開く →';
      link.style.cssText = 'margin:18px 0;font-size:14px;padding:14px 18px';
      link.addEventListener('click', openDemo); host.before(link);
    }
  }
  if (typeof activeProject === 'function' && activeProject()) renderProjectView();
})();
