#!/usr/bin/python3
# MISW-4407 — Semana 3 (sprites, animaciones, Hunter, explosiones) + semanas anteriores

import sys
from pathlib import Path

from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    # Por defecto: src/cfg (JSON semana 3; las imágenes siguen en assets/img según rutas del JSON).
    # Semana 2 (rectángulos): python3 main.py assets/verification_s02/cfg_00
    cfg_folder = None
    if len(sys.argv) >= 2:
        cfg_folder = Path(sys.argv[1])

    game = GameEngine(cfg_dir=cfg_folder)
    game.run()
