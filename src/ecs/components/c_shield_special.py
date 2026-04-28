class CShieldSpecial:
    """Habilidad temporal: pulso que elimina enemigos cercanos; requiere recarga."""

    def __init__(
        self,
        duration_sec: float,
        cooldown_sec: float,
        radius_px: float,
        activation_key: int,
    ):
        self.duration_sec = float(duration_sec)
        self.cooldown_sec = float(cooldown_sec)
        self.radius_px = float(radius_px)
        self.activation_key = int(activation_key)
        self.active_remaining = 0.0
        self.cooldown_remaining = 0.0
