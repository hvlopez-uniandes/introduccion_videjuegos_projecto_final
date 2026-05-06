import math
import random

import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_missile_burst import CMissileBurst
from src.ecs.components.c_color import CColor
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_lander_ai import CLanderAI
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_pod_cargo import CPodCargo
from src.ecs.components.c_bomber_drop import CBomberDrop
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import (
    CTagAsteroid,
    CTagBomber,
    CTagEnemy,
    CTagHunter,
    CTagLander,
    CTagMutant,
    CTagPod,
    CTagSwarmer,
    CTagBaiter,
)
from src.ecs.components.c_velocity import CVelocity
import src.engine.game_state as game_state
from src.engine.enemy_defs import (
    AsteroidEnemyDef,
    BomberDef,
    ChaseMutantDef,
    ChaseVariantDef,
    HunterEnemyDef,
    LanderEnemyDef,
    PodCargoDef,
)
import src.engine.paths as engine_paths
from src.engine.audio_util import play_sound
from src.engine.service_locator import ServiceLocator


def system_enemy_spawner(delta_time):
    for _, spawner in esper.get_component(CEnemySpawner):
        spawner.accumulated_time = spawner.accumulated_time + delta_time

        for ev in spawner.events:
            if ev.fired:
                continue
            if spawner.accumulated_time < ev.time_sec:
                continue

            tipo = spawner.enemy_types.get(ev.enemy_type)
            if tipo is None:
                ev.fired = True
                continue

            root = engine_paths.PROJECT_ROOT
            if root is None:
                ev.fired = True
                continue

            if isinstance(tipo, AsteroidEnemyDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, 1)
                speed = random.uniform(tipo.velocity_min, tipo.velocity_max)
                angle = random.uniform(0, 2 * math.pi)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(vx, vy))
                esper.add_component(e, cs)
                esper.add_component(e, CTagEnemy())
                esper.add_component(e, CTagAsteroid())
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.5)

            elif isinstance(tipo, LanderEnemyDef):
                rz = esper.create_entity()
                esper.add_component(rz, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(rz, CVelocity(0.0, 0.0))
                if tipo.is_rect_sprite():
                    esper.add_component(rz, CSize(float(tipo.rect_w), float(tipo.rect_h)))
                    esper.add_component(
                        rz,
                        CColor(int(tipo.rect_r), int(tipo.rect_g), int(tipo.rect_b)),
                    )
                else:
                    surf = ServiceLocator.current().get("textures").load(tipo.sprite_image_path)
                    cs = CSurface(surf, tipo.number_frames)
                    anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                    esper.add_component(rz, cs)
                    esper.add_component(rz, anim)
                esper.add_component(rz, CTagEnemy())
                esper.add_component(rz, CTagLander())
                esper.add_component(
                    rz,
                    CLanderAI(
                        ev.pos_x,
                        ev.pos_y,
                        tipo.distance_start_chase,
                        tipo.distance_start_return,
                        tipo.velocity_chase,
                        tipo.velocity_return,
                        tipo.shoot_interval_sec,
                        tipo.bullet_velocity,
                        tipo.bullet_width,
                        tipo.bullet_height,
                        tipo.bullet_r,
                        tipo.bullet_g,
                        tipo.bullet_b,
                        sound_chase_path=tipo.sound_chase_path,
                        shoot_sound_path=tipo.shoot_sound_path,
                        bullet_image_path=tipo.bullet_image_path,
                        bullet_num_frames=tipo.bullet_num_frames,
                    ),
                )
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.42)
                r = getattr(game_state, "rules_cache", {}) or {}
                land_ai = esper.try_component(rz, CLanderAI)
                if land_ai is not None:
                    land_ai.approach_speed = float(r.get("lander_approach_speed", land_ai.approach_speed))
                    land_ai.ascend_speed = float(r.get("lander_ascend_speed", land_ai.ascend_speed))
                    land_ai.mutate_screen_y_px = float(r.get("lander_mutate_y_px", land_ai.mutate_screen_y_px))

            elif isinstance(tipo, PodCargoDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, tipo.number_frames)
                anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(0.0, 0.0))
                esper.add_component(e, cs)
                esper.add_component(e, anim)
                esper.add_component(e, CTagEnemy())
                esper.add_component(e, CTagPod())
                esper.add_component(
                    e,
                    CHunterAI(
                        ev.pos_x,
                        ev.pos_y,
                        tipo.distance_start_chase,
                        tipo.distance_start_return,
                        tipo.velocity_chase,
                        tipo.velocity_return,
                        tipo.sound_chase_path,
                    ),
                )
                esper.add_component(e, CPodCargo(tipo.swarm_enemy_key, tipo.swarm_count))
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.42)

            elif isinstance(tipo, BomberDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, tipo.number_frames)
                anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(tipo.velocity_x, tipo.velocity_y))
                esper.add_component(e, cs)
                esper.add_component(e, anim)
                esper.add_component(e, CTagEnemy())
                esper.add_component(e, CTagBomber())
                esper.add_component(
                    e,
                    CBomberDrop(tipo.bomb_interval_sec, tipo.bomb_fall_speed),
                )
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.42)

            elif isinstance(tipo, ChaseMutantDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, tipo.number_frames)
                anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(0.0, 0.0))
                esper.add_component(e, cs)
                esper.add_component(e, anim)
                esper.add_component(e, CTagEnemy())
                esper.add_component(e, CTagMutant())
                esper.add_component(
                    e,
                    CHunterAI(
                        ev.pos_x,
                        ev.pos_y,
                        tipo.distance_start_chase,
                        tipo.distance_start_return,
                        tipo.velocity_chase,
                        tipo.velocity_return,
                        tipo.sound_chase_path,
                    ),
                )
                cd = float(game_state.get_rule("missile_cd_sec", 1.35))
                esper.add_component(e, CMissileBurst(cd))
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.45)

            elif isinstance(tipo, ChaseVariantDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, tipo.number_frames)
                anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(0.0, 0.0))
                esper.add_component(e, cs)
                esper.add_component(e, anim)
                esper.add_component(e, CTagEnemy())
                tag = tipo.variant.lower()
                if tag == "baiter":
                    esper.add_component(e, CTagBaiter())
                else:
                    esper.add_component(e, CTagSwarmer())
                esper.add_component(
                    e,
                    CHunterAI(
                        ev.pos_x,
                        ev.pos_y,
                        tipo.distance_start_chase,
                        tipo.distance_start_return,
                        tipo.velocity_chase,
                        tipo.velocity_return,
                        tipo.sound_chase_path,
                    ),
                )
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.45)

            elif isinstance(tipo, HunterEnemyDef):
                surf = ServiceLocator.current().get("textures").load(tipo.image_path)
                cs = CSurface(surf, tipo.number_frames)
                anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
                e = esper.create_entity()
                esper.add_component(e, CPosition(ev.pos_x, ev.pos_y))
                esper.add_component(e, CVelocity(0.0, 0.0))
                esper.add_component(e, cs)
                esper.add_component(e, anim)
                esper.add_component(e, CTagEnemy())
                esper.add_component(e, CTagHunter())
                esper.add_component(
                    e,
                    CHunterAI(
                        ev.pos_x,
                        ev.pos_y,
                        tipo.distance_start_chase,
                        tipo.distance_start_return,
                        tipo.velocity_chase,
                        tipo.velocity_return,
                        tipo.sound_chase_path,
                    ),
                )
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.45)

            ev.fired = True
