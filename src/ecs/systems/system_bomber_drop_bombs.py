import esper

import src.engine.game_state as game_state

from src.ecs.components.c_animation import AnimClip, CAnimation
from src.ecs.components.c_bomber_drop import CBomberDrop
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBomb, CTagBomber, CTagEnemy
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator


def system_bomber_drop_bombs(delta_time: float) -> None:
    if game_state.paused or game_state.game_phase != "play":
        return
    if delta_time <= 0.0:
        return

    bomb_path = str(game_state.get_rule("bomber_bomb_image", "assets/img/bomber_bomb.png"))
    bf = max(1, int(game_state.get_rule("bomber_bomb_num_frames", 5)))
    bfps = float(game_state.get_rule("bomber_bomb_anim_framerate", 14.0))

    for ent, (pos, drop, _) in esper.get_components(CPosition, CBomberDrop, CTagBomber):
        surf = esper.try_component(ent, CSurface)
        if surf is None:
            continue
        drop.cooldown_remaining -= float(delta_time)
        if drop.cooldown_remaining > 0.0:
            continue
        drop.cooldown_remaining = drop.bomb_interval_sec

        bx = pos.x + surf.area_w * 0.5
        by = pos.y + surf.area_h * 0.88
        img = ServiceLocator.current().get("textures").load(bomb_path)
        csurf = CSurface(img, bf)
        bx0 = float(bx - float(csurf.area_w) * 0.5)
        by0 = float(by)
        bs = esper.create_entity()
        esper.add_component(bs, CPosition(bx0, by0))
        esper.add_component(bs, CVelocity(0.0, float(drop.bomb_fall_speed)))
        esper.add_component(bs, csurf)
        end_f = max(0, bf - 1)
        anim = CAnimation(
            bf,
            {"IDLE": AnimClip("IDLE", 0, end_f, max(1.0, bfps), loops=True)},
            initial="IDLE",
        )
        esper.add_component(bs, anim)
        esper.add_component(bs, CTagEnemy())
        esper.add_component(bs, CTagBomb())
