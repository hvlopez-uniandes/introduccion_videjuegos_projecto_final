"""Propulsión visual arcade (tira detrás del sprite del jugador)."""

from src.ecs.components.c_surface import CSurface


class CPlayerArcadeBurner:
    def __init__(
        self,
        idle_surf: CSurface,
        moving_surf: CSurface,
        anim_hz: float = 12.0,
        tuck_px: float = 3.0,
    ):
        self.idle = idle_surf
        self.moving = moving_surf
        self.anim_hz = max(4.0, float(anim_hz))
        self.tuck_px = max(0.0, float(tuck_px))
        self.boost = False
        self.anim_t = 0.0

    def active_sheet(self) -> CSurface:
        return self.moving if self.boost else self.idle
