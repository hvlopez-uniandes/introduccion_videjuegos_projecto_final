class CParticle:
    """Partícula visual temporal."""
    def __init__(self, lifetime: float, vx: float, vy: float,
                 r: int, g: int, b: int, size: float = 2.0):
        self.lifetime = lifetime      # tiempo total de vida
        self.elapsed = 0.0            # tiempo transcurrido
        self.vx = vx
        self.vy = vy
        self.r = r
        self.g = g
        self.b = b
        self.size = size