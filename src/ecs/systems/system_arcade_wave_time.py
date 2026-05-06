import src.engine.game_state as game_state


def system_arcade_wave_time(delta_time: float) -> None:
    if not game_state.defense_arcade_enabled or game_state.paused:
        return
    if game_state.game_phase != "play":
        return
    if game_state.defense_phase != "space":
        return
    game_state.wave_survival_sec += max(0.0, float(delta_time))
