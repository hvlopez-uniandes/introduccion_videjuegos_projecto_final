import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet


def system_bullet_bounds(screen_w, screen_h):
    sw = float(screen_w)
    sh = float(screen_h)
    to_kill = []

    for ent, (pos, _tb) in esper.get_components(CPosition, CTagBullet):
        surf = esper.try_component(ent, CSurface)
        if surf is not None:
            w, h = surf.area_w, surf.area_h
        else:
            sz = esper.try_component(ent, CSize)
            if sz is None:
                continue
            w, h = float(sz.w), float(sz.h)

        if pos.x + w <= 0 or pos.x >= sw or pos.y + h <= 0 or pos.y >= sh:
            to_kill.append(ent)

    for ent in to_kill:
        esper.delete_entity(ent, immediate=True)
