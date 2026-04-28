import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_color import CColor
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagExplosion, CTagHud, CTagHudDynamic


def _blit_sprite(surface, pos, surf, anim):
    if anim is not None:
        fi = int(anim.current_frame)
        fi = max(0, min(fi, surf.num_frames - 1))
    else:
        fi = 0
    x = fi * surf.frame_w
    rect = pygame.Rect(x, 0, surf.frame_w, surf.frame_h)
    piece = surf.surface.subsurface(rect)
    surface.blit(piece, (int(pos.x), int(pos.y)))


def _is_hud(ent):
    return esper.try_component(ent, CTagHud) is not None or esper.try_component(ent, CTagHudDynamic) is not None


def system_draw(surface):
    for _ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if _is_hud(_ent):
            continue
        if esper.try_component(_ent, CTagExplosion) is not None:
            continue
        anim = esper.try_component(_ent, CAnimation)
        _blit_sprite(surface, pos, surf, anim)

    for _ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if esper.try_component(_ent, CTagExplosion) is None:
            continue
        anim = esper.try_component(_ent, CAnimation)
        _blit_sprite(surface, pos, surf, anim)

    for _ent, (pos, size, color) in esper.get_components(CPosition, CSize, CColor):
        if esper.try_component(_ent, CSurface) is not None:
            continue
        if _is_hud(_ent):
            continue
        r = pygame.Rect(int(pos.x), int(pos.y), int(size.w), int(size.h))
        pygame.draw.rect(surface, (color.r, color.g, color.b), r)

    for _ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if esper.try_component(_ent, CTagHud) is None and esper.try_component(_ent, CTagHudDynamic) is None:
            continue
        if esper.try_component(_ent, CTagExplosion) is not None:
            continue
        anim = esper.try_component(_ent, CAnimation)
        _blit_sprite(surface, pos, surf, anim)
