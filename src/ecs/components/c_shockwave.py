class CShockwave:
    """Onda expansiva visual que crece y desaparece."""
    def __init__(self, max_radius: float = 80.0, lifetime: float = 0.4,
                 r: int = 255, g: int = 140, b: int = 0):
        self.max_radius = max_radius
        self.lifetime = lifetime
        self.elapsed = 0.0
        self.r = r
        self.g = g
        self.b = b