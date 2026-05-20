class CBoss:
    """Estado y configuración del boss."""

    IDLE        = "IDLE"
    CHARGING    = "CHARGING"
    AIMING      = "AIMING"
    FIRING      = "FIRING"
    TELEPORTING = "TELEPORTING"

    def __init__(self, cfg: dict):
        self.health              = int(cfg["health"])
        self.teleport_interval   = float(cfg["teleport_interval_sec"])
        self.ray_charge_sec      = float(cfg["ray_charge_sec"])
        self.ray_rotate_speed    = float(cfg["ray_rotate_speed_deg_s"])
        self.ray_duration_sec    = float(cfg["ray_duration_sec"])
        self.sound_teleport      = str(cfg.get("sound_teleport", ""))
        self.sound_ray           = str(cfg.get("sound_ray", ""))
        self.sound_charge = str(cfg.get("sound_charge", ""))
        self._charge_sound_channel = None
        self._ray_sound_channel = None
        self.aim_duration_sec = float(cfg.get("aim_duration_sec", 1.0))

        self.state               = CBoss.IDLE
        self.state_timer         = 0.0   # tiempo en el estado actual
        self.ray_angle           = 0.0   # ángulo actual del rayo en grados
        self.ray_entity          = None  # entidad del rayo activo