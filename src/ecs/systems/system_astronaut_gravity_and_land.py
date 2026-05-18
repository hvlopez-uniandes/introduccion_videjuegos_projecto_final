"""Gravedad en caída y contacto simple con línea-planeta antes del snap visual."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagAstronaut
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.collision_util import get_entity_dims
import src.engine.game_state as game_state
from src.engine.scenario_profile import planet_edge_screen_y
from src.engine.scenario_query import get_planet_profile

def system_astronaut_gravity(delta_time):
    if delta_time <= 0.0:
        return
    g = float(game_state.get_rule("gravity_human_px_s2", 520.0))
    for _ent, (pos, vel, st, _foot, _ta) in esper.get_components(
        CPosition,
        CVelocity,
        CAstronautState,
        CAstronautFootprint,
        CTagAstronaut,
    ):
        if st.mode != CAstronautState.FALLING:
            continue
        vel.vy += g * delta_time


def system_astronaut_landing_resolve():
    """Tras mover: pegar astronauta cayendo al suelo y detener velocidad."""
    pl = get_planet_profile()
    if pl is None:
        return
    for ae, (pos, vel, st, foot, _ta) in esper.get_components(
        CPosition,
        CVelocity,
        CAstronautState,
        CAstronautFootprint,
        CTagAstronaut,
    ):
        if st.mode != CAstronautState.FALLING:
            continue
        aw, ah = get_entity_dims(ae, fallback=(8.0, 10.0))
        cx = pos.x + aw * 0.5
        sy = planet_edge_screen_y(pl, cx)
        feet_y = pos.y + ah
        margin = sy - ah - foot.clearance_px_above_terrain_line + 4.0
        if feet_y >= margin:
            st.mode = CAstronautState.GROUND
            vel.vx = 0.0
            vel.vy = 0.0
            pos.y = sy - ah - foot.clearance_px_above_terrain_line
