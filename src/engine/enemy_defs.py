"""Definiciones de tipos de enemigo cargadas desde enemies.json."""


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


class LanderEnemyDef:
    """Lander tipo Defender: comportamiento cercano Hunter + disparo sólo cuando el jugador cruza vista."""

    def __init__(
        self,
        *,
        sprite_image_path,
        number_frames,
        clips_by_name,
        velocity_chase,
        velocity_return,
        distance_start_chase,
        distance_start_return,
        sound_path,
        sound_chase_path,
        shoot_interval_sec,
        bullet_velocity,
        bullet_width,
        bullet_height,
        bullet_r,
        bullet_g,
        bullet_b,
        rect_w=None,
        rect_h=None,
        rect_r=None,
        rect_g=None,
        rect_b=None,
        shoot_sound_path="",
        bullet_image_path="",
        bullet_num_frames=1,
    ):
        self.sprite_image_path = sprite_image_path
        self.number_frames = number_frames if number_frames else 1
        self.clips = clips_by_name if clips_by_name is not None else {}
        self.velocity_chase = float(velocity_chase)
        self.velocity_return = float(velocity_return)
        self.distance_start_chase = float(distance_start_chase)
        self.distance_start_return = float(distance_start_return)
        self.sound_path = sound_path or ""
        self.sound_chase_path = sound_chase_path or ""
        self.shoot_interval_sec = max(0.15, float(shoot_interval_sec))
        self.bullet_velocity = float(bullet_velocity)
        self.bullet_width = float(bullet_width)
        self.bullet_height = float(bullet_height)
        self.bullet_r = int(bullet_r)
        self.bullet_g = int(bullet_g)
        self.bullet_b = int(bullet_b)
        self.rect_w = float(rect_w) if rect_w is not None else None
        self.rect_h = float(rect_h) if rect_h is not None else None
        self.rect_r = int(rect_r) if rect_r is not None else None
        self.rect_g = int(rect_g) if rect_g is not None else None
        self.rect_b = int(rect_b) if rect_b is not None else None
        self.shoot_sound_path = shoot_sound_path or ""
        self.bullet_image_path = str(bullet_image_path) if bullet_image_path else ""
        self.bullet_num_frames = max(1, int(bullet_num_frames))

    def is_rect_sprite(self):
        return self.rect_w is not None


class ChaseMutantDef(HunterEnemyDef):
    """Mutante tipo caza (CHunterAI + misiles en motor)."""


class ChaseVariantDef(HunterEnemyDef):
    """Persecutor JSON con variante de tag: hunter | swarmer | baiter."""

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
        variant="hunter",
    ):
        super().__init__(
            image_path,
            number_frames,
            clips_by_name,
            velocity_chase,
            velocity_return,
            distance_start_chase,
            distance_start_return,
            sound_path=sound_path,
            sound_chase_path=sound_chase_path,
        )
        self.variant = str(variant)


class PodCargoDef:
    def __init__(
        self,
        image_path: str,
        number_frames: int,
        clips_by_name: dict,
        velocity_chase: float,
        velocity_return: float,
        distance_start_chase: float,
        distance_start_return: float,
        swarm_count: int,
        swarm_enemy_key: str,
        sound_path: str = "",
        sound_chase_path: str = "",
    ):
        self.image_path = str(image_path)
        self.number_frames = int(number_frames)
        self.clips = clips_by_name
        self.velocity_chase = float(velocity_chase)
        self.velocity_return = float(velocity_return)
        self.distance_start_chase = float(distance_start_chase)
        self.distance_start_return = float(distance_start_return)
        self.swarm_count = max(1, int(swarm_count))
        self.swarm_enemy_key = str(swarm_enemy_key)
        self.sound_path = sound_path or ""
        self.sound_chase_path = sound_chase_path or ""


class BomberDef:
    def __init__(
        self,
        image_path: str,
        number_frames: int,
        clips_by_name: dict,
        velocity_x: float,
        velocity_y: float,
        bomb_interval_sec: float,
        bomb_fall_speed: float,
        bomb_image_path: str = "",
        sound_path: str = "",
    ):
        self.image_path = str(image_path)
        self.number_frames = int(number_frames)
        self.clips = clips_by_name
        self.velocity_x = float(velocity_x)
        self.velocity_y = float(velocity_y)
        self.bomb_interval_sec = max(0.4, float(bomb_interval_sec))
        self.bomb_fall_speed = float(bomb_fall_speed)
        self.bomb_image_path = str(bomb_image_path).strip() or "assets/img/bomber_bomb.png"
        self.sound_path = sound_path or ""
