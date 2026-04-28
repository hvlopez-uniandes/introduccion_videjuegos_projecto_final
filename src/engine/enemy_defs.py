"""Definiciones de tipos de enemigo (asteroide vs Hunter) cargadas desde enemies.json."""


class AsteroidEnemyDef:
    def __init__(self, image_path, velocity_min, velocity_max, sound_path=None):
        self.image_path = image_path
        self.velocity_min = float(velocity_min)
        self.velocity_max = float(velocity_max)
        self.sound_path = sound_path or ""


class HunterEnemyDef:
    def __init__(
        self,
        image_path,
        number_frames,
        clips_by_name,
        velocity_chase,
        velocity_return,
        distance_start_chase,
        distance_start_return,
        sound_path=None,
        sound_chase_path=None,
    ):
        self.image_path = image_path
        self.number_frames = int(number_frames)
        self.clips = clips_by_name
        self.velocity_chase = float(velocity_chase)
        self.velocity_return = float(velocity_return)
        self.distance_start_chase = float(distance_start_chase)
        self.distance_start_return = float(distance_start_return)
        self.sound_path = sound_path or ""
        self.sound_chase_path = sound_chase_path or ""
