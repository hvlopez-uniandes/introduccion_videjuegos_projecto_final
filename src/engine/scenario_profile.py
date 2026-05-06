"""Muestreo del perfil planetario períodico (escenario ECS)."""

import math

from src.ecs.components.c_scenario import CScenarioPlanetProfile


def planet_edge_screen_y(planet: CScenarioPlanetProfile, screen_x_px: float) -> float:
    """Borde superior del relieve en pantalla al desplazar el patrón (parallax incluido en `planet.scroll_x`)."""
    ux = float(screen_x_px + planet.scroll_x)
    sw = float(max(1, planet.screen_w))
    n = len(planet.offsets)
    if n <= 0:
        return float(planet.baseline_y)
    q = ux / sw
    q = q - math.floor(q)
    t = q * float(n)
    fi = int(t) % n
    fi_next = (fi + 1) % n
    frac = t - math.floor(t)
    h0 = planet.offsets[fi]
    h1 = planet.offsets[fi_next]
    return float(planet.baseline_y + (h0 + (h1 - h0) * frac))
