"""Datos de explosión cargados desde explosion.json (en la entidad de configuración)."""


class CExplosionConfig:
    def __init__(self, image_path, number_frames, clips_by_name, sound_path=None):
        self.image_path = image_path
        self.number_frames = number_frames
        self.clips = clips_by_name
        self.sound_path = sound_path or ""
