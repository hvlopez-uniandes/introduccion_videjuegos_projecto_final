import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagHunter
from src.ecs.components.c_velocity import CVelocity


def system_bounce(screen_w, screen_h):
    sw = float(screen_w)
    sh = float(screen_h)

    for ent, (pos, vel, surf, _te) in esper.get_components(CPosition, CVelocity, CSurface, CTagEnemy):
        if esper.try_component(ent, CTagHunter) is not None:
            continue
        aw = surf.area_w
        ah = surf.area_h
        max_x = max(0.0, sw - aw)
        max_y = max(0.0, sh - ah)

        if pos.x < 0:
            pos.x = 0.0
            vel.vx = abs(vel.vx)
        elif pos.x > max_x:
            pos.x = max_x
            vel.vx = -abs(vel.vx)

        if pos.y < 0:
            pos.y = 0.0
            vel.vy = abs(vel.vy)
        elif pos.y > max_y:
            pos.y = max_y
            vel.vy = -abs(vel.vy)
