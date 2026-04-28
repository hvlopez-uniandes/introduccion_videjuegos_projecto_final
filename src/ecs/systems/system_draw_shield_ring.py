import math

import esper
import pygame

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_shield_special import CShieldSpecial
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer


def system_draw_shield_ring(surface: pygame.Surface) -> None:
    for pe, (pos, shield, _tp) in esper.get_components(CPosition, CShieldSpecial, CTagPlayer):
        if shield.active_remaining <= 0.0:
            continue
        surf = esper.try_component(pe, CSurface)
        sz = esper.try_component(pe, CSize)
        if surf is not None:
            cx = int(pos.x + surf.area_w / 2.0)
            cy = int(pos.y + surf.area_h / 2.0)
        elif sz is not None:
            cx = int(pos.x + sz.w / 2.0)
            cy = int(pos.y + sz.h / 2.0)
        else:
            continue
        r = int(max(4.0, shield.radius_px))
        t = shield.active_remaining / max(shield.duration_sec, 1e-6)
        pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.02))
        col = (80, 220, 255, int(90 * pulse * t + 40))
        ring = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(ring, col, (cx, cy), r, width=4)
        surface.blit(ring, (0, 0))
