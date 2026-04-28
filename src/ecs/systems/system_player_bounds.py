import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer


def system_player_bounds(screen_w, screen_h):
    sw = float(screen_w)
    sh = float(screen_h)

    for ent, (pos, _tp) in esper.get_components(CPosition, CTagPlayer):
        surf = esper.try_component(ent, CSurface)
        if surf is not None:
            aw = surf.area_w
            ah = surf.area_h
        else:
            sz = esper.try_component(ent, CSize)
            if sz is None:
                continue
            aw = float(sz.w)
            ah = float(sz.h)

        max_x = max(0.0, sw - aw)
        max_y = max(0.0, sh - ah)
        if pos.x < 0:
            pos.x = 0.0
        elif pos.x > max_x:
            pos.x = max_x
        if pos.y < 0:
            pos.y = 0.0
        elif pos.y > max_y:
            pos.y = max_y
