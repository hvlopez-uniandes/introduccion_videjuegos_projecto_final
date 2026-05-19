#!/usr/bin/env bash
# Prueba local del build web. NO uses file:// (falla CORS).
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f build/web/index.html ]]; then
  echo "Falta build/web — ejecuta: ./scripts/build_web.sh"
  exit 1
fi

echo "=== Opción recomendada: servidor pygbag (desde la raíz del repo) ==="
echo "  python3 -m pygbag . --ume_block=0"
echo "  Abre la URL que imprima (http://localhost:...) y haz CLIC en la página."
echo ""
echo "=== Opción alternativa: solo archivos de build/web ==="
echo "  Sirviendo http://127.0.0.1:8000/ — abre esa URL (no file://)"
echo ""

cd build/web
python3 -m http.server 8000
