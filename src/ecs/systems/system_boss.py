import math
import random
import esper
import pygame

from src.ecs.components.c_particle import CParticle
from src.ecs.components.c_shockwave import CShockwave
import src.engine.game_state as game_state
from src.ecs.components.c_boss import CBoss
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_tags import CTagBoss, CTagPlayer, CTagBullet
from src.engine.audio_util import play_sound
from src.ecs.systems.collision_util import get_entity_dims, aabb_overlap
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.engine.service_locator import ServiceLocator


def _boss_center(pos, surf):
    return pos.x + surf.area_w / 2.0, pos.y + surf.area_h / 2.0


def _random_border_pos(screen_w, screen_h, boss_w, boss_h):
    return random.uniform(0, screen_w - boss_w), 90.0


def _update_boss_frame(boss_ent, boss):
    anim = esper.try_component(boss_ent, CAnimation)
    if anim is None:
        return

    surf = esper.try_component(boss_ent, CSurface)
    if surf is None:
        return

    max_health = int(game_state.get_rule("boss_health", 10))
    total_frames = anim.number_frames - 1

    damage_ratio = 1.0 - (max(0, boss.health) / max_health)
    anim.current_frame = int(damage_ratio * total_frames)


def system_boss_update(delta_time: float, screen_w: int, screen_h: int):
    if game_state.paused:
        return

    for ent, (boss, pos, surf) in esper.get_components(
        CBoss,
        CPosition,
        CSurface
    ):
        boss.state_timer += delta_time

        if boss.state == CBoss.IDLE:
            if boss.state_timer >= boss.teleport_interval:
                boss.state = CBoss.CHARGING
                boss.state_timer = 0.0
                boss.ray_angle = 90.0

                if boss.sound_charge:
                    snd = ServiceLocator.current().get("sounds").load(
                        boss.sound_charge
                    )
                    boss._charge_sound_channel = snd.play()

        elif boss.state == CBoss.CHARGING:
            if boss.state_timer >= boss.ray_charge_sec:
                boss.state = CBoss.FIRING
                boss.state_timer = 0.0

                if boss.sound_ray:
                    snd = ServiceLocator.current().get("sounds").load(
                        boss.sound_ray
                    )
                    boss._ray_sound_channel = snd.play()

        elif boss.state == CBoss.FIRING:
            _check_ray_player_hit(
                boss,
                pos,
                surf,
                screen_w,
                screen_h
            )

            if boss.state_timer >= boss.ray_duration_sec:
                boss.state = CBoss.TELEPORTING
                boss.state_timer = 0.0

                if boss._ray_sound_channel:
                    boss._ray_sound_channel.fadeout(500)
                    boss._ray_sound_channel = None

        elif boss.state == CBoss.TELEPORTING:
            if boss.state_timer >= 0.3:
                bw = float(surf.area_w)
                bh = float(surf.area_h)

                old_x = pos.x + bw / 2.0
                old_y = pos.y + bh / 2.0

                system_boss_particles(old_x, old_y, bw, bh)

                nx, ny = _random_border_pos(
                    screen_w,
                    screen_h,
                    bw,
                    bh
                )

                pos.x = nx
                pos.y = ny

                new_x = pos.x + bw / 2.0
                new_y = pos.y + bh / 2.0

                system_boss_particles(new_x, new_y, bw, bh)

                boss.state = CBoss.IDLE
                boss.state_timer = 0.0

                if boss.sound_teleport:
                    play_sound(boss.sound_teleport, 0.6)


def _check_ray_player_hit(
    boss,
    boss_pos,
    boss_surf,
    screen_w,
    screen_h
):
    cx, cy = _boss_center(boss_pos, boss_surf)

    angle_rad = math.radians(boss.ray_angle)

    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    for pent, (ppos, _tp) in esper.get_components(
        CPosition,
        CTagPlayer
    ):
        psurf = esper.try_component(pent, CSurface)

        if psurf:
            pw = psurf.area_w
            ph = psurf.area_h
        else:
            from src.ecs.components.c_size import CSize

            sz = esper.try_component(pent, CSize)

            pw = sz.w if sz else 16
            ph = sz.h if sz else 16

        pcx = ppos.x + pw / 2.0
        pcy = ppos.y + ph / 2.0

        t = (pcx - cx) * dx + (pcy - cy) * dy

        closest_x = cx + dx * max(0, t)
        closest_y = cy + dy * max(0, t)

        dist = math.hypot(
            pcx - closest_x,
            pcy - closest_y
        )

        if dist < max(pw, ph) / 2.0 + 4.0:
            if boss._ray_sound_channel is not None:
                boss._ray_sound_channel.fadeout(500)
                boss._ray_sound_channel = None
            game_state.lose_life()

