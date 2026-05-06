"""Componentes de escenario tipo Defender (estrellas + perfil planetario procedural)."""


class StarEntry:
    __slots__ = ("x", "y", "r", "g", "b", "phase", "blink_rad_s")

    def __init__(self, x, y, r, g, b, phase, blink_rad_s):
        self.x = float(x)
        self.y = float(y)
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.phase = float(phase)
        self.blink_rad_s = float(blink_rad_s)


class CScenarioStarfield:
    """Estrellas: parpadeo y scroll horizontal (parallax vía velocidad)."""

    __slots__ = ("stars", "scroll_x", "stars_scroll_px_s", "screen_w", "screen_h")

    def __init__(self, stars, scroll_x, stars_scroll_px_s, screen_w, screen_h):
        self.stars = stars
        self.scroll_x = float(scroll_x)
        self.stars_scroll_px_s = float(stars_scroll_px_s)
        self.screen_w = int(screen_w)
        self.screen_h = int(screen_h)


class CScenarioPlanetProfile:
    """Perfil inferior con alturas de borde períodicas sobre el ancho de pantalla."""

    __slots__ = (
        "offsets",
        "scroll_x",
        "planet_scroll_px_s",
        "baseline_y",
        "terrain_colors_rgb",
        "segments",
        "screen_w",
        "screen_h",
        "rng_seed",
    )

    def __init__(
        self,
        offsets,
        scroll_x,
        planet_scroll_px_s,
        baseline_y,
        terrain_colors_rgb,
        segments,
        screen_w,
        screen_h,
        rng_seed,
    ):
        self.offsets = offsets
        self.scroll_x = float(scroll_x)
        self.planet_scroll_px_s = float(planet_scroll_px_s)
        self.baseline_y = int(baseline_y)
        self.terrain_colors_rgb = terrain_colors_rgb
        self.segments = int(segments)
        self.screen_w = int(screen_w)
        self.screen_h = int(screen_h)
        self.rng_seed = int(rng_seed)


class CTagScenarioBackground:
    """Marca capas sólo-visual del escenario."""

    pass
