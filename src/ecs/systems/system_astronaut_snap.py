import math

import esper

from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagAstronaut
from src.ecs.systems.collision_util import get_entity_dims
from src.engine.scenario_profile import planet_edge_screen_y
from src.engine.scenario_query import get_planet_profile

def system_astronaut_terrain_snap(delta_time: float) -> None:
    pl = get_planet_profile()
    if pl is None or delta_time <= 0.0:
        return

    for _ent, (pos, foot, _ta) in esper.get_components(CPosition, CAstronautFootprint, CTagAstronaut):
        st = esper.try_component(_ent, CAstronautState)
        if st is not None and st.mode != CAstronautState.GROUND:
            continue
        aw, ah = get_entity_dims(_ent, fallback=(6.0, 10.0))
        tau = getattr(math, "tau", math.pi * 2.0)
        foot.phase = (foot.phase + delta_time * foot.wobble_hz * tau) % tau
        cx = pos.x + aw * 0.5
        surface_y = planet_edge_screen_y(pl, cx)
        wob = math.sin(foot.phase) * foot.wobble_amplitude_px
        pos.y = surface_y - ah - foot.clearance_px_above_terrain_line + wob
