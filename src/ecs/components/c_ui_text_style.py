class CUiTextStyle:
    """Estilo para regenerar texto dinámico (HUD)."""

    def __init__(self, font_path: str, size_px: int, r: int, g: int, b: int, antialias: bool = False):
        self.font_path = str(font_path)
        self.size_px = int(size_px)
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.antialias = bool(antialias)
        self._last_rendered = ""
