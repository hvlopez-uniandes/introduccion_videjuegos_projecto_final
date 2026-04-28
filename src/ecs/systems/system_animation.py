import esper

from src.ecs.components.c_animation import CAnimation


def system_animation(delta_time):
    for _ent, anim in esper.get_component(CAnimation):
        if anim.finished:
            continue
        clip = anim.clips[anim.current_name]
        if clip.start == clip.end:
            anim.current_frame = clip.start
            continue

        anim.subframe_accum += delta_time * clip.framerate
        while anim.subframe_accum >= 1.0:
            anim.subframe_accum -= 1.0
            if anim.current_frame < clip.end:
                anim.current_frame += 1
            else:
                if clip.loops:
                    anim.current_frame = clip.start
                else:
                    anim.current_frame = clip.end
                    anim.finished = True
                    break
