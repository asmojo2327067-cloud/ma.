"""Browser checks for the existing app and its drawing/parts project tab.

Run: python tests/drawing-parts-browser.py [standalone-html]
The private fixture is generated locally and never committed.
"""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
APP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'index.html'
FIXTURE = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'tests/fixtures/drawing-parts.json'
fixture = json.loads(FIXTURE.read_text())
expected_count = sum(p['qty'] for p in fixture['parts']) * fixture['productionUnits']

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(APP.parent)))
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/{APP.name}'

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1680, 'height': 1050}, accept_downloads=True)
    page = context.new_page()
    page.set_default_timeout(8000)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url, wait_until='load')
    # Existing native design data must still be editable after the addition.
    legacy = page.evaluate('''() => {
      const p=createProjectObject('旧案件互換チェック');
      p.units=[snapshot()];p.units[0].id='U-legacy';
      p.cutting.lastResult={sourceSignature:'original',results:[]};
      saveProject(p);openProject(p.id);return p;
    }''')
    page.locator('[data-project-tab="drawings"]').wait_for(state='attached', timeout=3000)
    page.locator('[data-project-tab="drawings"]').click()
    assert page.locator('#drawingPartsRoot').is_visible()
    assert page.locator('.dp-empty').is_visible()
    page.locator('#drawingPartsFile').set_input_files(str(FIXTURE))
    page.locator('[data-dp-part="G007"]').wait_for()
    page.locator('[data-dp-part="G007"]').click()
    assert page.locator('#dpLength').input_value() == '940'
    assert page.locator('#dpWidth').input_value() == '545'
    assert page.locator('#dpThickness').input_value() == '20'
    assert page.locator('.dp-marker.is-selected[data-dp-marker="G007"]').count() == 1
    assert '元PDF p.3' in page.locator('#dpViewSource').inner_text()
    # Selecting the same part through its drawing marker must preserve a draft.
    page.locator('#dpWidth').fill('530')
    page.locator('[data-dp-marker="G007"] rect').first.click()
    assert page.locator('#dpWidth').input_value() == '530'
    page.locator('#dpUndo').click()
    assert page.locator('#dpWidth').input_value() == '545'
    # Reading a second drawing must save the current valid draft before switching.
    other = json.loads((ROOT / 'tests/fixtures/drawing-parts.json').read_text())
    other.update(id='synthetic-second', name='追加の合成図面')
    other['source']['sha256'] = 'b' * 64
    page.locator('#dpWidth').fill('525')
    page.locator('#drawingPartsFile').set_input_files({
        'name': 'second.json', 'mimeType': 'application/json',
        'buffer': json.dumps(other, ensure_ascii=False).encode()})
    expect(page.locator('#dpBundle')).to_have_value('synthetic-second')
    page.locator('#dpBundle').select_option(fixture['id'])
    page.locator('[data-dp-part="G007"]').click()
    assert page.locator('#dpWidth').input_value() == '525'
    page.locator('#dpUndo').click()
    assert page.locator('#dpWidth').input_value() == '545'
    # An invalid draft blocks import without losing the entered value.
    other['id'] = 'synthetic-third'
    other['source']['sha256'] = 'c' * 64
    page.locator('#dpWidth').fill('0')
    page.locator('#drawingPartsFile').set_input_files({
        'name': 'third.json', 'mimeType': 'application/json',
        'buffer': json.dumps(other, ensure_ascii=False).encode()})
    expect(page.locator('#dpMessage')).to_contain_text('正の数値')
    assert page.locator('#dpBundle').input_value() == fixture['id']
    assert page.locator('#dpWidth').input_value() == '0'
    assert page.locator('#dpBundle option').count() == 2
    page.locator('#dpWidth').fill('545')
    page.locator('[data-dp-part="G013"]').click()
    assert page.locator('.dp-marker.is-selected[data-dp-marker="G013"]').count() == 4
    assert page.locator('#dpQuantity').input_value() == '4'
    assert str(expected_count) in page.locator('#dpSummary').inner_text()
    page.locator('[data-dp-marker="G010"] rect').first.click()
    assert page.locator('#dpPartId').inner_text() == 'G010'
    # A draw-only unknown remains an expression; it is not replaced by zero.
    assert page.locator('#dpThickness').input_value() == 'ワードローブ束厚'
    page.locator('[data-dp-part="G007"]').click()
    page.locator('#dpWidth').fill('500/2+20')
    page.locator('#dpApply').click()
    assert '270' in page.locator('#dpDimensionResult1').inner_text()
    page.locator('#dpUndo').click()
    assert page.locator('#dpWidth').input_value() == '545'
    page.locator('#dpRedo').click()
    assert page.locator('#dpWidth').input_value() == '500/2+20'
    page.reload(wait_until='load')
    page.evaluate('id => { openProject(id);setProjectTab("drawings"); }', legacy['id'])
    page.locator('[data-dp-part="G007"]').click()
    assert page.locator('#dpWidth').input_value() == '500/2+20'
    saved = page.evaluate('id => loadProject(id)', legacy['id'])
    assert saved['units'] == legacy['units']
    assert saved['materials'] == legacy['materials']
    assert saved['materialPatterns'] == legacy['materialPatterns']
    assert saved['cutting'] == legacy['cutting']
    # Reimporting the same source must not overwrite our edit.
    page.locator('#drawingPartsFile').set_input_files(str(FIXTURE))
    expect(page.locator('#dpMessage')).to_contain_text('読込済み')
    assert page.locator('#dpWidth').input_value() == '500/2+20'
    # HTML-like notes are rendered as text.
    page.locator('#dpNote').fill('<img src=x onerror="window.bad=true">')
    page.locator('#dpApply').click()
    assert not page.evaluate('Boolean(window.bad)')
    assert page.locator('#dpNote').input_value().startswith('<img')
    # Export retains images, source evidence, and editing history provenance.
    with page.expect_download() as download_info:
        page.locator('#dpExport').click()
    path = download_info.value.path()
    exported = json.loads(Path(path).read_text())
    exported_part = next(p for p in exported['parts'] if p['id'] == 'G007')
    assert exported_part['original']['dims'][1]['display'] == 545
    assert len(exported['views']) == len(fixture['views'])
    assert exported_part['dims'][1]['result'] == 270
    assert not errors, errors
    if page.locator('#dpDemo').count():
        # Use a fresh profile: embedding the full private PDF twice would exceed
        # Chromium's localStorage quota and prevent the second project opening.
        demo_context = browser.new_context(viewport={'width':1680, 'height':1050})
        page = demo_context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url, wait_until='load')
        page.locator('#drawingDemoHome').click()
        page.locator('[data-dp-part="G007"]').click()
        assert page.locator('#dpWidth').input_value() == '545'
        page.locator('#dpWidth').fill('530')
        page.locator('#dpDemo').click()
        assert page.locator('#dpWidth').input_value() == '530'
        page.locator('#dpUndo').click()
        assert page.locator('#dpWidth').input_value() == '545'
        page.locator('#dpWidth').fill('0')
        page.locator('#dpDemo').click()
        expect(page.locator('#dpMessage')).to_contain_text('正の数値')
        assert page.locator('#dpWidth').input_value() == '0'
        page.locator('#dpWidth').fill('545')
    # Responsive layout keeps form controls visible and avoids document overflow.
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.locator('#dpApply').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    assert not errors, errors
    browser.close()
    server.shutdown()
    print(json.dumps({'app': str(APP), 'browser_checks': 'passed', 'native_project_preserved': True,
                      'unknown_dimensions_preserved': True, 'marker_selection_and_quantity': True,
                      'edit_reload_undo_redo_export': True, 'page_errors': errors}, ensure_ascii=False))
