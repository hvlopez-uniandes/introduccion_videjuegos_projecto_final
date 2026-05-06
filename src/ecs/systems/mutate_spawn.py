"""Spawn mutant con sprite cohorte al completar ascenso rapto."""

import esper

from src.ecs.components.c_animation import AnimClip, CAnimation
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_missile_burst import CMissileBurst
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagMutant
from src.ecs.components.c_velocity import CVelocity
import src.engine.game_state as game_state
from src.engine.service_locator import ServiceLocator


def spawn_mutant_at(pos_x: float, pos_y: float) -> None:
    path = str(game_state.get_rule("mutant_image", "assets/img/enemy_mutant.png"))
    nf = int(game_state.get_rule("mutant_number_frames", 5))
    fps = float(game_state.get_rule("mutant_anim_framerate", 12))
    v_chase = float(game_state.get_rule("mutant_velocity_chase", 115))
    v_ret = float(game_state.get_rule("mutant_velocity_return", 70))
    ch = float(game_state.get_rule("mutant_distance_chase_start", 400))
    ret_d = float(game_state.get_rule("mutant_distance_return", 580))
    cd = float(game_state.get_rule("missile_cd_sec", 1.35))

    surf = ServiceLocator.current().get("textures").load(path)
    nf = max(1, nf)
    cs = CSurface(surf, nf)
    clips = {
        "IDLE": AnimClip("IDLE", 0, nf - 1, fps, loops=True),
    }
    e = esper.create_entity()
    esper.add_component(e, CPosition(float(pos_x), float(pos_y)))
    esper.add_component(e, CVelocity(0.0, 0.0))
    esper.add_component(e, cs)
    esper.add_component(e, CAnimation(nf, clips, initial="IDLE"))
    esper.add_component(e, CTagEnemy())
    esper.add_component(e, CTagMutant())
    esper.add_component(
        e,
        CHunterAI(
            float(pos_x),
            float(pos_y),
            ch,
            ret_d,
            v_chase,
            v_ret,
            sound_chase_path="",
        ),
    )
    esper.add_component(e, CMissileBurst(cd))
