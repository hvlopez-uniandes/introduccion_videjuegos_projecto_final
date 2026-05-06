"""Construye entidades ECS del escenario desde `world.json`."""

import esper

from src.ecs.components.c_scenario import (
    CScenarioPlanetProfile,
    CScenarioStarfield,
    CTagScenarioBackground,
    StarEntry,
)
from src.engine.config import LoadedWorldCfg


def build_periodic_offsets(n: int, rng) -> list[float]:
    """Perfil períodico cerrado sobre n muestras (ruido dominado ~Defender-ish)."""
    if n < 8:
        n = 8
    raw = []
    t = rng.uniform(-4.5, 4.5)
    for _ in range(n):
        t += rng.uniform(-3.2, 3.2)
        t = max(-22.0, min(24.0, t))
        raw.append(t)

    for _iteration in range(3):
        nxt = []
        for i in range(n):
            a = raw[(i - 1) % n]
            b = raw[i]
            c = raw[(i + 1) % n]
            nxt.append(0.5 * b + 0.25 * a + 0.25 * c)
        raw = nxt
    avg = (raw[0] + raw[-1]) / 2.0
    raw[0] = raw[-1] = avg
    return raw


def create_scenario_entities(rng, world: LoadedWorldCfg, screen_w: int, screen_h: int):
    stars = []
    if world.stars_number > 0 and world.star_colors:
        sky_bottom = screen_h * 0.74
        for _ in range(world.stars_number):
            rc, gc, bc = rng.choice(world.star_colors)
            period_sec = rng.uniform(world.stars_blink_min_sec, world.stars_blink_max_sec)
            period_sec = max(1e-2, period_sec)
            rad_s = 2.0 * 3.1415926535 / period_sec * 2.15
            stars.append(
                StarEntry(
                    rng.uniform(0, float(screen_w)),
                    rng.uniform(2.0, max(42.0, sky_bottom)),
                    rc,
                    gc,
                    bc,
                    rng.uniform(0, 2.0 * 3.1415926535),
                    rad_s,
                )
            )

    stars_v = float(world.ambient_scroll_px_s) * float(world.stars_parallax_factor)
    planet_v = float(world.ambient_scroll_px_s) * float(world.planet_parallax_factor)
    baseline_y = screen_h - int(world.planet_baseline_from_bottom_px)

    offsets = build_periodic_offsets(int(world.planet_line_points), rng)
    seed_repr = rng.randint(1, (1 << 30) - 1)

    e_stars = esper.create_entity()
    esper.add_component(
        e_stars,
        CScenarioStarfield(stars, 0.0, stars_v, screen_w, screen_h),
    )
    esper.add_component(e_stars, CTagScenarioBackground())

    e_plan = esper.create_entity()
    esper.add_component(
        e_plan,
        CScenarioPlanetProfile(
            offsets,
            0.0,
            planet_v,
            baseline_y,
            world.planet_colors,
            len(offsets),
            screen_w,
            screen_h,
            seed_repr,
        ),
    )
    esper.add_component(e_plan, CTagScenarioBackground())
