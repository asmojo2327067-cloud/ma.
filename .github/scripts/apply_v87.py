from pathlib import Path
import subprocess

BASE_COMMIT = "11b51d66fe447779ccc1a399d1aa4c5ff88f72a7"  # last index.html before image-button v82

source = subprocess.check_output(["git", "show", f"{BASE_COMMIT}:index.html"], text=True)

replacements = [
    ("<title>ma.｜案件 v81</title>", "<title>ma.｜案件 v87</title>"),
    ("version:81,", "version:87,"),
    ('data-build="ma-project-v81"', 'data-build="ma-project-v87"'),
    ('const WORKSPACE_DOCK_KEY="maWorkspaceDockV81"', 'const WORKSPACE_DOCK_KEY="maWorkspaceDockV87"'),
]
for old, new in replacements:
    if old not in source:
        raise SystemExit(f"missing v81 marker: {old}")
    source = source.replace(old, new, 1)

# Guard against accidentally reintroducing any image-button implementation.
for forbidden in [
    "v82 / image-button system",
    "original Sketch Craft image buttons",
    "btn-normal.png",
    "btn-normal.svg",
    "concept-derived raster button surfaces",
]:
    if forbidden in source:
        raise SystemExit(f"image-button residue found: {forbidden}")

Path("index.html").write_text(source, encoding="utf-8")
