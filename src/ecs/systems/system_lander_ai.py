"""Lander Defender: hunter-like + disparo en vista + rapto ascendente."""

import math
import random

import esper

from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_color import CColor
from src.ecs.components.c_lander_ai import CLanderAI
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_tags import CTagEnemyBullet, CTagAstronaut, CTagEnemy, CTagLander, CTagPlayer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity
import src.engine.game_state as game_state
from src.engine.audio_util import play_sound
from src.engine.viewport import aabb_in_viewport
from src.engine.service_locator import ServiceLocator


_bullet_surface_cache = {}


def _shared_enemy_bullet_surface(rel_path: str, num_frames: int) -> CSurface:
    key = (rel_path, int(num_frames))
    if key not in _bullet_surface_cache:
        surf = ServiceLocator.current().get("textures").load(rel_path)
        _bullet_surface_cache[key] = CSurface(surf, int(num_frames))
    return _bullet_surface_cache[key]


def _dims_player(ent):
    from src.ecs.components.c_surface import CSurface

    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is None:
        return 12.0, 8.0
    return float(sz.w), float(sz.h)


def _enemy_dims(ent):
    from src.ecs.components.c_surface import CSurface

    s = esper.try_component(ent, CSurface)
    if s is not None:
        return float(s.area_w), float(s.area_h)
    sz = esper.try_component(ent, CSize)
    if sz is None:
        return 10.0, 10.0
    return float(sz.w), float(sz.h)


def _dims_any(ent):
    return _enemy_dims(ent)


def _aabb_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _nearest_ground_human(lx_cx, lx_cy, hz):
    """Humano en suelo más cercano al lander dentro de anchura característica hz."""
    best_ent = -1
    best_d2 = 1e18
    best_pos = None
    best_aw = best_ah = 0.0
    radial = hz * hz * 25.0
    for ae, (apos, az, _ta) in esper.get_components(CPosition, CAstronautState, CTagAstronaut):
        if az.mode != CAstronautState.GROUND:
            continue
        aw, ah = _dims_any(ae)
        tcx = apos.x + aw * 0.5 - lx_cx
        tcy = apos.y + ah * 0.5 - lx_cy
        d2 = tcx * tcx + tcy * tcy
        if d2 <= radial and d2 < best_d2:
            best_d2 = d2
            best_ent = ae
            best_pos = apos
            best_aw = aw
            best_ah = ah
    if best_ent < 0:
        return -1, None, 0.0, 0.0, 0.0
    return best_ent, best_pos, math.sqrt(best_d2), best_aw, best_ah


