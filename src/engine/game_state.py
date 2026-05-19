paused = False
play_area_top_px = None
play_area_bottom_px = None
world_wrap_w = None
world_screen_w = None
world_screen_h = None
camera_scroll_x = 0.0
planet_explosion_flash_remaining = 0.0
smart_bomb_flash_remaining = 0.0
player_occluded_by_terrain = False
tick_dt = 0.016
homing_missiles = 3

score = 0
lives = 3
player_spawn_x = 160.0
player_spawn_y = 96.0
session_time_accum = 0.0

game_phase = "menu"
game_over = False
level_victorious = False
fanfare_needed = False
rules_cache = {}

arcade_defender_flight = False
smart_bombs = 0
next_score_milestone = 10_000

defense_arcade_enabled = False
defense_phase = "surface"
space_wave_index = 0
surface_astronauts_initial = 0
wave_survival_sec = 0.0
baiter_spawned_this_wave = False
play_cfg_dir = None
play_screen_h_int = 256
scenario_space_skirmish = False
defense_space_waves_total = 0
high_score_saved = 0

# Player respawn transient (invuln optional future)
_pause_blink_phase = 0.0


def _high_score_path():
    """Ruta estable bajo raíz del proyecto (crea userdata si hace falta)."""
    from pathlib import Path

    try:
        from src.engine.paths import PROJECT_ROOT as _root
    except Exception:
        _root = None
    root = Path(_root) if _root else Path.cwd()
    d = root / "userdata"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return d / "high_score.json"


def load_high_score_from_disk():
    """Carga mejor puntuación histórico (Williams Defender: marcador alto)."""
    global high_score_saved
    path = _high_score_path()
    if path is None or not path.is_file():
        return
    try:
        import json

        raw = json.loads(path.read_text(encoding="utf-8"))
        best = raw.get("best")
        best = max(0, int(best))
        high_score_saved = max(high_score_saved, best)
    except (OSError, ValueError, TypeError, KeyError):
        pass


