"""Raíz del proyecto (la setea GameEngine al iniciar)."""

PROJECT_ROOT = None


def set_project_root(path):
    global PROJECT_ROOT
    PROJECT_ROOT = path
