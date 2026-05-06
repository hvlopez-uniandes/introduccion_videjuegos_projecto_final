"""Visibilidad respecto a la cámara y al ancho de mundo (toro horizontal)."""

import src.engine.game_state as game_state


def _metrics():
    cam = float(getattr(game_state, "camera_scroll_x", None) or 0.0)
    sw = float(game_state.world_screen_w or 320)
    ww = float(game_state.world_wrap_w or sw)
    sh = float(game_state.world_screen_h or 256)
    return cam, sw, ww, sh


def horiz_overlaps_viewport(px: float, pw: float, margin: float = 6.0) -> bool:
    """True si el segmento horizontal [px, px+pw] intersecta la franja visible (con margen)."""
    cam, sw, ww, _ = _metrics()
    if pw < 0.0:
        pw = 0.0
    lo = min(px, px + pw)
    hi = max(px, px + pw)
    vp_lo = cam - margin
    vp_hi = cam + sw + margin
    if ww <= sw + margin * 2 + 4.0:
        return hi > vp_lo and lo < vp_hi
    for k in (-2, -1, 0, 1, 2):
        lo_k = lo + k * ww
        hi_k = hi + k * ww
        if hi_k > vp_lo and lo_k < vp_hi:
            return True
    return False


def aabb_in_viewport(px: float, py: float, pw: float, ph: float, margin: float = 6.0) -> bool:
    cam, sw, ww, sh = _metrics()
    _ = cam, sw, ww
    if py + ph <= -margin or py >= sh + margin:
        return False
    return horiz_overlaps_viewport(px, pw, margin=margin)


def world_to_screen_x_positions(world_x: float, entity_w: float) -> list[float]:
    """Posiciones en pantalla para dibujar una entidad de mundo (copias del toro si aplica)."""
    cam, sw, ww, _ = _metrics()
    x0 = world_x - cam
    xs = [x0]
    if ww > sw + 0.5:
        xs.extend([x0 + ww, x0 - ww])
    margin = max(80.0, float(entity_w) + 64.0)
    out = []
    for sx in xs:
        if sx + entity_w > -margin and sx < sw + margin:
            out.append(sx)
    return out

