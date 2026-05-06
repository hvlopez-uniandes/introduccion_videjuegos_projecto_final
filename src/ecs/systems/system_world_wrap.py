"""Avance 3: wrap horizontal para jugador/proyectiles/astros; adversarios también vertical."""

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_scenario import CTagScenarioBackground
from src.ecs.components.c_tags import (
    CTagAstronaut,
    CTagBullet,
    CTagEnemy,
    CTagEnemyBullet,
    CTagExplosion,
    CTagHud,
    CTagHudDynamic,
    CTagPlayer,
)


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 0.0, 0.0


def _wrap_horizontal(pos, w, ww):
    if ww <= 0:
        return
    while pos.x < -24.0:
        pos.x += ww
    while pos.x + w > ww + 24.0:
        pos.x -= ww


def _wrap_vertical(pos, h, sh):
    if sh <= 0:
        return
    while pos.y < -48.0:
        pos.y += sh
    while pos.y + h > sh + 48.0:
        pos.y -= sh


def system_world_wrap(screen_w: int, screen_h: int) -> None:
    ww = float(game_state.world_wrap_w if game_state.world_wrap_w else screen_w)
    sh = float(screen_h)

    for ent, (pos,) in esper.get_components(CPosition):
        if esper.try_component(ent, CTagHud) or esper.try_component(ent, CTagHudDynamic):
            continue
        if esper.try_component(ent, CTagExplosion):
            continue
        if esper.try_component(ent, CTagScenarioBackground):
            continue

        aw, ah = _dims(ent)
        if aw <= 0:
            continue

        is_player = esper.try_component(ent, CTagPlayer) is not None
        is_ast = esper.try_component(ent, CTagAstronaut) is not None
        is_pb = esper.try_component(ent, CTagBullet) is not None
        is_eb = esper.try_component(ent, CTagEnemyBullet) is not None
        is_enemy = esper.try_component(ent, CTagEnemy) is not None

        if is_ast:
            _wrap_horizontal(pos, aw, ww)
        elif is_pb or is_eb:
            if not is_pb:
                _wrap_horizontal(pos, aw, ww)
            # Láser jugador: sin wrap horizontal (arcade / enunciato; mueren en system_bullet_bounds).
        elif is_player:
            _wrap_horizontal(pos, aw, ww)
        elif is_enemy:
            _wrap_horizontal(pos, aw, ww)
            _wrap_vertical(pos, ah, sh)
