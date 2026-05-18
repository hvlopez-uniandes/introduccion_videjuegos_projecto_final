"""Bala rival vs jugador: descuenta vida y respawn en spawn nivel."""

import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_tags import CTagEnemyBullet, CTagPlayer
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap
from src.engine.audio_util import play_sound
import src.engine.game_state as game_state


def _play_collision_sfx():
    for _, sfx in esper.get_component(CPlayerSfx):
        if sfx.collision_sound_path:
            play_sound(sfx.collision_sound_path, 0.38)
        break


def system_collision_enemy_bullet_player():
    if game_state.game_phase != "play":
        return
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (ppos, _tp) = players[0]
    pw, ph = get_entity_dims(pe)
    rm = []

    for be, (bpos, _tb) in esper.get_components(CPosition, CTagEnemyBullet):
        bw, bh = get_entity_dims(be)
        if aabb_overlap(
            ppos.x, ppos.y, pw, ph,
            bpos.x, bpos.y, bw, bh,
        ):
            rm.append(be)
            _play_collision_sfx()

    for ent in rm:
        esper.delete_entity(ent, immediate=True)

    if rm and game_state.lose_life():
        game_state.respawn_player_entity(pe)
