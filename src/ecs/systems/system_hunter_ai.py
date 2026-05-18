import math

import esper

from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_tags import CTagBaiter, CTagHunter, CTagMutant, CTagPod, CTagPlayer, CTagSwarmer
from src.ecs.components.c_velocity import CVelocity
from src.engine.audio_util import play_sound


def _tick_brain(pos, vel, ai, ppos):
    prev_state = ai.state
    dx_p = ppos.x - pos.x
    dy_p = ppos.y - pos.y
    dist_p = math.hypot(dx_p, dy_p)
    dist_o = math.hypot(pos.x - ai.origin_x, pos.y - ai.origin_y)

    if ai.state == "return":
        dx = ai.origin_x - pos.x
        dy = ai.origin_y - pos.y
        d = math.hypot(dx, dy)
        if d < 2.0:
            pos.x = ai.origin_x
            pos.y = ai.origin_y
            vel.vx = 0.0
            vel.vy = 0.0
            ai.state = "idle"
        else:
            vel.vx = dx / d * ai.v_return
            vel.vy = dy / d * ai.v_return
    elif ai.state == "chase":
        if dist_o > ai.return_dist + 0.5:
            ai.state = "return"
            return prev_state, True
        if dist_p < 1e-6:
            vel.vx = 0.0
            vel.vy = 0.0
        else:
            vel.vx = dx_p / dist_p * ai.v_chase
            vel.vy = dy_p / dist_p * ai.v_chase
    else:
        vel.vx = 0.0
        vel.vy = 0.0
        if dist_p <= ai.chase_dist:
            ai.state = "chase"
    return prev_state, False


def _process_ai_group(tag_class, ppos, volume):
    for _ent, (pos, vel, ai, _) in esper.get_components(CPosition, CVelocity, CHunterAI, tag_class):
        prev, skipped = _tick_brain(pos, vel, ai, ppos)
        if skipped:
            continue
        if prev == "idle" and ai.state == "chase" and ai.sound_chase_path:
            play_sound(ai.sound_chase_path, volume)


def system_hunter_ai():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    _, (ppos, _tp) = players[0]

    _process_ai_group(CTagHunter, ppos, 0.75)
    _process_ai_group(CTagMutant, ppos, 0.55)
    _process_ai_group(CTagSwarmer, ppos, 0.68)
    _process_ai_group(CTagBaiter, ppos, 0.82)
    _process_ai_group(CTagPod, ppos, 0.34)
