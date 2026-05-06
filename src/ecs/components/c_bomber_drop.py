class CBomberDrop:
    def __init__(self, bomb_interval_sec: float, bomb_fall_speed: float):
        self.bomb_interval_sec = max(0.35, float(bomb_interval_sec))
        self.bomb_fall_speed = max(40.0, float(bomb_fall_speed))
        self.cooldown_remaining = float(self.bomb_interval_sec)
