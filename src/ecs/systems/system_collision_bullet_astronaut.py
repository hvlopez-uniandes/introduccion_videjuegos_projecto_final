"""Láser jugador vs astronautas (friendly fire y penalización configurada)."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagAstronaut, CTagBullet, CTagEnemyBullet
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap
from src.ecs.systems.spawn_explosion import spawn_explosion
import src.engine.game_state as game_state


def system_collision_bullet_astronaut():
    penalty = int(game_state.get_rule("score_human_friend_fire", -180))
    bullets = []
    for be, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        if esper.try_component(be, CTagEnemyBullet):
            continue
        bw, bh = get_entity_dims(be)
        bullets.append((be, pos, bw, bh))

    astros = []
    for ae, (pos, st, _ta) in esper.get_components(CPosition, CAstronautState, CTagAstronaut):
        aw, ah = get_entity_dims(ae)
        astros.append((ae, pos, st, aw, ah))

    rm = []
    rm_a = []
    for be, bpos, bw, bh in bullets:
        for ae, apos, st, aw, ah in astros:
            if ae in rm_a:
                continue
            if st.mode == CAstronautState.LANDER_CARRY:
                continue
            if aabb_overlap(bpos.x, bpos.y, bw, bh, apos.x, apos.y, aw, ah):
                cx = apos.x + aw * 0.5
                cy = apos.y + ah * 0.5
                spawn_explosion(cx, cy, play_spawn_sound=False)
                game_state.add_score(penalty)
                rm.append(be)
                rm_a.append(ae)
                break

    for ent in rm:
        esper.delete_entity(ent, immediate=True)
    for ent in rm_a:
        esper.delete_entity(ent, immediate=True)
