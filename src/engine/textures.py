"""Carga y cache de texturas (rutas relativas a la raíz del proyecto)."""

from pathlib import Path

import pygame

_cache = {}


def load_texture(project_root: Path, relative_path: str) -> pygame.Surface:
    rel = relative_path.replace("\\", "/")
    key = str(Path(rel).resolve()) if Path(rel).is_absolute() else str((project_root / rel).resolve())
    if key not in _cache:
        path = Path(rel) if Path(rel).is_absolute() else project_root / rel
        surf = pygame.image.load(str(path)).convert_alpha()
        _cache[key] = surf
    return _cache[key]


def clear_texture_cache():
    _cache.clear()
