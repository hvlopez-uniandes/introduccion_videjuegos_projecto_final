import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_tags import CTagPlayer
from src.ecs.components.c_velocity import CVelocity


def system_player_animation():
    for _ent, (vel, anim, _tp) in esper.get_components(CVelocity, CAnimation, CTagPlayer):
        moving = abs(vel.vx) > 0.05 or abs(vel.vy) > 0.05
        want = "MOVE" if moving else "IDLE"
        if want in anim.clips and want != anim.current_name:
            anim.set_clip(want)
