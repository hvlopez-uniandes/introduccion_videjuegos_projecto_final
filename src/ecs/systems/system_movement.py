import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_velocity import CVelocity


def system_movement(delta_time):
    for _entity, (pos, vel) in esper.get_components(CPosition, CVelocity):
        pos.x = pos.x + vel.vx * delta_time
        pos.y = pos.y + vel.vy * delta_time
