#!/usr/bin/python3
# MISW-4407 — Semana 3 (sprites, animaciones, Hunter, explosiones) + semanas anteriores

import sys
from pathlib import Path

from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    # Por defecto: assets/cfg (JSON del proyecto; fuentes/textos en assets/ según rutas del JSON).
    # Otra carpeta de JSON: python3 main.py path/a/cfg
    cfg_folder = None
    if len(sys.argv) >= 2:
        cfg_folder = Path(sys.argv[1])

    game = GameEngine(cfg_dir=cfg_folder)
    game.run()
