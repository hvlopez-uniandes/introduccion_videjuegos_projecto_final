import pygame
import esper

import src.engine.game_state as game_state

from src.ecs.commands import (
    PlayerDownCommand,
    PlayerFireCommand,
    PlayerLeftCommand,
    PlayerReverseCommand,
    PlayerRightCommand,
    PlayerThrustHoldCommand,
    PlayerUpCommand,
)
from src.ecs.components.c_arcade_defender_flight import CArcadeDefenderFlight
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer


def system_input_command():
    keys = pygame.key.get_pressed()
    mouse_down = pygame.mouse.get_pressed()[0]
    mx, my = pygame.mouse.get_pos()

    centers = []
    for pe, (ppos, _tp) in esper.get_components(CPosition, CTagPlayer):
        s = esper.try_component(pe, CSurface)
        if s is not None:
            cx = ppos.x + s.area_w * 0.5
            cy = ppos.y + s.area_h * 0.5
        else:
            sz = esper.try_component(pe, CSize)
            if sz is None:
                continue
            cx = ppos.x + sz.w * 0.5
            cy = ppos.y + sz.h * 0.5
        centers.append((cx, cy))

    facing = 1
    if game_state.arcade_defender_flight:
        for _, (af, _tp) in esper.get_components(CArcadeDefenderFlight, CTagPlayer):
            facing = af.facing
            break

    for _, cmd in esper.get_component(CInputCommand):
        q = []

        if game_state.arcade_defender_flight:
            if keys[pygame.K_UP]:
                q.append(PlayerUpCommand())
            if keys[pygame.K_DOWN]:
                q.append(PlayerDownCommand())
            if keys[pygame.K_LEFT]:
                q.append(PlayerLeftCommand())
            if keys[pygame.K_RIGHT]:
                q.append(PlayerRightCommand())
            if keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                q.append(PlayerThrustHoldCommand())
            rev_down = keys[pygame.K_c]
            if rev_down and not cmd.prev_reverse_down:
                q.append(PlayerReverseCommand())
            cmd.prev_reverse_down = rev_down
        else:
            if keys[pygame.K_LEFT]:
                q.append(PlayerLeftCommand())
            if keys[pygame.K_RIGHT]:
                q.append(PlayerRightCommand())
            if keys[pygame.K_UP]:
                q.append(PlayerUpCommand())
            if keys[pygame.K_DOWN]:
                q.append(PlayerDownCommand())

        if mouse_down and not cmd.prev_mouse_down:
            q.append(PlayerFireCommand(mx, my))

        kb_fire = keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        if kb_fire and not cmd.prev_kb_fire_down and centers:
            cx, cy = centers[0]
            off = 140.0 * float(facing) if game_state.arcade_defender_flight else 140.0
            q.append(PlayerFireCommand(cx + off, cy))

        cmd.prev_mouse_down = mouse_down
        cmd.prev_kb_fire_down = kb_fire
        cmd.command_queue = q
