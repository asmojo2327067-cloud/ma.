const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const modulePath = path.join(__dirname, '../assets/drawing-parts-core.js');
const api = fs.existsSync(modulePath) ? require(modulePath) : {};

function feature(name) {
  assert.equal(typeof api[name], 'function', `${name}: 図面・部材連携の機能が未実装`);
  return api[name];
}
function bundle() {
  return {
    schemaVersion: 1, id: 'drawing-a', name: 'ミニバー', productionUnits: 1,
    source: { name: 'original.pdf', sha256: 'a'.repeat(64), pages: 1 },
    parts: [
      { id: 'G001', sourceIds: ['B001'], name: '天板', zone: '共通', qty: 1,
        dims: [
          { display: 760, result: 760, method: '明記', axis: '取付幅', source: 'p.1' },
          { display: 545, result: 545, method: '明記', axis: '奥行', source: 'p.1' },
          { display: 20, result: 20, method: '明記', axis: '厚み', source: 'p.1' }
        ], note: '元の読取', finish: '木部', joints: '' },
      { id: 'G002', sourceIds: ['B002'], name: '箱側板', zone: '引出', qty: 4,
        dims: [
          { display: 460, result: 460, method: '明記', axis: '奥行', source: 'p.1' },
          { display: '107＋底板厚＋底板下残り', result: null, formula: '107＋底板厚＋底板下残り', method: '変数式', axis: '高さ', source: 'p.1' },
          { display: '箱側板厚', result: null, method: '変数式', axis: '厚み', source: '未記載' }
        ], note: '底板の下まで側板が必要', finish: '', joints: '' }
    ],
    views: [{ id: 'A01', title: '平断面', source: '元PDF p.1', image: 'data:image/png;base64,aGVsbG8=',
      width: 857, height: 674, marks: [
        { id: 'G001', x: .4, y: .3, labelX: .45, labelY: .2 },
        ...[.1,.2,.3,.4].map(x => ({ id: 'G002', x, y: .5, labelX: x, labelY: .55 }))
      ] }]
  };
}

test('旧案件の構造・材料・木取りを保ったまま図面を追加できる', () => {
  const project = { id: 'old', version: 28, units: [{ id: 'U1', structure: { original: true } }], materials: [{ id: 'M1' }], cutting: { lastResult: { sheets: 2 } } };
  const before = JSON.stringify(project);
  const next = feature('addBundle')(project, bundle());
  assert.equal(JSON.stringify(project), before);
  assert.deepEqual(next.units, project.units);
  assert.deepEqual(next.materials, project.materials);
  assert.deepEqual(next.cutting, project.cutting);
  assert.equal(next.drawingParts.bundles[0].parts.length, 2);
});

test('未知の板厚は空欄の結果と意味のある式のまま保持する', () => {
  const parsed = feature('validateBundle')(bundle());
  assert.equal(parsed.parts[1].dims[1].result, null);
  assert.equal(parsed.parts[1].dims[2].result, null);
  assert.equal(parsed.parts[1].dims[1].formula, '107＋底板厚＋底板下残り');
  assert.equal(feature('summary')(parsed).pieceCount, 5);
});

test('同じ部材の4箇所を選択しても使用枚数を4倍にしない', () => {
  const b = feature('validateBundle')(bundle());
  const marks = feature('markersFor')(b, 'G002', 'A01');
  assert.equal(marks.length, 4);
  assert.equal(feature('summary')(b).pieceCount, 5);
  assert.equal(feature('summary')(b).totalCount, 5);
});

