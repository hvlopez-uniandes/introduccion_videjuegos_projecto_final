"""Choque láser jugador vs balas enemigas — elimina la bala enemiga."""

import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagBullet, CTagEnemyBullet
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap


def system_collision_bullet_enemy_bullet():
    lasers = []
    for be, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        if esper.try_component(be, CTagEnemyBullet) is not None:
            continue
        bw, bh = get_entity_dims(be)
        lasers.append((be, pos, bw, bh))

    ebs = []
    for ee, (pos, _teb) in esper.get_components(CPosition, CTagEnemyBullet):
        ew, eh = get_entity_dims(ee)
        ebs.append((ee, pos, ew, eh))

    rm = []
    for be, bpos, bw, bh in lasers:
        for ee, epos, ew, eh in ebs:
            if ee in rm:
                continue
            if aabb_overlap(bpos.x, bpos.y, bw, bh, epos.x, epos.y, ew, eh):
                rm.append(ee)
    for ent in rm:
        esper.delete_entity(ent, immediate=True)