def system_boss_draw(
    surface: pygame.Surface,
    screen_w: int,
    screen_h: int
):
    for ent, (boss, pos, surf) in esper.get_components(
        CBoss,
        CPosition,
        CSurface
    ):
        if boss.state not in (CBoss.CHARGING, CBoss.FIRING):
            continue

        cx = (pos.x + surf.area_w / 2.0) - 0.5
        cy = pos.y + surf.area_h + 10.0

        angle_rad = math.radians(boss.ray_angle)

        ray_len = math.hypot(screen_w, screen_h)

        ex = cx + math.cos(angle_rad) * ray_len
        ey = cy + math.sin(angle_rad) * ray_len

        if boss.state == CBoss.CHARGING:
            progress = min(
                1.0,
                boss.state_timer / boss.ray_charge_sec
            )

            for width, base_alpha in [(3, 80), (1, 200)]:
                alpha = int(base_alpha * progress)

                ray_surf = pygame.Surface(
                    (screen_w, screen_h),
                    pygame.SRCALPHA
                )

                pygame.draw.line(
                    ray_surf,
                    (255, 0, 0, alpha),
                    (int(cx), int(cy)),
                    (int(ex), int(ey)),
                    width
                )

                surface.blit(ray_surf, (0, 0))

        else:
            progress = min(
                1.0,
                boss.state_timer / 0.3
            )

            for width, base_alpha in [
                (16, 40),
                (10, 100),
                (6, 200),
                (3, 255)
            ]:
                alpha = int(base_alpha * progress)

                ray_surf = pygame.Surface(
                    (screen_w, screen_h),
                    pygame.SRCALPHA
                )

                pygame.draw.line(
                    ray_surf,
                    (180, 0, 255, alpha),
                    (int(cx), int(cy)),
                    (int(ex), int(ey)),
                    width
                )

                surface.blit(ray_surf, (0, 0))


def system_boss_bullet_collision():
    for boss_ent, (boss, boss_pos, boss_surf) in esper.get_components(
        CBoss,
        CPosition,
        CSurface
    ):
        bw, bh = get_entity_dims(boss_ent)

        if bw == 0:
            bw = float(boss_surf.area_w)
            bh = float(boss_surf.area_h)

        for b_ent, (b_pos, _tb) in esper.get_components(
            CPosition,
            CTagBullet
        ):
            from src.ecs.components.c_tags import CTagEnemyBullet

            if esper.try_component(b_ent, CTagEnemyBullet) is not None:
                continue

            bul_w, bul_h = get_entity_dims(b_ent)

            if not aabb_overlap(
                b_pos.x,
                b_pos.y,
                bul_w,
                bul_h,
                boss_pos.x,
                boss_pos.y,
                bw,
                bh
            ):
                continue

            boss.health -= 1

            spawn_explosion(
                boss_pos.x + bw / 2.0,
                boss_pos.y + bh / 2.0
            )

            _update_boss_frame(boss_ent, boss)

            try:
                esper.delete_entity(b_ent, immediate=True)
            except KeyError:
                pass

            if boss.health <= 0:
                bx = boss_pos.x + bw / 2.0
                by = boss_pos.y + bh / 2.0

                snd = ServiceLocator.current().get("sounds").load(
                    "assets/snd/explosion_boss.ogg"
                )

                snd.play()

                if boss._ray_sound_channel:
                    boss._ray_sound_channel.fadeout(300)
                    boss._ray_sound_channel = None

                if boss._charge_sound_channel:
                    boss._charge_sound_channel.stop()

                spawn_explosion(bx, by)

                for i in range(8):
                    angle = (2 * math.pi / 8) * i

                    rx = bx + math.cos(angle) * bw * 0.6
                    ry = by + math.sin(angle) * bh * 0.6

                    spawn_explosion(rx, ry)

                system_boss_particles(bx, by, bw, bh)

                sw = esper.create_entity()

                esper.add_component(sw, CPosition(bx, by))

                esper.add_component(
                    sw,
                    CShockwave(
                        max_radius=bw * 2.0,
                        lifetime=0.6,
                        r=255,
                        g=100,
                        b=0
                    )
                )

                try:
                    esper.delete_entity(
                        boss_ent,
                        immediate=True
                    )
                except KeyError:
                    pass


def system_boss_particles(bx, by, bw, bh):
    for _ in range(20):
        angle = random.uniform(0, 2 * math.pi)

        speed = random.uniform(30.0, 150.0)

        trail = esper.create_entity()

        esper.add_component(
            trail,
            CPosition(
                bx + math.cos(angle) * random.uniform(0, bw * 0.5),
                by + math.sin(angle) * random.uniform(0, bh * 0.5)
            )
        )

        esper.add_component(
            trail,
            CParticle(
                lifetime=random.uniform(0.5, 1.2),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                r=random.choice([255, 220, 200]),
                g=random.randint(50, 120),
                b=20,
                size=random.uniform(2.0, 5.0)
            )
        )
