import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet, CTagEnemy
from src.ecs.systems.spawn_explosion import spawn_explosion


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 0.0, 0.0


def _aabb_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def system_collision_bullet_enemy():
    bullets = []
    for e, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        bw, bh = _dims(e)
        bullets.append((e, pos, bw, bh))

    enemies = []
    for e, (pos, _te) in esper.get_components(CPosition, CTagEnemy):
        ew, eh = _dims(e)
        enemies.append((e, pos, ew, eh))

    to_remove = set()

    for be, bpos, bw, bh in bullets:
        if be in to_remove:
            continue
        for ee, epos, ew, eh in enemies:
            if ee in to_remove:
                continue
            if _aabb_overlap(
                bpos.x,
                bpos.y,
                bw,
                bh,
                epos.x,
                epos.y,
                ew,
                eh,
            ):
                cx = (bpos.x + bw / 2.0 + epos.x + ew / 2.0) / 2.0
                cy = (bpos.y + bh / 2.0 + epos.y + eh / 2.0) / 2.0
                spawn_explosion(cx, cy)
                to_remove.add(be)
                to_remove.add(ee)

    for ent in to_remove:
        esper.delete_entity(ent, immediate=True)
