"""Raíz del proyecto (la setea GameEngine al iniciar)."""

import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = None


def resolve_project_root(anchor_file: Optional[Path] = None) -> Path:
    """Raíz con assets/ y main.py; compatible con PyInstaller y pygbag."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path.cwd()))
    if anchor_file is not None:
        return anchor_file.resolve().parents[2]
    return Path.cwd()


def set_project_root(path):
    global PROJECT_ROOT
    PROJECT_ROOT = path
