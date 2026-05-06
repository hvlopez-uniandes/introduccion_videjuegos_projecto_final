"""Mantienen humano visualmente sujeto a Lander o a la nave al rescatar."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagAstronaut, CTagPlayer


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is None:
        return 8.0, 10.0
    return float(sz.w), float(sz.h)


def system_astronaut_carried_sync():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (p_pos, _) = players[0]
    pw, ph = _dims(pe)

    for ae, (pos, st, _foot, _ta) in esper.get_components(
        CPosition, CAstronautState, CAstronautFootprint, CTagAstronaut,
    ):
        if st.mode != CAstronautState.LANDER_CARRY and st.mode != CAstronautState.SHIP_CARRY:
            continue
        ce = st.carrier_ent
        if not esper.entity_exists(ce):
            if st.mode == CAstronautState.LANDER_CARRY:
                st.mode = CAstronautState.FALLING
            else:
                st.mode = CAstronautState.FALLING
            st.carrier_ent = -1
            continue
        cpos = esper.try_component(ce, CPosition)
        if cpos is None:
            st.mode = CAstronautState.FALLING
            st.carrier_ent = -1
            continue
        aw, ah = _dims(ae)
        lw, lh = _dims(ce)

        if st.mode == CAstronautState.SHIP_CARRY and ce == pe:
            pos.x = cpos.x + (lw - aw) * 0.47
            pos.y = cpos.y - ah * 0.92
        elif st.mode == CAstronautState.LANDER_CARRY:
            pos.x = cpos.x + (lw - aw) * 0.5
            pos.y = cpos.y - lh * 0.35 - ah * 0.88
