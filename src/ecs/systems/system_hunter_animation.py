import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_tags import CTagHunter
from src.ecs.components.c_velocity import CVelocity


def system_hunter_animation():
    for _ent, (vel, ai, anim, _th) in esper.get_components(CVelocity, CHunterAI, CAnimation, CTagHunter):
        moving = ai.state in ("chase", "return") and (abs(vel.vx) > 0.01 or abs(vel.vy) > 0.01)
        want = "MOVE" if moving else "IDLE"
        if want in anim.clips and want != anim.current_name:
            anim.set_clip(want)
