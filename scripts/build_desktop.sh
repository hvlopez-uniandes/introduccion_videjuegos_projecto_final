#!/usr/bin/env bash
# Build ejecutable de escritorio (macOS/Linux) con PyInstaller.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -q -r requirements.txt pyinstaller

rm -rf build dist

python3 -m PyInstaller \
  --name Defender-MISW \
  --windowed \
  --noconfirm \
  --clean \
  --add-data "assets:assets" \
  --add-data "userdata:userdata" \
  --hidden-import esper \
  main.py

echo ""
echo "Listo: dist/Defender-MISW/ (macOS app bundle) o dist/Defender-MISW.exe en Windows."
echo "Prueba: ./dist/Defender-MISW/Defender-MISW   (o abrir la .app en macOS)"
