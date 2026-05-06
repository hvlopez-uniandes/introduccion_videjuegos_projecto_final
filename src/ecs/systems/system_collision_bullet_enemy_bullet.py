"""Choque láser jugador vs balas enemigas — elimina la bala enemiga."""

import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet, CTagEnemyBullet


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


def system_collision_bullet_enemy_bullet():
    lasers = []
    for be, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        if esper.try_component(be, CTagEnemyBullet) is not None:
            continue
        bw, bh = _dims(be)
        lasers.append((be, pos, bw, bh))

    ebs = []
    for ee, (pos, _teb) in esper.get_components(CPosition, CTagEnemyBullet):
        ew, eh = _dims(ee)
        ebs.append((ee, pos, ew, eh))

    rm = []
    for be, bpos, bw, bh in lasers:
        for ee, epos, ew, eh in ebs:
            if ee in rm:
                continue
            if _overlap(bpos.x, bpos.y, bw, bh, epos.x, epos.y, ew, eh):
                rm.append(ee)
    for ent in rm:
        esper.delete_entity(ent, immediate=True)
