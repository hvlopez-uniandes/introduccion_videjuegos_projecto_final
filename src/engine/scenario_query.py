"""Consultas de escenario vía ECS (planet profile global)."""

import esper

from src.ecs.components.c_scenario import CScenarioPlanetProfile


def get_planet_profile():
    """Primer perfil planetario cargado (`None` antes de iniciar mundo)."""
    for _, (pl,) in esper.get_components(CScenarioPlanetProfile):
        return pl
    return None
