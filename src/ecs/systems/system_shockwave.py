import esper
import pygame

import src.engine.game_state as game_state
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_shockwave import CShockwave


def system_shockwave(delta_time: float, surface: pygame.Surface):
    if game_state.paused:
        return

    for ent, (pos, sw) in esper.get_components(CPosition, CShockwave):
        sw.elapsed += delta_time

        if sw.elapsed >= sw.lifetime:
            try:
                esper.delete_entity(ent, immediate=True)
            except KeyError:
                pass
            continue

        progress = sw.elapsed / sw.lifetime
        radius = int(sw.max_radius * progress)
        alpha = int(255 * (1.0 - progress))

        ring = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (sw.r, sw.g, sw.b, alpha),(radius + 2, radius + 2), radius, 10)
        surface.blit(ring, (int(pos.x) - radius - 2, int(pos.y) - radius - 2))