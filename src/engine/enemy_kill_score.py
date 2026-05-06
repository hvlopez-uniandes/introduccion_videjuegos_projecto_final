"""Puntos al destruir enemigos (láser, bomba inteligente, embestida nave)."""

import esper

from src.ecs.components.c_tags import (
    CTagAsteroid,
    CTagBaiter,
    CTagBomb,
    CTagBomber,
    CTagEnemy,
    CTagHunter,
    CTagLander,
    CTagMutant,
    CTagPod,
    CTagSwarmer,
)
import src.engine.game_state as game_state


def score_for_destroyed_enemy(ent: int) -> int:
    """Suma de puntaje por entidad; 0 si no es enemigo puntuablle."""
    if esper.try_component(ent, CTagEnemy) is None:
        return 0
    if esper.try_component(ent, CTagBomb) is not None:
        return int(game_state.get_rule("score_bomb_destroy", 0))
    if esper.try_component(ent, CTagPod) is not None:
        return int(game_state.get_rule("score_pod_kill", 1000))
    if esper.try_component(ent, CTagBomber) is not None:
        return int(game_state.get_rule("score_bomber_kill", 250))
    if esper.try_component(ent, CTagBaiter) is not None:
        return int(game_state.get_rule("score_baiter_kill", 200))
    if esper.try_component(ent, CTagSwarmer) is not None:
        return int(game_state.get_rule("score_swarmer_kill", 150))
    if esper.try_component(ent, CTagMutant) is not None:
        return int(game_state.get_rule("score_mutant_kill", 150))
    if esper.try_component(ent, CTagLander) is not None:
        return int(game_state.get_rule("score_lander_kill", 150))
    if esper.try_component(ent, CTagHunter) is not None:
        return int(game_state.get_rule("score_hunter_kill", 120))
    if esper.try_component(ent, CTagAsteroid) is not None:
        return int(game_state.get_rule("score_asteroid_kill", 25))
    return 80
