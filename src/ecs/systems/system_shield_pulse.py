import math

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_shield_special import CShieldSpecial
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagPlayer
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.engine.audio_util import play_sound
from src.engine.frame_input import consume_shield_pulse


def _player_center(pe):
    pos = esper.try_component(pe, CPosition)
    if pos is None:
        return None
    surf = esper.try_component(pe, CSurface)
    if surf is not None:
        return pos.x + surf.area_w / 2.0, pos.y + surf.area_h / 2.0
    sz = esper.try_component(pe, CSize)
    if sz is not None:
        return pos.x + sz.w / 2.0, pos.y + sz.h / 2.0
    return None


def _enemy_center(ee):
    pos = esper.try_component(ee, CPosition)
    if pos is None:
        return None
    surf = esper.try_component(ee, CSurface)
    if surf is not None:
        return pos.x + surf.area_w / 2.0, pos.y + surf.area_h / 2.0
    sz = esper.try_component(ee, CSize)
    if sz is not None:
        return pos.x + sz.w / 2.0, pos.y + sz.h / 2.0
    return None


def system_shield_pulse(delta_time: float) -> None:
    if game_state.paused:
        return
    players = list(esper.get_components(CShieldSpecial, CTagPlayer))
    if not players:
        return
    pe, (shield, _tp) = players[0]

    if consume_shield_pulse():
        if shield.active_remaining <= 0.0 and shield.cooldown_remaining <= 0.0:
            shield.active_remaining = shield.duration_sec
            play_sound("assets/snd/laser.ogg", 0.32)

    if shield.active_remaining > 0.0:
        center = _player_center(pe)
        if center is not None:
            cx, cy = center
            to_kill = []
            for ee, (epos, _te) in esper.get_components(CPosition, CTagEnemy):
                ec = _enemy_center(ee)
                if ec is None:
                    continue
                ex, ey = ec
                if math.hypot(ex - cx, ey - cy) <= shield.radius_px:
                    to_kill.append((ee, ex, ey))
            for ee, ex, ey in to_kill:
                spawn_explosion(ex, ey)
                esper.delete_entity(ee, immediate=True)

        shield.active_remaining = max(0.0, shield.active_remaining - delta_time)
        if shield.active_remaining <= 0.0:
            shield.cooldown_remaining = shield.cooldown_sec
    elif shield.cooldown_remaining > 0.0:
        shield.cooldown_remaining = max(0.0, shield.cooldown_remaining - delta_time)
