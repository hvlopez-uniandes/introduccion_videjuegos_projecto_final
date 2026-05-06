"""Progresión de oleada · victoria · fases superficie/espacio (Defender arcade)."""

import esper

from src.ecs.components.c_enemy_spawner import CEnemySpawner, clone_spawn_events
from src.ecs.components.c_tags import CTagAstronaut, CTagEnemy
import src.engine.game_state as game_state
from src.engine.config import repopulate_surface_astronauts


def _restore_planet_phase(spawner: CEnemySpawner) -> None:
    tpl = clone_spawn_events(spawner.surface_template)
    spawner.load_event_wave(tpl)
    cfg = game_state.play_cfg_dir
    if cfg is not None:
        n = repopulate_surface_astronauts(cfg, game_state.play_screen_h_int)
        game_state.surface_astronauts_initial = n
    else:
        game_state.surface_astronauts_initial = 0

    game_state.defense_phase = "surface"
    game_state.space_wave_index = 0
    game_state.scenario_space_skirmish = False
    game_state.reset_wave_survival_timers()
    bb = int(game_state.get_rule("restore_surface_score_bonus", 1500))
    game_state.add_score(max(0, bb))


def system_level_progress():
    if game_state.game_phase != "play" or game_state.level_victorious:
        return
    spawner = None
    for _, sp in esper.get_component(CEnemySpawner):
        spawner = sp
        break
    if spawner is None:
        return
    if not spawner.events:
        return
    if not all(ev.fired for ev in spawner.events):
        return
    n_enemies = sum(1 for _ in esper.get_component(CTagEnemy))
    if n_enemies > 0:
        return

    humans = sum(1 for _ in esper.get_component(CTagAstronaut))
    per = int(game_state.get_rule("wave_bonus_per_human_alive", 100))

    if not game_state.defense_arcade_enabled:
        if humans > 0:
            game_state.add_score(humans * per)
        game_state.mark_victory()
        return

    if game_state.defense_phase == "surface":
        if humans > 0:
            # Defender: superficie sigue hasta perder todos los astronautas; repetir oleada.
            cw_surf = int(game_state.get_rule("score_surface_wave_clear_bonus", 120))
            game_state.add_score(max(0, cw_surf))
            tpl = clone_spawn_events(spawner.surface_template)
            spawner.load_event_wave(tpl)
        return

    cw = int(game_state.get_rule("score_space_wave_clear_bonus", 200))
    game_state.add_score(max(0, cw))

    nw = len(spawner.space_wave_templates)
    idx = int(game_state.space_wave_index)

    if idx + 1 < nw:
        game_state.space_wave_index = idx + 1
        nxt = clone_spawn_events(spawner.space_wave_templates[game_state.space_wave_index])
        spawner.load_event_wave(nxt)
        game_state.reset_wave_survival_timers()
        game_state.scenario_space_skirmish = True
        return

    _restore_planet_phase(spawner)
