import math
import random

import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagHunter
from src.ecs.components.c_velocity import CVelocity
from src.engine.enemy_defs import AsteroidEnemyDef, HunterEnemyDef
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
                if tipo.sound_path:
                    play_sound(tipo.sound_path, 0.5)

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
