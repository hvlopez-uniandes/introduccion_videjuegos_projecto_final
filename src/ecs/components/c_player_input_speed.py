class CPlayerInputSpeed:
    """Velocidad en píxeles por segundo para las flechas (input_velocity del player.json)."""

    def __init__(self, pixels_per_second, smoothing_hz=20.0):
        self.pixels_per_second = float(pixels_per_second)
        self.smoothing_hz = max(2.0, float(smoothing_hz))
