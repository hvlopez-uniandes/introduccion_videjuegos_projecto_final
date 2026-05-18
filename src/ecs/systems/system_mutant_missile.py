"""Misiles pequeños lanzados aleatoriamente por mutantes ECS."""

import math
import random

import esper

from src.ecs.components.c_color import CColor
from src.ecs.components.c_missile_burst import CMissileBurst
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_tags import CTagEnemy, CTagEnemyBullet, CTagEnemyMissile, CTagMutant, CTagPlayer
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.collision_util import get_entity_dims
import src.engine.game_state as game_state
from src.engine.viewport import aabb_in_viewport





def system_mutant_missile(delta_time):
    if delta_time <= 0.0:
        return
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    _, (ppos, _) = players[0]
    pe = players[0][0]
    pw, ph = get_entity_dims(pe, fallback=(12.0, 8.0))
    vis = aabb_in_viewport(float(ppos.x), float(ppos.y), pw, ph, margin=8.0)
    if not vis:
        return

    p_try = float(game_state.get_rule("missile_chance_per_sec", 0.1)) * delta_time
    spd = float(game_state.get_rule("missile_speed", 95.0))

    for ent, (pos, burst, _, _tm) in esper.get_components(
        CPosition,
        CMissileBurst,
        CTagEnemy,
        CTagMutant,
    ):
        burst.timer = max(0.0, burst.timer - delta_time)
        if burst.timer > 0.0:
            continue
        if random.random() > p_try:
            continue

        ew, eh = get_entity_dims(ent, fallback=(10.0, 10.0))
        ecx = pos.x + ew * 0.5
        ecy = pos.y + eh * 0.5
        pcx = ppos.x + pw * 0.5
        pcy = ppos.y + ph * 0.5
        fdx = pcx - ecx
        fdy = pcy - ecy
        dist = math.hypot(fdx, fdy)
        if dist < 6.0:
            continue
        fdx /= dist
        fdy /= dist

        mw, mh = 5.5, 5.5
        ms = esper.create_entity()
        esper.add_component(ms, CPosition(ecx - mw * 0.5, ecy - mh * 0.5))
        esper.add_component(ms, CVelocity(fdx * spd, fdy * spd))
        esper.add_component(ms, CSize(mw, mh))
        esper.add_component(ms, CColor(255, 215, 64))
        esper.add_component(ms, CTagEnemyBullet())
        esper.add_component(ms, CTagEnemyMissile())

        burst.timer = burst.cooldown
