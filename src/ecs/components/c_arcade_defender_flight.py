"""Vuelo tipo arcade Defender: thrust/reverse horizontal + eje vertical aparte."""


class CArcadeDefenderFlight:
    def __init__(
        self,
        facing: int = 1,
        thrust_accel_px_s2: float = 420.0,
        drag_per_s: float = 0.72,
        max_speed_x: float = 220.0,
        vertical_speed_px_s: float = 150.0,
    ):
        self.facing = 1 if int(facing) >= 0 else -1
        self.thrust_accel_px_s2 = float(thrust_accel_px_s2)
        self.drag_per_s = float(drag_per_s)
        self.max_speed_x = float(max_speed_x)
        self.vertical_speed_px_s = float(vertical_speed_px_s)
