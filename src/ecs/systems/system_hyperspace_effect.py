import math
import random
import esper
import pygame

import src.engine.game_state as game_state
from src.ecs.components.c_particle import CParticle
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_size import CSize
from src.ecs.components.c_tags import CTagPlayer
from src.engine.frame_input import consume_hyperspace


def _spawn_hyperspace_particles(px, py, pw, ph):
    cx = px + pw / 2.0
    cy = py + ph / 2.0
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(40.0, 120.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        ox = random.uniform(-pw / 2.0, pw / 2.0)
        oy = random.uniform(-ph / 2.0, ph / 2.0)
        r = random.choice([80, 120, 180, 220])
        g = random.choice([160, 200, 240])
        b = 255
        size = random.uniform(1.5, 3.5)
        lifetime = random.uniform(0.3, 0.7)
        ent = esper.create_entity()
        esper.add_component(ent, CPosition(cx + ox, cy + oy))
        esper.add_component(ent, CParticle(lifetime, vx, vy, r, g, b, size))


def system_hyperspace_effect(delta_time: float):
    if game_state.paused:
        return

    # Actualizar y eliminar partículas muertas
    for ent, (pos, part) in esper.get_components(CPosition, CParticle):
        part.elapsed += delta_time
        pos.x += part.vx * delta_time
        pos.y += part.vy * delta_time
        # Desacelerar gradualmente
        part.vx *= 0.92
        part.vy *= 0.92
        if part.elapsed >= part.lifetime:
            try:
                esper.delete_entity(ent, immediate=True)
            except KeyError:
                pass