def system_lander_ai(delta_time):
    players = list(esper.get_components(CPosition, CTagPlayer))
    if not players:
        return
    _, (ppos, _tp) = players[0]
    pe = players[0][0]
    pw, ph = _dims_player(pe)

    sh = float(game_state.world_screen_h or 256)
    visible = aabb_in_viewport(float(ppos.x), float(ppos.y), pw, ph, margin=8.0)
    hz = float(game_state.get_rule("lander_capture_horizontal_px", 104.0))

    for ent, (pos, vel, ai, _te, _tl) in esper.get_components(
        CPosition, CVelocity, CLanderAI, CTagEnemy, CTagLander,
    ):
        ew, eh = _enemy_dims(ent)
        lx_cx = pos.x + ew * 0.5
        lx_cy = pos.y + eh * 0.5

        if ai.capture_phase == "idle" and ai.carried_astronaut_entity < 0:
            ae, apos_near, _, aw_u, _ = _nearest_ground_human(lx_cx, lx_cy, hz)
            if ae >= 0 and apos_near is not None:
                acx = apos_near.x + aw_u * 0.5
                if abs(lx_cx - acx) <= hz:
                    ai.capture_phase = "approach"
                    ai.capture_target_astronaut = ae

        if ai.capture_phase == "approach":
            te = ai.capture_target_astronaut
            if not esper.entity_exists(te):
                ai.capture_phase = "idle"
                ai.capture_target_astronaut = -1
                vel.vx = vel.vy = 0.0
            else:
                apos = esper.try_component(te, CPosition)
                az = esper.try_component(te, CAstronautState)
                if apos is None or az is None or az.mode != CAstronautState.GROUND:
                    ai.capture_phase = "idle"
                    ai.capture_target_astronaut = -1
                    vel.vx = vel.vy = 0.0
                else:
                    aw, ah = _dims_any(te)
                    tcx = apos.x + aw * 0.5 - lx_cx
                    tcy = apos.y + ah * 0.5 - lx_cy
                    d = math.hypot(tcx, tcy)
                    spd = ai.approach_speed
                    if d < 12.0 and _aabb_overlap(
                        pos.x, pos.y, ew, eh,
                        apos.x, apos.y, aw, ah,
                    ):
                        ai.capture_phase = "ascend"
                        ai.carried_astronaut_entity = te
                        ai.capture_target_astronaut = -1
                        az.mode = CAstronautState.LANDER_CARRY
                        az.carrier_ent = ent
                        play_sound(str(game_state.get_rule("sound_lander_capture", "")), 0.62)
                    elif d > 1e-3:
                        vel.vx = tcx / d * spd
                        vel.vy = tcy / d * spd
                    elif d <= 1e-3:
                        vel.vx = vel.vy = 0.0

            ai.shoot_cd = max(0.0, ai.shoot_cd - delta_time)
            continue

        if ai.capture_phase == "ascend":
            ai.capture_target_astronaut = -1
            vel.vx = 0.0
            vel.vy = -ai.ascend_speed
            ai.shoot_cd = max(0.0, ai.shoot_cd - delta_time)
            continue

        prev_state = ai.state
        dx_p = ppos.x - pos.x
        dy_p = ppos.y - pos.y
        dist_p = math.hypot(dx_p, dy_p)
        dist_o = math.hypot(pos.x - ai.origin_x, pos.y - ai.origin_y)

        if ai.state == "return":
            dx = ai.origin_x - pos.x
            dy = ai.origin_y - pos.y
            d = math.hypot(dx, dy)
            if d < 2.0:
                pos.x = ai.origin_x
                pos.y = ai.origin_y
                vel.vx = 0.0
                vel.vy = 0.0
                ai.state = "idle"
            else:
                vel.vx = dx / d * ai.v_return
                vel.vy = dy / d * ai.v_return
        elif ai.state == "chase":
            if dist_o > ai.return_dist + 0.5:
                ai.state = "return"
                continue
            if dist_p < 1e-6:
                vel.vx = 0.0
                vel.vy = 0.0
            else:
                vel.vx = dx_p / dist_p * ai.v_chase
                vel.vy = dy_p / dist_p * ai.v_chase
        else:
            vel.vx = 0.0
            vel.vy = 0.0
            if dist_p <= ai.chase_dist:
                ai.state = "chase"

        if prev_state == "idle" and ai.state == "chase" and ai.sound_chase_path:
            play_sound(ai.sound_chase_path, 0.72)

        if delta_time <= 0.0:
            continue

        ai.shoot_cd = max(0.0, ai.shoot_cd - delta_time)

        can_try_shoot = visible and ai.state in ("idle", "chase") and ai.capture_phase == "idle"
        if not can_try_shoot or ai.shoot_cd > 0.0:
            continue

        pcx = ppos.x + pw * 0.5
        pcy = ppos.y + ph * 0.5
        ecx = pos.x + ew * 0.5
        ecy = pos.y + eh * 0.5
        fdx = pcx - ecx
        fdy = pcy - ecy
        dist = math.hypot(fdx, fdy)
        if dist < 18.0:
            continue
        fdx /= dist
        fdy /= dist

        bv = ai.bullet_velocity
        bullet = esper.create_entity()
        esper.add_component(bullet, CVelocity(fdx * bv, fdy * bv))
        bimg = str(getattr(ai, "bullet_image_path", "") or "").strip()
        if bimg:
            bcs = _shared_enemy_bullet_surface(bimg, int(getattr(ai, "bullet_num_frames", 1) or 1))
            bx = ecx - bcs.area_w / 2.0
            by = ecy - bcs.area_h / 2.0
            esper.add_component(bullet, CPosition(bx, by))
            esper.add_component(bullet, bcs)
        else:
            bx = ecx - ai.bullet_w / 2.0
            by = ecy - ai.bullet_h / 2.0
            esper.add_component(bullet, CPosition(bx, by))
            esper.add_component(bullet, CSize(ai.bullet_w, ai.bullet_h))
            esper.add_component(
                bullet,
                CColor(ai.bullet_r, ai.bullet_g, ai.bullet_b),
            )
        esper.add_component(bullet, CTagEnemyBullet())

        ai.shoot_cd = ai.shoot_interval_sec
        if ai.shoot_sound_path:
            play_sound(ai.shoot_sound_path, 0.35)


def release_human_from_dead_lander(enemy_ent) -> None:
    ai = esper.try_component(enemy_ent, CLanderAI)
    if ai is None or ai.carried_astronaut_entity < 0:
        return
    ae = ai.carried_astronaut_entity
    if not esper.entity_exists(ae):
        return
    st = esper.try_component(ae, CAstronautState)
    vel = esper.try_component(ae, CVelocity)
    if st is not None:
        st.mode = CAstronautState.FALLING
        st.carrier_ent = -1
    if vel is not None:
        vel.vx = random.uniform(-40.0, 40.0)
        vel.vy = random.uniform(30.0, 65.0)
    play_sound(str(game_state.get_rule("sound_astronaut_fall", "")), 0.48)
    ai.carried_astronaut_entity = -1
    ai.capture_phase = "idle"
