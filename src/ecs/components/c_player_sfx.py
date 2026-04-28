class CPlayerSfx:
    """Rutas de sonido del jugador (movimiento y colisión)."""

    def __init__(self, move_sound_path, collision_sound_path):
        self.move_sound_path = move_sound_path or ""
        self.collision_sound_path = collision_sound_path or ""
        self._last_move_sound_ms = 0

    def mark_move_sound(self, now_ms: int, min_interval_ms: int) -> bool:
        if now_ms - self._last_move_sound_ms >= min_interval_ms:
            self._last_move_sound_ms = now_ms
            return True
        return False
