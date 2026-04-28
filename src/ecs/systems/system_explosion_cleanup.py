import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_tags import CTagExplosion


def system_explosion_cleanup():
    to_kill = []
    for ent, (anim, _te) in esper.get_components(CAnimation, CTagExplosion):
        if anim.finished:
            to_kill.append(ent)
    for ent in to_kill:
        esper.delete_entity(ent, immediate=True)
