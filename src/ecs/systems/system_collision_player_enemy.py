"""Choque físico nave vs enemigo: daño jugador · libera víctimas Lander ECS."""

import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_tags import CTagEnemy, CTagPlayer
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.ecs.systems.system_lander_ai import release_human_from_dead_lander
from src.engine.audio_util import play_sound
import src.engine.game_state as game_state
from src.engine.enemy_kill_score import score_for_destroyed_enemy


def _play_collision_sfx():
    for _, sfx in esper.get_component(CPlayerSfx):
        if sfx.collision_sound_path:
            play_sound(sfx.collision_sound_path, 0.42)
        break


def system_collision_player_enemy():
    if game_state.game_phase != "play":
        return
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (ppos, _tp) = players[0]
    pw, ph = get_entity_dims(pe)

    to_remove = []
    for ee, (epos, _te) in esper.get_components(CPosition, CTagEnemy):
        ew, eh = get_entity_dims(ee)
        if aabb_overlap(
            ppos.x,
            ppos.y,
            pw,
            ph,
            epos.x,
            epos.y,
            ew,
            eh,
        ):
            cx = epos.x + ew / 2.0
            cy = epos.y + eh / 2.0
            spawn_explosion(cx, cy, play_spawn_sound=False)
            release_human_from_dead_lander(ee)
            to_remove.append(ee)

    for ent in to_remove:
        game_state.add_score(score_for_destroyed_enemy(ent))
        esper.delete_entity(ent, immediate=True)

    if to_remove:
        _play_collision_sfx()
        if game_state.lose_life():
            game_state.respawn_player_entity(pe)
