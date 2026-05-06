"""Hyperspace: salto aleatorio con riesgo de destrucción (FAQ arcade)."""

import random

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.engine.audio_util import play_sound
from src.engine.frame_input import consume_hyperspace


def _player_dims(ent: int):
    surf = esper.try_component(ent, CSurface)
    if surf is not None:
        return surf.area_w, surf.area_h
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 16.0, 16.0


def system_arcade_hyperspace():
    if not game_state.arcade_defender_flight or game_state.paused:
        return
    if not consume_hyperspace():
        return

    players = list(esper.get_components(CTagPlayer, CPosition, CVelocity))
    if not players:
        return
    ent, (_tp, pos, vel) = players[0]
    w, h = _player_dims(ent)
    ww = float(game_state.world_wrap_w or game_state.world_screen_w or 320)
    sh = float(game_state.world_screen_h or 256)

    eff_top = 0.0
    if game_state.play_area_top_px is not None:
        eff_top = max(0.0, float(game_state.play_area_top_px))
    bottom = sh
    if game_state.play_area_bottom_px is not None:
        bottom = float(game_state.play_area_bottom_px)
    bottom = min(bottom, sh)
    min_y = eff_top
    max_y = max(min_y, bottom - h)
    max_x = max(0.0, ww - w)

    chance = float(game_state.get_rule("hyperspace_death_chance", 0.35))
    cx = pos.x + w / 2.0
    cy = pos.y + h / 2.0

    if random.random() < chance:
        spawn_explosion(cx, cy)
        play_sound("assets/snd/explosion.ogg", 0.42)
        if game_state.lose_life():
            game_state.respawn_player_entity(ent)
        vel.vx = 0.0
        vel.vy = 0.0
        return

    pos.x = random.uniform(4.0, max_x)
    pos.y = random.uniform(min_y, max_y)
    vel.vx *= 0.35
    vel.vy *= 0.35
    play_sound("assets/snd/laser.ogg", 0.18)
