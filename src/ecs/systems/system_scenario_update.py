import math

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_scenario import CScenarioPlanetProfile, CScenarioStarfield


def system_scenario_update(delta_time: float) -> None:
    if delta_time <= 0.0:
        return
    if game_state.paused:
        return

    for _, (sf,) in esper.get_components(CScenarioStarfield):
        sw = float(max(1, sf.screen_w))
        sf.scroll_x = (sf.scroll_x + delta_time * sf.stars_scroll_px_s) % sw

    for _, (pl,) in esper.get_components(CScenarioPlanetProfile):
        sw = float(max(1, pl.screen_w))
        pl.scroll_x = (pl.scroll_x + delta_time * pl.planet_scroll_px_s) % sw

    for _, (sf,) in esper.get_components(CScenarioStarfield):
        for star in sf.stars:
            star.phase = (star.phase + delta_time * star.blink_rad_s) % (2.0 * math.pi)
