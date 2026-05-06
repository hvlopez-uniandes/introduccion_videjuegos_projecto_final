"""Todos los astronautas perdidos ⇒ planeta destruido · oleada espacio #0."""

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_enemy_spawner import CEnemySpawner, clone_spawn_events
from src.ecs.components.c_tags import CTagAstronaut
from src.engine.audio_util import play_sound


def system_defense_arcade_transition():
    if not game_state.defense_arcade_enabled or game_state.game_phase != "play":
        return
    if game_state.defense_phase != "surface":
        return
    if game_state.surface_astronauts_initial <= 0:
        return

    alive = sum(1 for _ in esper.get_component(CTagAstronaut))
    if alive > 0:
        return

    spawner = None
    for _, sp in esper.get_component(CEnemySpawner):
        spawner = sp
        break
    if spawner is None or not spawner.space_wave_templates:
        return

    game_state.defense_phase = "space"
    game_state.space_wave_index = 0
    game_state.scenario_space_skirmish = True
    game_state.planet_explosion_flash_remaining = float(
        game_state.get_rule("planet_explosion_flash_sec", 2.2)
    )
    game_state.reset_wave_survival_timers()

    first = clone_spawn_events(spawner.space_wave_templates[0])
    spawner.load_event_wave(first)
    try:
        play_sound("assets/snd/explosion.ogg", 0.78)
    except Exception:
        pass
