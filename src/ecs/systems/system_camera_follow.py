"""Centra la cámara sobre el jugador en mundos más anchos que la ventana."""

import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer


def system_camera_follow() -> None:
    sw = float(game_state.world_screen_w or 320)
    ww = float(game_state.world_wrap_w or sw)
    max_cam = max(0.0, ww - sw)
    for ent, (pos, _tp) in esper.get_components(CPosition, CTagPlayer):
        surf = esper.try_component(ent, CSurface)
        if surf is not None:
            aw = float(surf.area_w)
        else:
            sz = esper.try_component(ent, CSize)
            if sz is None:
                game_state.camera_scroll_x = max(0.0, min(max_cam, game_state.camera_scroll_x))
                return
            aw = float(sz.w)
        pcx = float(pos.x) + aw * 0.5
        cam = pcx - sw * 0.5
        game_state.camera_scroll_x = max(0.0, min(max_cam, cam))
        return
    game_state.camera_scroll_x = max(0.0, min(max_cam, float(game_state.camera_scroll_x)))
