import math

import esper

import src.engine.game_state as game_state

from src.ecs.commands import CommandContext
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_arcade_defender_flight import CArcadeDefenderFlight
from src.ecs.components.c_bullet_def import CBulletDef
from src.ecs.components.c_color import CColor
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_input_speed import CPlayerInputSpeed
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet, CTagEnemyBullet, CTagPlayer
from src.ecs.components.c_player_arcade_burner import CPlayerArcadeBurner
from src.ecs.components.c_velocity import CVelocity
import src.engine.paths as engine_paths
from src.engine.audio_util import play_sound
from src.engine.service_locator import ServiceLocator


def system_execute_commands():
    bullet_def = None
    max_bullets = 99
    for _, sp in esper.get_component(CEnemySpawner):
        max_bullets = sp.max_bullets
    for _, bd in esper.get_component(CBulletDef):
        bullet_def = bd
        break
    if bullet_def is None:
        bullet_def = CBulletDef(200, image_path="assets/img/bullet.png")

    def _player_bullet_count():
        return sum(
            1 for e, _ in esper.get_component(CTagBullet) if esper.try_component(e, CTagEnemyBullet) is None
        )

    n_bullets = _player_bullet_count()
    dt = max(1e-4, float(game_state.tick_dt))
    smooth_hz = lambda sp: min(1.0, float(sp.smoothing_hz) * dt)

    def _arcade_integrate(af: CArcadeDefenderFlight, vel: CVelocity, ctx: CommandContext, speed: CPlayerInputSpeed):
        if ctx.reverse_triggered:
            af.facing = -af.facing
            vel.vx *= -1.0
        ax = 0.0
        if ctx.thrust_active:
            ax += float(af.facing) * af.thrust_accel_px_s2
        lx = max(-1.0, min(1.0, float(ctx.dir_x)))
        if lx != 0.0:
            ax += lx * af.thrust_accel_px_s2
        vel.vx += ax * dt
        cap = af.max_speed_x
        if vel.vx > cap:
            vel.vx = cap
        elif vel.vx < -cap:
            vel.vx = -cap
        drag = math.exp(-af.drag_per_s * dt)
        vel.vx *= drag
        dy = max(-1.0, min(1.0, float(ctx.dir_y)))
        t_vy = dy * af.vertical_speed_px_s
        sm = smooth_hz(speed)
        vel.vy += (t_vy - vel.vy) * sm

    def _spawn_bullet_sprite(cx: float, cy: float, bvx: float, bvy: float) -> None:
        nonlocal n_bullets
        if bullet_def.is_sprite():
            bsurf = ServiceLocator.current().get("textures").load(bullet_def.image_path)
            bcs = CSurface(bsurf, bullet_def.num_frames)
            bw = bcs.area_w
            bh = bcs.area_h
        else:
            bw = bullet_def.w
            bh = bullet_def.h
        bx = cx - bw / 2.0
        by = cy - bh / 2.0
        be = esper.create_entity()
        esper.add_component(be, CPosition(bx, by))
        esper.add_component(be, CVelocity(bvx, bvy))
        if bullet_def.is_sprite():
            esper.add_component(be, bcs)
        else:
            esper.add_component(be, CSize(bw, bh))
            esper.add_component(be, CColor(bullet_def.r, bullet_def.g, bullet_def.b))
        esper.add_component(be, CTagBullet())
        n_bullets += 1
        if bullet_def.sound_path:
            play_sound(bullet_def.sound_path, 0.55)

    def _spawn_bullet_rect(cx: float, cy: float, bvx: float, bvy: float) -> None:
        nonlocal n_bullets
        bx = cx - bullet_def.w / 2.0
        by = cy - bullet_def.h / 2.0
        be = esper.create_entity()
        esper.add_component(be, CPosition(bx, by))
        esper.add_component(be, CVelocity(bvx, bvy))
        esper.add_component(be, CSize(bullet_def.w, bullet_def.h))
        esper.add_component(be, CColor(bullet_def.r, bullet_def.g, bullet_def.b))
        esper.add_component(be, CTagBullet())
        n_bullets += 1
        if bullet_def.sound_path:
            play_sound(bullet_def.sound_path, 0.55)

    root = engine_paths.PROJECT_ROOT

    for _ent, (inp, vel, pos, speed, _tp) in esper.get_components(
        CInputCommand,
        CVelocity,
        CPosition,
        CPlayerInputSpeed,
        CTagPlayer,
    ):
        surf = esper.try_component(_ent, CSurface)
        anim = esper.try_component(_ent, CAnimation)
        sz = esper.try_component(_ent, CSize)
        af = esper.try_component(_ent, CArcadeDefenderFlight)

        ctx = CommandContext()
        for c in inp.command_queue:
            c.execute(ctx)

        if af is not None:
            _arcade_integrate(af, vel, ctx, speed)
            brn = esper.try_component(_ent, CPlayerArcadeBurner)
            if brn is not None:
                lx = max(-1.0, min(1.0, float(ctx.dir_x)))
                brn.boost = bool(ctx.thrust_active) or abs(lx) > 1e-6
                brn.anim_t += dt
        else:
            dx, dy = ctx.dir_x, ctx.dir_y
            if dx != 0 and dy != 0:
                inv = 1.0 / math.sqrt(2.0)
                dx *= inv
                dy *= inv
            t_vx = dx * speed.pixels_per_second
            t_vy = dy * speed.pixels_per_second
            sm = smooth_hz(speed)
            vel.vx += (t_vx - vel.vx) * sm
            vel.vy += (t_vy - vel.vy) * sm

        if ctx.fire_mx is None or n_bullets >= max_bullets or root is None:
            continue

        if surf is not None:
            cx = pos.x + surf.area_w / 2.0
            cy = pos.y + surf.area_h / 2.0
        elif sz is not None:
            cx = pos.x + sz.w / 2.0
            cy = pos.y + sz.h / 2.0
        else:
            continue

        if af is not None:
            bs = float(bullet_def.velocity)
            bvx = float(af.facing) * bs
            bvy = 0.0
            if surf is not None:
                _spawn_bullet_sprite(cx, cy, bvx, bvy)
            else:
                _spawn_bullet_rect(cx, cy, bvx, bvy)
            continue

        fdx = ctx.fire_mx - cx
        fdy = ctx.fire_my - cy
        dist = math.hypot(fdx, fdy)
        if dist <= 1e-6:
            continue
        fdx /= dist
        fdy /= dist
        bvx = fdx * bullet_def.velocity
        bvy = fdy * bullet_def.velocity
        if surf is not None:
            _spawn_bullet_sprite(cx, cy, bvx, bvy)
        else:
            _spawn_bullet_rect(cx, cy, bvx, bvy)
