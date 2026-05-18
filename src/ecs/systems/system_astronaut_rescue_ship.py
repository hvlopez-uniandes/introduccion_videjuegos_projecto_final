"""Rescate tipo Defender: recoger caídas con la nave y soltar puntos tras tocar superficie."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagAstronaut, CTagPlayer
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap
from src.engine.scenario_profile import planet_edge_screen_y
from src.engine.scenario_query import get_planet_profile
import src.engine.game_state as game_state





def system_astronaut_rescue_pickup():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (ppos, _) = players[0]
    pw, ph = get_entity_dims(pe, fallback=(8.0, 10.0))

    for ae, (apos, st, _foot, _ta) in esper.get_components(
        CPosition, CAstronautState, CAstronautFootprint, CTagAstronaut,
    ):
        if st.mode != CAstronautState.FALLING:
            continue
        aw, ah = get_entity_dims(ae, fallback=(8.0, 10.0))
        if aabb_overlap(ppos.x, ppos.y, pw, ph, apos.x, apos.y, aw, ah):
            st.mode = CAstronautState.SHIP_CARRY
            st.carrier_ent = pe


def system_astronaut_rescue_deposit():
    pl = get_planet_profile()
    if pl is None:
        return
    rescue_pts = int(game_state.get_rule("score_human_rescue", 500))
    for ae, (apos, st, foot, _ta) in esper.get_components(
        CPosition, CAstronautState, CAstronautFootprint, CTagAstronaut,
    ):
        if st.mode != CAstronautState.SHIP_CARRY:
            continue
        aw, ah = get_entity_dims(ae, fallback=(8.0, 10.0))
        cx = apos.x + aw * 0.5
        sy = planet_edge_screen_y(pl, cx)
        feet = apos.y + ah
        if feet >= sy - foot.clearance_px_above_terrain_line - 2.0:
            st.mode = CAstronautState.GROUND
            st.carrier_ent = -1
            game_state.add_score(rescue_pts)
