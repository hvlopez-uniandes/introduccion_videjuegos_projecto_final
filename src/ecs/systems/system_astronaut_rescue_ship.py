"""Rescate tipo Defender: recoger caídas con la nave y soltar puntos tras tocar superficie."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagAstronaut, CTagPlayer
from src.engine.scenario_profile import planet_edge_screen_y
from src.engine.scenario_query import get_planet_profile
import src.engine.game_state as game_state


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is None:
        return 8.0, 10.0
    return float(sz.w), float(sz.h)


def _overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def system_astronaut_rescue_pickup():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (ppos, _) = players[0]
    pw, ph = _dims(pe)

    for ae, (apos, st, _foot, _ta) in esper.get_components(
        CPosition, CAstronautState, CAstronautFootprint, CTagAstronaut,
    ):
        if st.mode != CAstronautState.FALLING:
            continue
        aw, ah = _dims(ae)
        if _overlap(ppos.x, ppos.y, pw, ph, apos.x, apos.y, aw, ah):
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
        aw, ah = _dims(ae)
        cx = apos.x + aw * 0.5
        sy = planet_edge_screen_y(pl, cx)
        feet = apos.y + ah
        if feet >= sy - foot.clearance_px_above_terrain_line - 2.0:
            st.mode = CAstronautState.GROUND
            st.carrier_ent = -1
            game_state.add_score(rescue_pts)
