import pygame
import esper

from src.ecs.commands import (
    PlayerDownCommand,
    PlayerFireCommand,
    PlayerLeftCommand,
    PlayerRightCommand,
    PlayerUpCommand,
)
from src.ecs.components.c_input_command import CInputCommand


def system_input_command():
    keys = pygame.key.get_pressed()
    mouse_down = pygame.mouse.get_pressed()[0]
    mx, my = pygame.mouse.get_pos()

    for _, cmd in esper.get_component(CInputCommand):
        q = []
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

        cmd.prev_mouse_down = mouse_down
        cmd.command_queue = q
