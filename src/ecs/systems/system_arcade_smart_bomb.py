"""Smart bomb arcade: pantalla visible (misma anchura mundo) borra todos los enemigos."""

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_size import CSize
from src.ecs.components.c_pod_cargo import CPodCargo
from src.ecs.components.c_tags import CTagBomb, CTagEnemy, CTagEnemyBullet, CTagEnemyMissile
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.ecs.systems.spawn_pod_swarm import spawn_swarmers_from_pod_cargo
from src.engine.audio_util import play_sound
from src.engine.enemy_kill_score import score_for_destroyed_enemy
from src.engine.frame_input import consume_smart_bomb
from src.engine.viewport import aabb_in_viewport


def _enemy_center_xy(ent: int):
    pos = esper.try_component(ent, CPosition)
    if pos is None:
        return None
    surf = esper.try_component(ent, CSurface)
    if surf is not None:
        return pos.x + surf.area_w / 2.0, pos.y + surf.area_h / 2.0
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return pos.x + sz.w / 2.0, pos.y + sz.h / 2.0
    return None


def _viewport_kill_center(ent: int):
    """Centro del blip si está en viewport; None si no."""
    pos = esper.try_component(ent, CPosition)
    surf = esper.try_component(ent, CSurface)
    sz = esper.try_component(ent, CSize)
    if pos is None:
        return None
    if surf is not None:
        ew, eh = float(surf.area_w), float(surf.area_h)
    elif sz is not None:
        ew, eh = float(sz.w), float(sz.h)
    else:
        return None
    if not aabb_in_viewport(float(pos.x), float(pos.y), ew, eh, margin=16.0):
        return None
    c = _enemy_center_xy(ent)
    return c


def system_arcade_smart_bomb():
    if not game_state.arcade_defender_flight or game_state.paused:
        return
    if not consume_smart_bomb():
        return
    if not game_state.consume_smart_bomb_stock():
        return

    game_state.smart_bomb_flash_remaining = float(game_state.get_rule("smart_bomb_flash_sec", 0.42))

    # dict: misma entidad no dos veces — p. ej. bombas del bomber llevan CTagEnemy y CTagBomb.
    targets = {}
    for ee, _ in esper.get_component(CTagEnemy):
        c = _viewport_kill_center(ee)
        if c is not None:
            targets[ee] = c
    for tag in (CTagBomb, CTagEnemyBullet, CTagEnemyMissile):
        for ent, _ in esper.get_component(tag):
            c = _viewport_kill_center(ent)
            if c is not None:
                targets[ent] = c

    for ee, (ex, ey) in targets.items():
        game_state.add_score(score_for_destroyed_enemy(ee))
        spawn_explosion(ex, ey, play_spawn_sound=False)
        cargo = esper.try_component(ee, CPodCargo)
        if cargo is not None:
            spawn_swarmers_from_pod_cargo(ex, ey, cargo)
        try:
            esper.delete_entity(ee, immediate=True)
        except KeyError:
            pass
    play_sound("assets/snd/explosion.ogg", 0.55)
