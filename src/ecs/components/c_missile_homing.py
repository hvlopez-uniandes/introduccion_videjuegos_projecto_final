class CMissileHoming:
    """Misil de rastreo con daño en área al impactar."""

    def __init__(self, speed: float = 350.0, blast_radius: float = 80.0):
        self.speed = speed
        self.blast_radius = blast_radius
        self.target_ent = None  # entidad objetivo actual