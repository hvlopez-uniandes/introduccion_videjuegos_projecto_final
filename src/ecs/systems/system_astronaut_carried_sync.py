"""Mantienen humano visualmente sujeto a Lander o a la nave al rescatar."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagAstronaut, CTagPlayer
from src.ecs.systems.collision_util import get_entity_dims

def system_astronaut_carried_sync():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (p_pos, _) = players[0]
    pw, ph = get_entity_dims(pe, fallback=(8.0, 10.0))

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
        aw, ah = get_entity_dims(ae, fallback=(8.0, 10.0))
        lw, lh = get_entity_dims(ce, fallback=(8.0, 10.0))

        if st.mode == CAstronautState.SHIP_CARRY and ce == pe:
            pos.x = cpos.x + (lw - aw) * 0.47
            pos.y = cpos.y - ah * 0.92
        elif st.mode == CAstronautState.LANDER_CARRY:
            pos.x = cpos.x + (lw - aw) * 0.5
            pos.y = cpos.y - lh * 0.35 - ah * 0.88