def _persist_high_score():
    """Escribe mejor puntuación en disco."""
    global high_score_saved
    path = _high_score_path()
    if path is None:
        return
    try:
        import json

        payload = {"best": int(high_score_saved)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        pass


def record_high_score_if_best(candidate: int) -> None:
    """Actualiza récord persistente si `candidate` es mayor (típ. puntaje actual)."""
    global high_score_saved
    c = max(0, int(candidate))
    if c <= int(high_score_saved):
        return
    high_score_saved = c
    _persist_high_score()


def high_score_best_display() -> int:
    """Valor mostrado como MÁX: récord en disco y puntaje de la partida (el mayor de los dos)."""
    return max(int(high_score_saved), int(score))


def _arcade_reset_economy() -> None:
    global smart_bombs, next_score_milestone
    smart_bombs = int(get_rule("initial_smart_bombs", 3))
    step = max(1, int(get_rule("score_extra_life_every", 10_000)))
    next_score_milestone = step


def set_arcade_defender_flight(enabled: bool) -> None:
    global arcade_defender_flight
    arcade_defender_flight = bool(enabled)


def consume_smart_bomb_stock() -> bool:
    """Gasta una smart bomb si hay stock; False si no hay."""
    global smart_bombs
    if smart_bombs <= 0:
        return False
    smart_bombs -= 1
    return True


def add_smart_bombs(n: int) -> None:
    global smart_bombs
    cap = max(0, int(get_rule("smart_bomb_inventory_cap", 254)))
    smart_bombs = min(cap, int(smart_bombs) + int(n))


def reset_wave_survival_timers() -> None:
    global wave_survival_sec, baiter_spawned_this_wave
    wave_survival_sec = 0.0
    baiter_spawned_this_wave = False


def add_extra_life(n: int = 1) -> None:
    global lives
    cap = max(1, int(get_rule("extra_lives_cap", 255)))
    lives = min(cap, int(lives) + int(n))


def toggle_pause() -> None:
    global paused
    if game_over or game_phase != "play":
        return
    from src.engine.audio_util import play_sound

    was_paused = paused
    paused = not paused
    if paused and not was_paused:
        play_sound(str(get_rule("sound_pause", "")), 0.42)


def set_paused(value: bool) -> None:
    global paused
    paused = bool(value)


def set_world_metrics(screen_w_px: int, screen_h_px: int) -> None:
    global world_wrap_w, world_screen_w, world_screen_h, camera_scroll_x
    vw = max(1, int(screen_w_px))
    hh = max(1, int(screen_h_px))
    world_screen_w = vw
    world_screen_h = hh
    play_w_rule = get_rule("world_play_width_px", vw)
    try:
        play_w_int = max(vw, int(float(play_w_rule)))
    except (TypeError, ValueError):
        play_w_int = vw
    world_wrap_w = play_w_int
    camera_scroll_x = max(
        0.0,
        min(float(play_w_int - vw), float(camera_scroll_x)),
    )


def set_play_area_vertical(top_px, bottom_px):
    global play_area_top_px, play_area_bottom_px
    play_area_top_px = None if top_px is None else int(top_px)
    play_area_bottom_px = None if bottom_px is None else int(bottom_px)


def set_rules(merged: dict) -> None:
    global rules_cache
    rules_cache = dict(merged) if merged else {}


def get_rule(name: str, default=None):
    return rules_cache.get(name, default)


def set_spawn(x: float, y: float) -> None:
    global player_spawn_x, player_spawn_y
    player_spawn_x = float(x)
    player_spawn_y = float(y)


def reset_session_for_new_level(lives_override: int = None):
    global score, lives, game_over, level_victorious, paused, session_time_accum
    record_high_score_if_best(score)
    score = 0
    lives = int(lives_override if lives_override is not None else get_rule("initial_lives", 3))
    game_over = False
    level_victorious = False
    paused = False
    session_time_accum = 0.0
    _arcade_reset_economy()
    reset_homing_missiles()


def begin_play_after_menu():
    global game_phase, fanfare_needed, paused, game_over, level_victorious
    game_phase = "play"
    fanfare_needed = True
    paused = False
    game_over = False
    level_victorious = False


def return_to_menu():
    global game_phase, paused, game_over, level_victorious
    global scenario_space_skirmish, planet_explosion_flash_remaining, smart_bomb_flash_remaining, player_occluded_by_terrain
    global defense_phase
    game_phase = "menu"
    paused = False
    game_over = False
    level_victorious = False
    scenario_space_skirmish = False
    planet_explosion_flash_remaining = 0.0
    smart_bomb_flash_remaining = 0.0
    player_occluded_by_terrain = False
    defense_phase = "surface"
    reset_wave_survival_timers()


def add_score(delta: int) -> None:
    global score, next_score_milestone
    score = max(0, int(score + int(delta)))
    record_high_score_if_best(score)
    if not arcade_defender_flight:
        return
    step = max(1, int(get_rule("score_extra_life_every", 10_000)))
    while score >= next_score_milestone:
        next_score_milestone += step
        add_extra_life(1)
        add_smart_bombs(1)
        reset_homing_missiles()

def lose_life() -> bool:
    """Devuelve True si aún quedan vidas."""
    global lives, game_over, game_phase
    from src.engine.audio_util import play_sound

    lives = max(0, int(lives) - 1)
    if lives <= 0:
        record_high_score_if_best(score)
        game_over = True
        game_phase = "game_over"
        play_sound(str(get_rule("sound_game_over", "")), 0.65)
        return False
    return True


def respawn_player_entity(player_ent, cfg_h_pad=True):
    """Reubica la nave al spawn de nivel (tras perder vida)."""
    import esper
    from src.ecs.components.c_arcade_defender_flight import CArcadeDefenderFlight
    from src.ecs.components.c_position import CPosition
    from src.ecs.components.c_velocity import CVelocity

    pos = esper.try_component(player_ent, CPosition)
    vel = esper.try_component(player_ent, CVelocity)
    if pos is not None:
        pos.x = player_spawn_x
        pos.y = player_spawn_y
    if vel is not None:
        vel.vx = 0.0
        vel.vy = 0.0
    arc = esper.try_component(player_ent, CArcadeDefenderFlight)
    if arc is not None:
        arc.facing = 1


def tick_session(dt: float) -> None:
    global session_time_accum, _pause_blink_phase
    session_time_accum += max(0.0, float(dt))
    _pause_blink_phase = session_time_accum * 6.28318


def pause_overlay_visible() -> bool:
    import math

    return math.sin(_pause_blink_phase) > 0.0


def mark_victory():
    global level_victorious, game_phase
    record_high_score_if_best(score)
    level_victorious = True
    game_phase = "victory"

def consume_homing_missile_stock() -> bool:
    global homing_missiles
    if homing_missiles <= 0:
        return False
    homing_missiles -= 1
    return True

def reset_homing_missiles() -> None:
    global homing_missiles
    homing_missiles = int(get_rule("initial_homing_missiles", 8))


def consume_fanfare_flag() -> bool:
    global fanfare_needed
    t = fanfare_needed
    fanfare_needed = False
    return t