test('数値式を計算し、長さ・幅・厚みを取付方向と一緒に並べ替える', () => {
  const b = bundle();
  const next = feature('editPart')(b, 'G001', { dimensions: ['500/2+20', '600', '20'], qty: 2, note: '読取を修正' });
  const p = next.parts[0];
  assert.deepEqual(p.dims.map(d => d.result), [600, 270, 20]);
  assert.deepEqual(p.dims.map(d => d.axis), ['奥行', '取付幅', '厚み']);
  assert.equal(p.dims[1].formula, '500/2+20');
  assert.equal(p.dims[1].method, '編集・寸法計算');
  assert.equal(p.original.dims[0].display, 760);
  assert.equal(p.original.note, '元の読取');
  assert.equal(b.parts[0].qty, 1);
  assert.equal(p.qty, 2);
});

test('変数が残る式は数値を0にせず、元の図面根拠を残す', () => {
  const b = bundle();
  const next = feature('editPart')(b, 'G001', { dimensions: ['760', '545−後端逃げ', '20'], qty: 1, note: '後端確認' });
  assert.equal(next.parts[0].dims[1].result, null);
  assert.equal(next.parts[0].dims[1].formula, '545−後端逃げ');
  assert.equal(next.parts[0].dims[1].source, 'p.1');
  assert.equal(next.parts[0].dims[1].method, '編集・変数式');
});

test('0枚・負寸法・不正な計算で案件を部分的に更新しない', () => {
  const edit = feature('editPart');
  const b = bundle();
  const before = JSON.stringify(b);
  for (const patch of [
    { dimensions: ['760','545','20'], qty: 0, note: '' },
    { dimensions: ['-1','545','20'], qty: 1, note: '' },
    { dimensions: ['500/0','545','20'], qty: 1, note: '' }
  ]) assert.throws(() => edit(b, 'G001', patch));
  assert.equal(JSON.stringify(b), before);
});

test('計算欄をJavaScriptとして実行しない', () => {
  const parse = feature('readDimension');
  assert.equal(parse('500/2+20').result, 270);
  assert.equal(parse('（500＋20）÷2').result, 260);
  assert.equal(parse('545−後端逃げ').result, null);
  assert.throws(() => parse('globalThis.process.exit(1)'));
});

test('重複部材ID・他部材を指すマーカー・外部画像URLを読み込まない', () => {
  const validate = feature('validateBundle');
  const duplicate = bundle(); duplicate.parts[1].id = 'G001';
  assert.throws(() => validate(duplicate));
  const wrongMark = bundle(); wrongMark.views[0].marks[0].id = 'G999';
  assert.throws(() => validate(wrongMark));
  const externalImage = bundle(); externalImage.views[0].image = 'https://example.test/image.svg';
  assert.throws(() => validate(externalImage));
  const wrongPoint = bundle(); wrongPoint.views[0].marks[0].x = Infinity;
  assert.throws(() => validate(wrongPoint));
});

test('同じ元図面の再読込で保存済みの編集を上書きしない', () => {
  const add = feature('addBundle');
  const p = add({ id: 'p', units: [] }, bundle());
  p.drawingParts.bundles[0].parts[0].note = '編集済み';
  assert.throws(() => add(p, bundle()), /読込済み|追加済み/);
  assert.equal(p.drawingParts.bundles[0].parts[0].note, '編集済み');
});

test('読取元IDや原寸法の壊れた形式を保存前に拒否する', () => {
  const validate = feature('validateBundle');
  const sourceIds = bundle(); sourceIds.parts[0].sourceIds = 'B001';
  assert.throws(() => validate(sourceIds));
  const original = bundle(); original.parts[0].original = { dims: 'malformed', qty: 1, note: '' };
  assert.throws(() => validate(original));
  const originalDimension = bundle();
  originalDimension.parts[0].original = { dims: [{ display: 5 }, null, { display: 1 }], qty: 1, note: '' };
  assert.throws(() => validate(originalDimension));
  for (const field of ['bundle', 'part', 'view']) {
    const numeric = bundle();
    if (field === 'bundle') numeric.id = 123;
    if (field === 'part') numeric.parts[0].id = 123;
    if (field === 'view') numeric.views[0].id = 123;
    assert.throws(() => validate(numeric));
  }
});
