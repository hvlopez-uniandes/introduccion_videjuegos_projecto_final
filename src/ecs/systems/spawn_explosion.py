import esper

from src.ecs.components.c_animation import AnimClip, CAnimation
from src.ecs.components.c_explosion_config import CExplosionConfig
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagExplosion
import src.engine.paths as engine_paths
from src.engine.audio_util import play_sound
from src.engine.service_locator import ServiceLocator


def spawn_explosion(center_x, center_y, play_spawn_sound=True):
    root = engine_paths.PROJECT_ROOT
    if root is None:
        return
    cfg = None
    for _, c in esper.get_component(CExplosionConfig):
        cfg = c
        break
    if cfg is None:
        return

    surf = ServiceLocator.current().get("textures").load(cfg.image_path)
    cs = CSurface(surf, cfg.number_frames)
    ex = center_x - cs.area_w / 2.0
    ey = center_y - cs.area_h / 2.0
    anim = CAnimation(cfg.number_frames, cfg.clips, initial="EXPLODE")
    e = esper.create_entity()
    esper.add_component(e, CPosition(ex, ey))
    esper.add_component(e, cs)
    esper.add_component(e, anim)
    esper.add_component(e, CTagExplosion())
    if play_spawn_sound and cfg.sound_path:
        play_sound(cfg.sound_path, 0.55)
