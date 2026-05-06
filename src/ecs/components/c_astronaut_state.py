"""Modos de ciclo Defender: suelo · rapto Lander · caída · transporte por nave."""


class CAstronautState:
    GROUND = "ground"
    LANDER_CARRY = "lander_carry"
    FALLING = "falling"
    SHIP_CARRY = "ship_carry"

    def __init__(self, mode="ground", carrier_ent: int = -1):
        self.mode = mode
        self.carrier_ent = int(carrier_ent)
