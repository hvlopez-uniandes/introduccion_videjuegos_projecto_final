from pathlib import Path

import pygame

from src.engine.textures import load_texture


class TextureService:
    """Carga de imágenes (usa el caché existente de texturas)."""

    def __init__(self, project_root: Path):
        self._root = project_root

    def load(self, relative_path: str) -> pygame.Surface:
        return load_texture(self._root, relative_path)


class SoundService:
    """Carga y caché de `pygame.mixer.Sound`."""

    def __init__(self, project_root: Path):
        self._root = project_root
        self._cache: dict[str, pygame.mixer.Sound] = {}

    def load(self, relative_path: str) -> pygame.mixer.Sound:
        if not relative_path:
            raise ValueError("ruta de sonido vacía")
        rel = relative_path.replace("\\", "/")
        key = str((self._root / rel).resolve()) if not Path(rel).is_absolute() else str(Path(rel).resolve())
        if key not in self._cache:
            path = Path(rel) if Path(rel).is_absolute() else self._root / rel
            self._cache[key] = pygame.mixer.Sound(str(path))
        return self._cache[key]


class FontService:
    """Carga y caché de `pygame.font.Font` por (ruta .ttf, tamaño)."""

    def __init__(self, project_root: Path):
        self._root = project_root
        self._cache: dict[tuple[str, int], pygame.font.Font] = {}

    def get(self, relative_path: str, size_px: int) -> pygame.font.Font:
        rel = relative_path.replace("\\", "/")
        size_px = max(1, int(size_px))
        key = (rel, size_px)
        if key not in self._cache:
            path = Path(rel) if Path(rel).is_absolute() else self._root / rel
            self._cache[key] = pygame.font.Font(str(path), size_px)
        return self._cache[key]
