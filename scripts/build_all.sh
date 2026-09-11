#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

export PYTHONPATH="$ROOT"

echo "=== CadQuery frame (Spruce tube sizes) ==="
.venv/bin/python -m design.frame_cad

echo "=== General-arrangement sheet (3 view, 1:20) ==="
.venv/bin/python -m design.drawings_3view

echo "=== Verify solid model against the drawing ==="
.venv/bin/python -m design.verify

if command -v blender >/dev/null 2>&1; then
  echo "=== Blender shaded views ==="
  blender --background --python "$ROOT/design/render_blender.py"
else
  echo "=== Blender not installed, skipping shaded views ==="
fi

echo "=== Done ==="
ls -lh output/cad/ output/views/ 2>/dev/null || true
