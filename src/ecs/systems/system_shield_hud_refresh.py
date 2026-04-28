import esper

import src.engine.game_state as game_state

from src.ecs.components.c_shield_special import CShieldSpecial
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagHudDynamic, CTagPlayer
from src.ecs.components.c_ui_text_style import CUiTextStyle
from src.engine.service_locator import ServiceLocator


def system_shield_hud_refresh() -> None:
    if game_state.paused:
        return
    hud = None
    for _e, (_h, st, surf) in esper.get_components(CTagHudDynamic, CUiTextStyle, CSurface):
        hud = (st, surf)
        break
    if hud is None:
        return
    st, surf = hud

    text = "Pulso: --"
    for _, (shield, _tp) in esper.get_components(CShieldSpecial, CTagPlayer):
        if shield.active_remaining > 0.0:
            text = f"Pulso activo {shield.active_remaining:.1f}s"
        elif shield.cooldown_remaining > 0.0:
            total = max(shield.cooldown_sec, 1e-6)
            pct = int(100.0 * (1.0 - shield.cooldown_remaining / total))
            text = f"Recarga {shield.cooldown_remaining:.1f}s  [{pct}%]"
        else:
            text = "Pulso LISTO [ESP]"
        break

    font = ServiceLocator.current().get("fonts").get(st.font_path, st.size_px)
    surf.update_from_text(font, text, (st.r, st.g, st.b), st.antialias)
