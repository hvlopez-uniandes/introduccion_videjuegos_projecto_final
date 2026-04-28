class AnimClip:
    def __init__(self, name, start, end, framerate, loops=True):
        self.name = name
        self.start = int(start)
        self.end = int(end)
        self.framerate = max(0.001, float(framerate))
        self.loops = loops


class CAnimation:
    """Control de animación: fotograma actual y clip activo."""

    def __init__(self, number_frames, clips_by_name, initial="IDLE"):
        self.number_frames = max(1, int(number_frames))
        self.clips = clips_by_name
        self.current_name = initial if initial in clips_by_name else next(iter(clips_by_name))
        self.current_frame = self.clips[self.current_name].start
        self.subframe_accum = 0.0
        self.finished = False

    def set_clip(self, name):
        if name not in self.clips:
            return
        self.current_name = name
        c = self.clips[name]
        self.current_frame = c.start
        self.subframe_accum = 0.0
        self.finished = False
