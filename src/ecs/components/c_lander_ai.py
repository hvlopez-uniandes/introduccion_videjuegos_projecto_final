"""Lander Defender: igual base que Hunter + temporizador de disparo cuando el jugador está en vista."""


class CLanderAI:
    def __init__(
        self,
        origin_x,
        origin_y,
        chase_dist,
        return_dist,
        v_chase,
        v_return,
        shoot_interval_sec,
        bullet_velocity,
        bullet_w,
        bullet_h,
        bullet_r,
        bullet_g,
        bullet_b,
        sound_chase_path="",
        shoot_sound_path="",
        bullet_image_path="",
        bullet_num_frames=1,
    ):
        self.origin_x = float(origin_x)
        self.origin_y = float(origin_y)
        self.chase_dist = float(chase_dist)
        self.return_dist = float(return_dist)
        self.v_chase = float(v_chase)
        self.v_return = float(v_return)
        self.state = "idle"
        self.sound_chase_path = sound_chase_path or ""
        self.shoot_sound_path = shoot_sound_path or ""
        self.shoot_interval_sec = float(shoot_interval_sec)
        self.shoot_cd = shoot_interval_sec * 0.4
        self.bullet_velocity = float(bullet_velocity)
        self.bullet_w = float(bullet_w)
        self.bullet_h = float(bullet_h)
        self.bullet_r = int(bullet_r)
        self.bullet_g = int(bullet_g)
        self.bullet_b = int(bullet_b)
        self.bullet_image_path = str(bullet_image_path) if bullet_image_path else ""
        self.bullet_num_frames = max(1, int(bullet_num_frames))
        self.capture_phase = "idle"
        self.capture_target_astronaut = -1
        self.carried_astronaut_entity = -1
        self.approach_speed = 52.0
        self.ascend_speed = 60.0
        self.capture_h_radius_px = 96.0
        self.mutate_screen_y_px = 16.0
