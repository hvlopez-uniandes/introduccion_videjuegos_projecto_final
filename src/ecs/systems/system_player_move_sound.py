import math

import esper
import pygame

import src.engine.game_state as game_state

from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_tags import CTagPlayer
from src.ecs.components.c_velocity import CVelocity
from src.engine.audio_util import play_sound

_MIN_SPEED = 12.0
_INTERVAL_MS = 140


def system_player_move_sound() -> None:
    if game_state.paused:
        return
    now = pygame.time.get_ticks()
    for _, (vel, sfx, _tp) in esper.get_components(CVelocity, CPlayerSfx, CTagPlayer):
        if not sfx.move_sound_path:
            continue
        if math.hypot(vel.vx, vel.vy) < _MIN_SPEED:
            continue
        if sfx.mark_move_sound(now, _INTERVAL_MS):
            play_sound(sfx.move_sound_path, 0.12)
