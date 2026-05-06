"""FAQ arcade: nave parcialmente oculta bajo la silueta del relieve (solo fase superficie)."""

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_scenario import CScenarioPlanetProfile
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer
from src.engine.scenario_profile import planet_edge_screen_y


def system_player_terrain_occlusion() -> None:
    game_state.player_occluded_by_terrain = False
    if game_state.scenario_space_skirmish or not game_state.defense_arcade_enabled:
        return
    planets = list(esper.get_components(CScenarioPlanetProfile))
    if not planets:
        return
    _, (pl,) = planets[0]
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (pos, _) = players[0]
    surf = esper.try_component(pe, CSurface)
    sz = esper.try_component(pe, CSize)
    if surf is not None:
        pw, ph = float(surf.area_w), float(surf.area_h)
    elif sz is not None:
        pw, ph = float(sz.w), float(sz.h)
    else:
        return
    sh = float(game_state.world_screen_h or 256)
    ridge = planet_edge_screen_y(pl, float(pos.x) + pw * 0.5)
    lip_px = float(game_state.get_rule("terrain_occlusion_lip_px", 6.0))
    mid_y = float(pos.y) + ph * 0.52
    game_state.player_occluded_by_terrain = mid_y > ridge + lip_px and float(pos.y) + ph < sh - 4.0
