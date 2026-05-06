"""Genera swarmers al romper una cápsula Pod."""

import math

import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_pod_cargo import CPodCargo
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagSwarmer
from src.ecs.components.c_velocity import CVelocity
from src.engine.enemy_defs import ChaseVariantDef
from src.engine.service_locator import ServiceLocator


def spawn_swarmers_from_pod_cargo(center_x: float, center_y: float, cargo: CPodCargo) -> None:
    types = None
    for _, sp in esper.get_component(CEnemySpawner):
        types = sp.enemy_types
        break
    if types is None:
        return
    tipo = types.get(cargo.swarm_enemy_key)
    if tipo is None or not isinstance(tipo, ChaseVariantDef) or tipo.variant != "swarmer":
        return
    n = int(cargo.swarm_count)
    for i in range(n):
        ang = 2 * math.pi * (i / max(1.0, float(n)))
        ox = math.cos(ang) * 34.0
        oy = math.sin(ang) * 22.0
        px = float(center_x) + ox
        py = float(center_y) + oy
        surf = ServiceLocator.current().get("textures").load(tipo.image_path)
        cs = CSurface(surf, tipo.number_frames)
        anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
        e = esper.create_entity()
        esper.add_component(e, CPosition(px, py))
        esper.add_component(e, CVelocity(0.0, 0.0))
        esper.add_component(e, cs)
        esper.add_component(e, anim)
        esper.add_component(e, CTagEnemy())
        esper.add_component(e, CTagSwarmer())
        esper.add_component(
            e,
            CHunterAI(
                px,
                py,
                tipo.distance_start_chase,
                tipo.distance_start_return,
                tipo.velocity_chase,
                tipo.velocity_return,
                tipo.sound_chase_path,
            ),
        )
