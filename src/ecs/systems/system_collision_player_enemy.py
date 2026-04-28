import esper

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_tags import CTagEnemy, CTagPlayer
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.engine.audio_util import play_sound


def _dims(ent):
    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return float(sz.w), float(sz.h)
    return 0.0, 0.0


def _aabb_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _play_collision_sfx():
    for _, sfx in esper.get_component(CPlayerSfx):
        if sfx.collision_sound_path:
            play_sound(sfx.collision_sound_path, 0.42)
        break


def system_collision_player_enemy():
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    pe, (ppos, _tp) = players[0]
    pw, ph = _dims(pe)

    to_remove = []
    for ee, (epos, _te) in esper.get_components(CPosition, CTagEnemy):
        ew, eh = _dims(ee)
        if _aabb_overlap(
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
            _play_collision_sfx()
            to_remove.append(ee)

    for ent in to_remove:
        esper.delete_entity(ent, immediate=True)
