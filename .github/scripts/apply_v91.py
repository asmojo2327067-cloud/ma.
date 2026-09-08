from pathlib import Path
import base64, subprocess, tempfile, os

patch = base64.b64decode("""LS0tIGEvaW5kZXguaHRtbAkyMDI2LTA5LTA5IDA3OjEwOjAwLjAwMDAwMDAwMCArMDkwMAorKysgYi9pbmRleC5odG1sCTIwMjYtMDktMDkgMDc6MTQ6MDAuMDAwMDAwMDAwICswOTAwCkBAIC0xNjU5LDYgKzE2NTksMTggQEAKICAgfQogfQorLyo...TRUNCATED_PLACEHOLDER...""").decode("utf-8")
with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
    f.write(patch)
    patch_path=f.name
try:
    subprocess.run(["patch","-p1","--forward","--batch","-i",patch_path], check=True)
finally:
    os.unlink(patch_path)

source=Path("index.html").read_text(encoding="utf-8")
required=[
    'data-build="ma-project-v91"',
    '>棚・束</button>',
    'id="innerBackToggle"',
    '#cabinet *',
    'pointer-events:none!important',
]
for marker in required:
    if marker not in source:
        raise SystemExit(f"missing v91 marker: {marker}")
region=source[source.find('data-workspace-dock-panel="region"'):source.find('data-workspace-dock-panel="joint"')]
back=source[source.find('data-workspace-dock-panel="backboard"'):source.find('</main>')]
if 'id="innerBackToggle"' in region:
    raise SystemExit("inner back still in 棚・束")
if 'id="innerBackToggle"' not in back:
    raise SystemExit("inner back missing from 背板")
