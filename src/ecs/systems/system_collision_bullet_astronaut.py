"""Láser jugador vs astronautas (friendly fire y penalización configurada)."""

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagAstronaut, CTagBullet, CTagEnemyBullet
from src.ecs.systems.spawn_explosion import spawn_explosion
import src.engine.game_state as game_state


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is None:
        return 0.0, 0.0
    return float(sz.w), float(sz.h)


def _overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def system_collision_bullet_astronaut():
    penalty = int(game_state.get_rule("score_human_friend_fire", -180))
    bullets = []
    for be, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        if esper.try_component(be, CTagEnemyBullet):
            continue
        bw, bh = _dims(be)
        bullets.append((be, pos, bw, bh))

    astros = []
    for ae, (pos, st, _ta) in esper.get_components(CPosition, CAstronautState, CTagAstronaut):
        aw, ah = _dims(ae)
        astros.append((ae, pos, st, aw, ah))

    rm = []
    rm_a = []
    for be, bpos, bw, bh in bullets:
        for ae, apos, st, aw, ah in astros:
            if ae in rm_a:
                continue
            if st.mode == CAstronautState.LANDER_CARRY:
                continue
            if _overlap(bpos.x, bpos.y, bw, bh, apos.x, apos.y, aw, ah):
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
