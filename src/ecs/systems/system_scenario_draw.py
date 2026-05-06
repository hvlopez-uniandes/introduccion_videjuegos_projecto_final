import math

import esper
import pygame

import src.engine.game_state as game_state

from src.ecs.components.c_scenario import CScenarioPlanetProfile, CScenarioStarfield
from src.engine.scenario_profile import planet_edge_screen_y


def system_scenario_background_draw(surface: pygame.Surface) -> None:
    for _, (sf,) in esper.get_components(CScenarioStarfield):
        w = max(1, sf.screen_w)
        base = sf.scroll_x % float(w)

        cam = float(getattr(game_state, "camera_scroll_x", None) or 0.0)
        for star in sf.stars:
            raw = star.x - base - cam
            while raw < -4:
                raw += float(w)
            while raw >= w + 8:
                raw -= float(w)

            blink = max(82, min(255, int(110 + 130 * math.sin(star.phase))))
            r = min(255, star.r * blink // 240)
            g = min(255, star.g * blink // 240)
            b = min(255, star.b * blink // 240)
            pygame.draw.circle(surface, (r, g, b), (int(raw), int(star.y)), 1)


def system_scenario_planet_draw(surface: pygame.Surface) -> None:
    rect = surface.get_rect()
    w = rect.width
    h = rect.height

    for _, (pl,) in esper.get_components(CScenarioPlanetProfile):
        if game_state.defense_arcade_enabled and game_state.scenario_space_skirmish:
            continue
        if len(pl.offsets) < 2:
            continue
        segs = pl.segments
        ridge_pts = []

        cam = float(getattr(game_state, "camera_scroll_x", None) or 0.0)
        for i in range(segs + 1):
            sx_screen = float(i) / float(segs) * float(w)
            wx = sx_screen + cam
            ridge_pts.append((int(sx_screen), int(planet_edge_screen_y(pl, wx))))

        for i in range(segs):
            c = pl.terrain_colors_rgb[i % len(pl.terrain_colors_rgb)]
            x0 = float(ridge_pts[i][0])
            y0 = float(ridge_pts[i][1])
            x1 = float(ridge_pts[i + 1][0])
            y1 = float(ridge_pts[i + 1][1])
            pygame.draw.polygon(
                surface,
                c,
                [(x0, y0), (x1, y1), (x1, float(h)), (x0, float(h))],
            )

        if len(ridge_pts) >= 2:
            pygame.draw.lines(
                surface,
                (220, 255, 255),
                False,
                ridge_pts,
                2,
            )


def system_scenario_draw(surface: pygame.Surface) -> None:
    system_scenario_background_draw(surface)
    system_scenario_planet_draw(surface)
