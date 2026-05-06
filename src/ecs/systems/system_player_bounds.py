import esper

import src.engine.game_state as game_state

from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagPlayer


def system_player_bounds(screen_w, screen_h):
    sw = float(screen_w)
    sh = float(screen_h)
    ww = float(game_state.world_wrap_w if game_state.world_wrap_w else screen_w)

    for ent, (pos, _tp) in esper.get_components(CPosition, CTagPlayer):
        surf = esper.try_component(ent, CSurface)
        if surf is not None:
            aw = surf.area_w
            ah = surf.area_h
        else:
            sz = esper.try_component(ent, CSize)
            if sz is None:
                continue
            aw = float(sz.w)
            ah = float(sz.h)

        max_x = max(0.0, ww - aw)
        max_y_scene = max(0.0, sh - ah)

        eff_top = 0.0
        if game_state.play_area_top_px is not None:
            eff_top = max(0.0, float(game_state.play_area_top_px))
        reserve = float(game_state.get_rule("scoreboard_reserve_top_px", 0.0))
        if reserve <= 0.0:
            reserve = min(115.0, max(52.0, float(sh) * 0.07))
        eff_top = max(eff_top, reserve)
        eff_top = min(eff_top, max_y_scene)

        bottom_wall = sh
        if game_state.play_area_bottom_px is not None:
            bottom_wall = float(game_state.play_area_bottom_px)
        bottom_wall = max(0.0, min(bottom_wall, sh))

        min_y = eff_top

        # Reserva inferior (relieve + radar + marcador): evita atravesar el “suelo” visual al escalar ventana.
        bw_cap_feet_max = bottom_wall
        air_px_rule = float(game_state.get_rule("playfield_air_bottom_px", -1.0))
        if air_px_rule >= 0.0:
            bw_cap_feet_max = float(sh) - max(0.0, air_px_rule)
        elif not game_state.scenario_space_skirmish:
            frac_air = float(game_state.get_rule("playfield_air_bottom_frac", -1.0))
            if frac_air < 0:
                frac_air = 0.22 if game_state.arcade_defender_flight else 0.17
            raw_strip = float(sh) * frac_air
            strip_h = min(0.40 * float(sh), max(56.0, raw_strip))
            bw_cap_feet_max = float(sh) - strip_h
        bw_cap_feet_max = max(0.0, min(float(sh), bw_cap_feet_max))
        if bw_cap_feet_max > min_y + float(ah) + 6.0:
            bottom_wall = min(bottom_wall, bw_cap_feet_max)

        max_y_allowed = min(max_y_scene, bottom_wall - ah)
        max_y_allowed = max(max_y_allowed, min_y)
        if max_y_allowed > max_y_scene:
            max_y_allowed = max_y_scene

        if pos.x < 0:
            pos.x = 0.0
        elif pos.x > max_x:
            pos.x = max_x

        if pos.y < min_y:
            pos.y = min_y
        elif pos.y > max_y_allowed:
            pos.y = max_y_allowed
