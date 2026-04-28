import pygame


def pygame_key_from_string(name: str) -> int:
    """Convierte un nombre legible (p. ej. SPACE, Q) a constante pygame."""
    n = (name or "SPACE").strip().upper()
    if len(n) == 1:
        return getattr(pygame, "K_" + n.lower())
    attr = "K_" + n
    if hasattr(pygame, attr):
        return getattr(pygame, attr)
    return pygame.K_SPACE
