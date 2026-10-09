(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MakeItFitDrawingParts = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const clone = value => JSON.parse(JSON.stringify(value));
  const requireValue = (condition, message) => { if (!condition) throw new Error(message); };
  const text = (value, max = 1000) => {
    requireValue(typeof value === 'string' && value.length <= max, '文字の形式または長さが不正です。');
    return value;
  };
  const positiveInteger = value => Number.isSafeInteger(value) && value > 0 && value <= 1000000;
  const validId = value => typeof value === 'string' && /^[A-Za-z0-9_-]{1,100}$/.test(value);

  function validateDimensions(dims) {
    requireValue(Array.isArray(dims) && dims.length === 3, '長さ・幅・厚みの3寸法が必要です。');
    dims.forEach(d => {
      requireValue(d && typeof d === 'object' && !Array.isArray(d) &&
        (typeof d.display === 'string' || (typeof d.display === 'number' && Number.isFinite(d.display))), '部材寸法の形式が不正です。');
      text(String(d.display), 250);
      requireValue(d.result == null || (typeof d.result === 'number' && Number.isFinite(d.result) && d.result > 0), '寸法の計算結果が不正です。');
      d.result = d.result == null ? null : d.result;
      text(d.method || '', 100); text(d.axis || '', 100); text(d.source || '', 2000); text(d.formula || '', 1000);
    });
  }

  function readDimension(value) {
    const display = text(String(value), 250).trim();
    requireValue(display.length > 0, '寸法または式を入力してください。');
    const normalized = display.replace(/[０-９]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0))
      .replace(/[＋]/g, '+').replace(/[−－]/g, '-').replace(/[×＊]/g, '*').replace(/[÷／]/g, '/')
      .replace(/[（]/g, '(').replace(/[）]/g, ')').replace(/[．]/g, '.').replace(/\s/g, '');
    // Named missing inputs remain expressions. Never evaluate identifiers as JavaScript.
    if (/[^0-9.+*/()\-]/.test(normalized)) {
      requireValue(/^[\p{L}\p{N}\p{M}_\s.+*/()\-※?：:、,]+$/u.test(normalized), '寸法欄には数値・計算式・変数名を入力してください。');
      requireValue(!/[A-Za-z_]\w*\./.test(normalized), '実行コードは寸法式として使えません。');
      return { display, formula: display, result: null, method: '編集・変数式' };
    }
    const tokens = normalized.match(/(?:\d+(?:\.\d*)?|\.\d+)|[()+*/-]/g) || [];
    requireValue(tokens.join('') === normalized && tokens.length <= 100, '計算式の形式が不正です。');
    let index = 0;
    function atom() {
      const t = tokens[index++];
      if (t === '+' || t === '-') return (t === '-' ? -1 : 1) * atom();
      if (t === '(') {
        const n = sum();
        requireValue(tokens[index++] === ')', '括弧を閉じてください。');
        return n;
      }
      requireValue(t !== undefined && /^(?:\d+(?:\.\d*)?|\.\d+)$/.test(t), '計算式の数値が不正です。');
      return Number(t);
    }
    function product() {
      let n = atom();
      while (tokens[index] === '*' || tokens[index] === '/') {
        const op = tokens[index++], rhs = atom();
        requireValue(op !== '/' || rhs !== 0, '0で割ることはできません。');
        n = op === '*' ? n * rhs : n / rhs;
      }
      return n;
    }
    function sum() {
      let n = product();
      while (tokens[index] === '+' || tokens[index] === '-') {
        const op = tokens[index++], rhs = product();
        n = op === '+' ? n + rhs : n - rhs;
      }
      return n;
    }
    const result = sum();
    requireValue(index === tokens.length && Number.isFinite(result) && result > 0, '寸法の計算結果は正の数値にしてください。');
    const calculated = tokens.length > 1;
    return { display: calculated ? display : result, formula: calculated ? display : '', result, method: calculated ? '編集・寸法計算' : '編集値' };
  }

  function validateBundle(value) {
    requireValue(value && typeof value === 'object' && value.schemaVersion === 1, '対応した図面・部材データ（形式1）を選んでください。');
    const b = clone(value);
    requireValue(validId(b.id), '図面データのIDが不正です。');
    text(b.name, 250);
    requireValue(positiveInteger(b.productionUnits), '製作台数は1以上の整数が必要です。');
    requireValue(b.source && /^[a-f0-9]{64}$/i.test(b.source.sha256), '元図面の識別情報がありません。');
    text(b.source.name, 250);
    requireValue(positiveInteger(b.source.pages), '元図面のページ数が不正です。');
    requireValue(Array.isArray(b.parts) && b.parts.length > 0 && b.parts.length <= 5000, '部材の一覧がありません。');
    const ids = new Set();
    b.parts.forEach(p => {
      requireValue(p && validId(p.id) && !ids.has(p.id), '部材IDが不正、または重複しています。');
      ids.add(p.id);
      text(p.name, 250); text(p.zone || '', 250);
      requireValue(positiveInteger(p.qty), '部材の使用枚数は1以上の整数が必要です。');
      validateDimensions(p.dims);
      if (p.sourceIds != null) requireValue(Array.isArray(p.sourceIds) && p.sourceIds.length <= 1000 && p.sourceIds.every(validId), '読取元の部材IDの形式が不正です。');
      if (p.original != null) {
        requireValue(typeof p.original === 'object' && !Array.isArray(p.original), '元の読取情報の形式が不正です。');
        validateDimensions(p.original.dims);
        requireValue(positiveInteger(p.original.qty), '元の使用枚数の形式が不正です。');
        text(p.original.note || '', 10000);
      }
      text(p.note || '', 10000); text(p.finish || '', 2000); text(p.joints || '', 2000);
    });
    requireValue(Array.isArray(b.views) && b.views.length > 0 && b.views.length <= 100, '対応する図面画像がありません。');
    const viewIds = new Set();
    b.views.forEach(v => {
      requireValue(v && validId(v.id) && !viewIds.has(v.id), '視図IDが不正、または重複しています。');
      viewIds.add(v.id); text(v.title, 250); text(v.source || '', 1000);
      requireValue(typeof v.image === 'string' && /^data:image\/(?:png|jpeg);base64,[A-Za-z0-9+/=\s]+$/.test(v.image) && v.image.length <= 15000000, '図面画像は埋め込みPNGまたはJPEGが必要です。');
      requireValue(Number.isFinite(v.width) && v.width > 0 && Number.isFinite(v.height) && v.height > 0, '図面画像の寸法が不正です。');
      requireValue(Array.isArray(v.marks) && v.marks.length <= 10000, '図面の部材位置が不正です。');
      v.marks.forEach(m => {
        requireValue(ids.has(m.id), '図面マーカーが存在しない部材を指しています。');
        for (const key of ['x', 'y', 'labelX', 'labelY']) requireValue(Number.isFinite(m[key]) && m[key] >= 0 && m[key] <= 1, '図面マーカーの位置が不正です。');
      });
    });
    requireValue(JSON.stringify(b).length <= 20000000, '図面・部材データは20MB以内にしてください。');
    return b;
  }

  function addBundle(project, value) {
    requireValue(project && project.id, '先に案件を開いてください。');
    const b = validateBundle(value);
    const bundles = project.drawingParts?.bundles || [];
    requireValue(!bundles.some(x => x.id === b.id || x.source?.sha256 === b.source.sha256), 'この元図面は読込済みです。保存済みの編集は上書きしません。');
    const next = clone(project);
    next.drawingParts = { ...(next.drawingParts || {}), schemaVersion: 1, bundles: [...clone(bundles), b] };
    return next;
  }
  function markersFor(bundle, partId, viewId) {
    return bundle.views.filter(v => !viewId || v.id === viewId).flatMap(v => v.marks.filter(m => m.id === partId).map(m => ({ ...m, viewId: v.id })));
  }
  function summary(bundle) {
    const pieceCount = bundle.parts.reduce((n, p) => n + p.qty, 0);
    return { pieceCount, totalCount: pieceCount * bundle.productionUnits, rowCount: bundle.parts.length,
      unresolvedCount: bundle.parts.filter(p => p.dims.some(d => d.result == null)).length };
  }
  function editPart(bundle, id, patch) {
    const next = clone(bundle), p = next.parts.find(p => p.id === id);
    requireValue(p, '対象部材が見つかりません。');
    requireValue(Array.isArray(patch.dimensions) && patch.dimensions.length === 3, '3寸法を入力してください。');
    const qtyText = String(patch.qty).trim();
    requireValue(/^\d+$/.test(qtyText) && positiveInteger(Number(qtyText)), '使用枚数は1以上の整数にしてください。');
    const note = text(patch.note, 10000);
    const dims = p.dims.map((d, i) => {
      if (String(d.display).trim() === String(patch.dimensions[i]).trim()) return d;
      return { ...d, ...readDimension(patch.dimensions[i]), editedAt: new Date().toISOString() };
    });
    if (dims.every(d => d.result != null)) dims.sort((a, b) => b.result - a.result);
    if (!p.original) p.original = { dims: clone(p.dims), qty: p.qty, note: p.note || '' };
    p.dims = dims; p.qty = Number(qtyText); p.note = note; p.editedAt = new Date().toISOString();
    return next;
  }
  return { validateBundle, addBundle, readDimension, editPart, markersFor, summary };
});
