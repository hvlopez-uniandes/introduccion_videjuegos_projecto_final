#!/usr/bin/env bash
# Build HTML5 para itch.io / navegador con pygbag.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -q -r requirements.txt pygbag

rm -rf build/web
mkdir -p build/web

python3 -m pygbag --build .

echo ""
echo "Listo: sube el contenido de build/web/ a itch.io (Kind: HTML)."
echo "Archivo principal: build/web/index.html"
