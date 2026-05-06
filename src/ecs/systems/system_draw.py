from __future__ import annotations

import esper
import pygame

import src.engine.game_state as game_state

from src.engine.viewport import world_to_screen_x_positions
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_color import CColor
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_arcade_defender_flight import CArcadeDefenderFlight
from src.ecs.components.c_player_arcade_burner import CPlayerArcadeBurner
from src.ecs.components.c_tags import CTagExplosion, CTagHud, CTagHudDynamic, CTagPlayer


def _sprite_draw_scale(world: bool = True):
    """Escala sólo dibujo (no colisiones): naves, enemigos, explosiones, rects de proyectiles."""
    if not world:
        return 1.0
    try:
        s = float(game_state.get_rule("sprite_draw_scale", 2.0))
    except (TypeError, ValueError):
        s = 2.0
    return max(0.8, min(4.25, s))


def _blit_sprite_frame(
    surface,
    pos_x,
    py,
    surf,
    frame_idx: int,
    flip_h: bool = False,
    alpha: int | None = None,
    world_scale: bool = True,
):
    fi = max(0, min(int(frame_idx), surf.num_frames - 1))
    x = fi * surf.frame_w
    rect = pygame.Rect(x, 0, surf.frame_w, surf.frame_h)
    piece = surf.surface.subsurface(rect)
    if flip_h:
        piece = pygame.transform.flip(piece, True, False)
    if alpha is not None and alpha < 255:
        piece = piece.copy()
        piece.set_alpha(int(max(0, min(255, alpha))))
    sc = _sprite_draw_scale(world=world_scale)
    if abs(sc - 1.0) > 1e-3:
        nw = max(1, int(round(float(piece.get_width()) * sc)))
        nh = max(1, int(round(float(piece.get_height()) * sc)))
        piece = pygame.transform.smoothscale(piece, (nw, nh))
        pos_x -= (nw - float(surf.frame_w)) * 0.5
        py -= (nh - float(surf.frame_h)) * 0.5
    surface.blit(piece, (int(pos_x), int(py)))


def _blit_sprite(
    surface,
    pos_x,
    py,
    surf,
    anim,
    flip_h: bool = False,
    alpha: int | None = None,
    world_scale: bool = True,
):
    if anim is not None:
        fi = int(anim.current_frame)
        fi = max(0, min(fi, surf.num_frames - 1))
    else:
        fi = 0
    _blit_sprite_frame(surface, pos_x, py, surf, fi, flip_h=flip_h, alpha=alpha, world_scale=world_scale)


def _draw_arcade_burners_behind_ship(surface):
    for ent, comps in esper.get_components(CPosition, CTagPlayer):
        pos = comps[0]
        br = esper.try_component(ent, CPlayerArcadeBurner)
        pl = esper.try_component(ent, CSurface)
        arc = esper.try_component(ent, CArcadeDefenderFlight)
        if br is None or pl is None or arc is None:
            continue

        alpha = None
        if game_state.player_occluded_by_terrain:
            alpha = int(game_state.get_rule("terrain_occlusion_alpha", 200))

        psw = float(pl.area_w)
        psh = float(pl.area_h)
        sheet = br.active_sheet()
        n = max(1, sheet.num_frames)
        fr_i = int(br.anim_t * br.anim_hz) % n

        tuck = float(br.tuck_px)
        if arc.facing >= 0:
            burn_x = float(pos.x) - float(sheet.frame_w) + tuck
            bflip = False
        else:
            burn_x = float(pos.x) + psw - tuck
            bflip = True
        burn_y = float(pos.y) + max(0.0, (psh - float(sheet.frame_h)) * 0.5)

        dx_world = burn_x - float(pos.x)
        ew = float(pl.area_w)
        for sx in world_to_screen_x_positions(float(pos.x), ew):
            screen_bx = sx + dx_world
            _blit_sprite_frame(surface, screen_bx, burn_y, sheet, fr_i, flip_h=bflip, alpha=alpha, world_scale=True)


def _is_hud(ent):
    return esper.try_component(ent, CTagHud) is not None or esper.try_component(ent, CTagHudDynamic) is not None


def system_draw(surface):
    _draw_arcade_burners_behind_ship(surface)
    for ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if _is_hud(ent):
            continue
        if esper.try_component(ent, CTagExplosion) is not None:
            continue
        anim = esper.try_component(ent, CAnimation)
        flip = False
        if esper.try_component(ent, CTagPlayer) is not None:
            arc = esper.try_component(ent, CArcadeDefenderFlight)
            if arc is not None and arc.facing < 0:
                flip = True
        ew = float(surf.area_w)
        alpha = None
        if esper.try_component(ent, CTagPlayer) is not None and game_state.player_occluded_by_terrain:
            alpha = int(game_state.get_rule("terrain_occlusion_alpha", 200))
        for sx in world_to_screen_x_positions(float(pos.x), ew):
            _blit_sprite(surface, sx, pos.y, surf, anim, flip_h=flip, alpha=alpha, world_scale=True)

    for ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if esper.try_component(ent, CTagExplosion) is None:
            continue
        anim = esper.try_component(ent, CAnimation)
        ew = float(surf.area_w)
        for sx in world_to_screen_x_positions(float(pos.x), ew):
            _blit_sprite(surface, sx, pos.y, surf, anim, world_scale=True)

    for ent, (pos, size, color) in esper.get_components(CPosition, CSize, CColor):
        if esper.try_component(ent, CSurface) is not None:
            continue
        if _is_hud(ent):
            continue
        sc = _sprite_draw_scale(world=True)
        ew = float(size.w)
        bw = max(1, int(round(float(size.w) * sc)))
        bh = max(1, int(round(float(size.h) * sc)))
        for sx in world_to_screen_x_positions(float(pos.x), ew):
            ox = int(round((bw - float(size.w)) * 0.5))
            oy = int(round((bh - float(size.h)) * 0.5))
            r = pygame.Rect(int(sx) - ox, int(pos.y) - oy, bw, bh)
            pygame.draw.rect(surface, (color.r, color.g, color.b), r)

    for ent, (pos, surf) in esper.get_components(CPosition, CSurface):
        if esper.try_component(ent, CTagHud) is None and esper.try_component(ent, CTagHudDynamic) is None:
            continue
        if esper.try_component(ent, CTagExplosion) is not None:
            continue
        anim = esper.try_component(ent, CAnimation)
        _blit_sprite(surface, pos.x, pos.y, surf, anim, world_scale=False)
