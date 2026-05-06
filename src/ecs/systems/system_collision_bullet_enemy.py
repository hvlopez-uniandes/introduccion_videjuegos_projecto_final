"""Láser jugador atraviesa enemigos sólo visibles; no se destruye por impacto."""

import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_pod_cargo import CPodCargo
from src.ecs.components.c_tags import (
    CTagBullet,
    CTagEnemy,
    CTagEnemyBullet,
    CTagPod,
)
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.ecs.systems.spawn_pod_swarm import spawn_swarmers_from_pod_cargo
from src.ecs.systems.system_lander_ai import release_human_from_dead_lander
import src.engine.game_state as game_state
from src.engine.enemy_kill_score import score_for_destroyed_enemy
from src.engine.viewport import aabb_in_viewport


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 0.0, 0.0


def _overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _enemy_visible(px, py, pw, ph):
    return aabb_in_viewport(float(px), float(py), float(pw), float(ph), margin=8.0)


def system_collision_bullet_enemy():
    bullets = []
    for e, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        if esper.try_component(e, CTagEnemyBullet) is not None:
            continue
        bw, bh = _dims(e)
        bullets.append((e, pos, bw, bh))

    enemies = []
    for e, (pos, _te) in esper.get_components(CPosition, CTagEnemy):
        ew, eh = _dims(e)
        enemies.append((e, pos, ew, eh))

    to_kill = []
    for be, bpos, bw, bh in bullets:
        for ee, epos, ew, eh in enemies:
            if ee in to_kill:
                continue
            if not _overlap(
                bpos.x, bpos.y, bw, bh,
                epos.x, epos.y, ew, eh,
            ):
                continue
            if not _enemy_visible(epos.x, epos.y, ew, eh):
                continue
            to_kill.append(ee)

    for ee in to_kill:
        epos = esper.try_component(ee, CPosition)
        ew, eh = _dims(ee)
        if epos is not None:
            cx = epos.x + ew / 2.0
            cy = epos.y + eh / 2.0
            spawn_explosion(cx, cy)
            if esper.try_component(ee, CTagPod) is not None:
                cargo = esper.try_component(ee, CPodCargo)
                if cargo is not None:
                    spawn_swarmers_from_pod_cargo(cx, cy, cargo)
        release_human_from_dead_lander(ee)
        game_state.add_score(score_for_destroyed_enemy(ee))
        esper.delete_entity(ee, immediate=True)
