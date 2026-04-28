import math

import esper

from src.ecs.commands import CommandContext
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_bullet_def import CBulletDef
from src.ecs.components.c_color import CColor
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_input_speed import CPlayerInputSpeed
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBullet, CTagPlayer
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

    n_bullets = len(list(esper.get_component(CTagBullet)))

    for _ent, (inp, vel, pos, surf, speed, anim, _tp) in esper.get_components(
        CInputCommand,
        CVelocity,
        CPosition,
        CSurface,
        CPlayerInputSpeed,
        CAnimation,
        CTagPlayer,
    ):
        ctx = CommandContext()
        for c in inp.command_queue:
            c.execute(ctx)

        dx, dy = ctx.dir_x, ctx.dir_y
        if dx != 0 and dy != 0:
            inv = 1.0 / math.sqrt(2.0)
            dx *= inv
            dy *= inv
        vel.vx = dx * speed.pixels_per_second
        vel.vy = dy * speed.pixels_per_second

        root = engine_paths.PROJECT_ROOT
        if ctx.fire_mx is not None and n_bullets < max_bullets and root is not None:
            cx = pos.x + surf.area_w / 2.0
            cy = pos.y + surf.area_h / 2.0
            fdx = ctx.fire_mx - cx
            fdy = ctx.fire_my - cy
            dist = math.hypot(fdx, fdy)
            if dist > 1e-6:
                fdx /= dist
                fdy /= dist
                bvx = fdx * bullet_def.velocity
                bvy = fdy * bullet_def.velocity
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

    for _ent, (inp, vel, pos, size, speed, _tp) in esper.get_components(
        CInputCommand,
        CVelocity,
        CPosition,
        CSize,
        CPlayerInputSpeed,
        CTagPlayer,
    ):
        if esper.try_component(_ent, CSurface) is not None:
            continue
        ctx = CommandContext()
        for c in inp.command_queue:
            c.execute(ctx)
        dx, dy = ctx.dir_x, ctx.dir_y
        if dx != 0 and dy != 0:
            inv = 1.0 / math.sqrt(2.0)
            dx *= inv
            dy *= inv
        vel.vx = dx * speed.pixels_per_second
        vel.vy = dy * speed.pixels_per_second
        if ctx.fire_mx is not None and n_bullets < max_bullets:
            cx = pos.x + size.w / 2.0
            cy = pos.y + size.h / 2.0
            fdx = ctx.fire_mx - cx
            fdy = ctx.fire_my - cy
            dist = math.hypot(fdx, fdy)
            if dist > 1e-6:
                fdx /= dist
                fdy /= dist
                bvx = fdx * bullet_def.velocity
                bvy = fdy * bullet_def.velocity
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
