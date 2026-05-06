"""Astronauta en superficie Defender (solo sombra posición ECS)."""


class CAstronautFootprint:
    def __init__(self, clearance_px_above_terrain_line=6.0, wobble_amplitude_px=3.5, wobble_hz=0.7):
        self.clearance_px_above_terrain_line = float(clearance_px_above_terrain_line)
        self.wobble_amplitude_px = float(wobble_amplitude_px)
        self.wobble_hz = float(wobble_hz)
        self.phase = 0.0
