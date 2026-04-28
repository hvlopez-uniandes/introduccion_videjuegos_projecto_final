class CSurface:
    """Textura y área de colisión/dibujo (un fotograma = tira horizontal / number_frames)."""

    def __init__(self, surface, number_frames=1):
        self.surface = surface
        self.num_frames = max(1, int(number_frames))
        w = surface.get_width()
        h = surface.get_height()
        self.frame_w = max(1, w // self.num_frames)
        self.frame_h = h
        self.area_w = float(self.frame_w)
        self.area_h = float(self.frame_h)

    @classmethod
    def from_text(cls, font, text: str, color_rgb, antialias: bool = False):
        surf = font.render(text, antialias, color_rgb)
        return cls(surf, 1)

    def update_from_text(self, font, text: str, color_rgb, antialias: bool = False) -> bool:
        """Regenera la superficie si cambió el texto. Devuelve True si hubo cambio."""
        if getattr(self, "_last_text", None) == text:
            return False
        self._last_text = text
        self.surface = font.render(text, antialias, color_rgb)
        w = self.surface.get_width()
        h = self.surface.get_height()
        self.num_frames = 1
        self.frame_w = max(1, w)
        self.frame_h = h
        self.area_w = float(self.frame_w)
        self.area_h = float(self.frame_h)
        return True
