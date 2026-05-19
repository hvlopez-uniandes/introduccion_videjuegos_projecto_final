#!/usr/bin/python3
# MISW-4407 — Semana 3 (sprites, animaciones, Hunter, explosiones) + semanas anteriores
# pygbag: requiere async def main() + await asyncio.sleep(0) en el loop (ver game_engine.run_async)

import asyncio
import sys
from pathlib import Path

from src.engine.game_engine import GameEngine


async def main():
    # Por defecto: assets/cfg (JSON del proyecto; fuentes/textos en assets/ según rutas del JSON).
    # Otra carpeta de JSON: python3 main.py path/a/cfg
    cfg_folder = None
    if len(sys.argv) >= 2:
        cfg_folder = Path(sys.argv[1])

    game = GameEngine(cfg_dir=cfg_folder)

    # pygbag: shell.source(main) espera que main() RETORNE. Si await run_async() aquí,
    # el bucle infinito bloquea y la UI se queda en "Loading please wait".
    if sys.platform == "emscripten":
        asyncio.create_task(game.run_async())
        return

    await game.run_async()


# pygbag carga main.py con shell.source: __name__ no es "__main__"; solo invoca async def main().
if __name__ == "__main__":
    asyncio.run(main())
