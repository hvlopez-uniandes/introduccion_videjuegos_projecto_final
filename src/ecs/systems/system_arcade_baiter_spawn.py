"""Baiter (FAQ): aparece si la oleada lleva demasiado tiempo sin limpiarse."""

import random

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_ai import CHunterAI
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBaiter, CTagEnemy
from src.ecs.components.c_velocity import CVelocity
from src.engine.enemy_defs import ChaseVariantDef
from src.engine.service_locator import ServiceLocator


def system_arcade_baiter_spawn():
    if not game_state.defense_arcade_enabled or game_state.paused:
        return
    if game_state.game_phase != "play":
        return
    if game_state.defense_phase != "space":
        return
    delay = float(game_state.get_rule("baiter_spawn_after_wave_sec", 24))
    key = str(game_state.get_rule("baiter_enemy_key", "baiter_ufo"))

    if game_state.wave_survival_sec < delay:
        return
    if game_state.baiter_spawned_this_wave:
        return
    if sum(1 for _, __ in esper.get_components(CPosition, CTagBaiter)) > 0:
        return

    tipo = None
    for _, sp in esper.get_component(CEnemySpawner):
        tipo = sp.enemy_types.get(key)
        break
    if tipo is None or not isinstance(tipo, ChaseVariantDef) or tipo.variant != "baiter":
        return

    cam = float(getattr(game_state, "camera_scroll_x", None) or 0.0)
    sw = float(game_state.world_screen_w or 320)
    wx = cam + random.uniform(24.0, max(48.0, sw - 40.0))
    y = 18.0

    surf = ServiceLocator.current().get("textures").load(tipo.image_path)
    cs = CSurface(surf, tipo.number_frames)
    anim = CAnimation(tipo.number_frames, tipo.clips, initial="IDLE")
    e = esper.create_entity()
    esper.add_component(e, CPosition(float(wx), float(y)))
    esper.add_component(e, CVelocity(0.0, 0.0))
    esper.add_component(e, cs)
    esper.add_component(e, anim)
    esper.add_component(e, CTagEnemy())
    esper.add_component(e, CTagBaiter())
    esper.add_component(
        e,
        CHunterAI(
            float(x),
            float(y),
            tipo.distance_start_chase,
            tipo.distance_start_return,
            tipo.velocity_chase,
            tipo.velocity_return,
            tipo.sound_chase_path,
        ),
    )
    game_state.baiter_spawned_this_wave = True
