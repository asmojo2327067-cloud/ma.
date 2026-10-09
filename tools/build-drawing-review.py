"""Build an offline, single-file copy of the existing app with private drawing data.

Usage: python tools/build-drawing-review.py data.drawing-parts.json result.html
The result is a local deliverable; do not commit it or the user's drawing data.
"""
import base64
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
data_path=Path(sys.argv[1])
output_path=Path(sys.argv[2])
data=json.loads(data_path.read_text())
html=(ROOT/'index.html').read_text()
css=(ROOT/'assets/drawing-parts.css').read_text()
html=html.replace('<link rel="stylesheet" href="assets/drawing-parts.css">','<style>\n'+css+'\n</style>')
for filename in ['drawing-parts-core.js','drawing-parts-ui.js']:
    code=(ROOT/'assets'/filename).read_text()
    if filename=='drawing-parts-ui.js':
        encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
        code='window.MakeItFitDrawingDemo='+encoded+';\n'+code
    html=html.replace(f'<script src="assets/{filename}"></script>','<script>\n'+code+'\n</script>')
sketch=ROOT/'assets/sketch-craft-cabinet.jpg'
if sketch.exists():
    image='data:image/jpeg;base64,'+base64.b64encode(sketch.read_bytes()).decode()
    html=html.replace('src="assets/sketch-craft-cabinet.jpg"','src="'+image+'"')
assert '<script src=' not in html
assert 'href="assets/' not in html
output_path.parent.mkdir(parents=True,exist_ok=True)
output_path.write_text(html)
print(json.dumps({'html':str(output_path),'bytes':output_path.stat().st_size,'parts':len(data['parts']),'pieces':sum(p['qty'] for p in data['parts'])},ensure_ascii=False))
