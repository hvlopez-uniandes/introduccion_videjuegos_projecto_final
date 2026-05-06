import esper

from src.engine.viewport import horiz_overlaps_viewport

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet, CTagEnemyBullet


def system_bullet_bounds(screen_w, screen_h):
    sh = float(screen_h)
    to_kill = []

    for ent, (pos,) in esper.get_components(CPosition):
        if esper.try_component(ent, CTagBullet) is None and esper.try_component(ent, CTagEnemyBullet) is None:
            continue
        surf = esper.try_component(ent, CSurface)
        if surf is not None:
            w, h = surf.area_w, surf.area_h
        else:
            sz = esper.try_component(ent, CSize)
            if sz is None:
                continue
            w, h = float(sz.w), float(sz.h)

        if (
            pos.y + h <= 0
            or pos.y >= sh
            or not horiz_overlaps_viewport(float(pos.x), float(w), margin=8.0)
        ):
            to_kill.append(ent)

    for ent in to_kill:
        esper.delete_entity(ent, immediate=True)
