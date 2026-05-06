"""Minirradar arcade: puntos por enemigos en una franja inferior."""

import pygame

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import (
    CTagBaiter,
    CTagBomb,
    CTagBomber,
    CTagEnemy,
    CTagHunter,
    CTagLander,
    CTagMutant,
    CTagPlayer,
    CTagPod,
    CTagSwarmer,
)


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return s.area_w, s.area_h
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 8.0, 8.0


def _enemy_color(ent: int):
    if esper.try_component(ent, CTagBomb) is not None:
        return 255, 160, 64
    if esper.try_component(ent, CTagPod) is not None:
        return 255, 0, 255
    if esper.try_component(ent, CTagSwarmer) is not None:
        return 255, 140, 200
    if esper.try_component(ent, CTagBaiter) is not None:
        return 0, 240, 255
    if esper.try_component(ent, CTagBomber) is not None:
        return 200, 120, 255
    if esper.try_component(ent, CTagLander) is not None:
        return 80, 255, 140
    if esper.try_component(ent, CTagMutant) is not None:
        return 255, 80, 90
    if esper.try_component(ent, CTagHunter) is not None:
        return 255, 220, 80
    return 200, 200, 255


def system_draw_radar_defender(surface: pygame.Surface) -> None:
    if not game_state.arcade_defender_flight:
        return
    w, h = surface.get_size()
    band_h = 14
    y0 = h - band_h - 2
    pygame.draw.rect(surface, (24, 32, 48), pygame.Rect(0, y0, w, band_h))
    pygame.draw.rect(surface, (90, 120, 170), pygame.Rect(0, y0, w, band_h), 1)

    try:
        rs = float(game_state.get_rule("radar_blip_scale", 2.0))
    except (TypeError, ValueError):
        rs = 2.0
    rs = max(1.0, min(4.0, rs))
    blip_w = max(2, min(10, int(round(2.0 * rs))))
    blip_h_en = max(3, min(band_h - 4, int(round(float(band_h - 6) * min(1.35, 0.5 + rs * 0.45)))))
    blip_h_pl = max(3, min(band_h - 6, int(round(float(band_h - 8) * min(1.2, 0.55 + rs * 0.4)))))

    ww = max(1.0, float(game_state.world_wrap_w or w))

    for ent, comps in esper.get_components(CPosition, CTagPlayer):
        pos = comps[0]
        pw, _ph = _dims(ent)
        px = ((pos.x + pw * 0.5) % ww) / ww * float(w - 4) + 2.0
        ix = int(px) - blip_w // 2 + 1
        py_r = y0 + 4 + max(0, (band_h - 8 - blip_h_pl) // 2)
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(ix, py_r, blip_w, blip_h_pl))
        break

    for ent, comps in esper.get_components(CPosition, CTagEnemy):
        pos = comps[0]
        ew, _eh = _dims(ent)
        ex = ((pos.x + ew * 0.5) % ww) / ww * float(w - 4) + 2.0
        col = _enemy_color(ent)
        ix = int(ex) - blip_w // 2 + 1
        ey_r = y0 + 3 + max(0, (band_h - 6 - blip_h_en) // 2)
        pygame.draw.rect(surface, col, pygame.Rect(ix, ey_r, blip_w, blip_h_en))
