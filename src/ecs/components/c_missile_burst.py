"""Enfriamiento simple para misiles de mutantes."""


class CMissileBurst:
    def __init__(self, cooldown_sec=1.25):
        self.cooldown = max(0.05, float(cooldown_sec))
        self.timer = 0.0
