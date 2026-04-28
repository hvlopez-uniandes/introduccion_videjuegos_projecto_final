# Definición de la bala (semana 3: sprite + velocidad; legado: rectángulo).


class CBulletDef:
    def __init__(
        self,
        velocity,
        image_path=None,
        w=5,
        h=5,
        r=255,
        g=0,
        b=0,
        num_frames=1,
        sound_path=None,
    ):
        self.velocity = float(velocity)
        self.image_path = image_path
        self.num_frames = max(1, int(num_frames))
        self.w = float(w)
        self.h = float(h)
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.sound_path = sound_path or ""

    def is_sprite(self):
        return self.image_path is not None
