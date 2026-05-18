import math
import esper

from src.ecs.components.c_animation import AnimClip, CAnimation
from src.ecs.components.c_rotation import CRotation
from src.engine.frame_input import consume_missile
import src.engine.game_state as game_state

from src.ecs.components.c_missile_homing import CMissileHoming
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagMissileHoming, CTagPlayer
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.spawn_explosion import spawn_explosion
from src.engine.audio_util import play_sound
from src.engine.enemy_kill_score import score_for_destroyed_enemy
from src.engine.service_locator import ServiceLocator

def system_missile_launch():
    if game_state.paused:
        return
    if not consume_missile():
        return
    if not game_state.consume_homing_missile_stock():
        return

    for pent, (pos, _tp) in esper.get_components(CPosition, CTagPlayer):
        surf = esper.try_component(pent, CSurface)
        sz = esper.try_component(pent, CSize)
        if surf is not None:
            cx = pos.x + surf.area_w / 2.0
            cy = pos.y + surf.area_h / 2.0
        elif sz is not None:
            cx = pos.x + sz.w / 2.0
            cy = pos.y + sz.h / 2.0
        else:
            continue

        target = _find_nearest_enemy(cx, cy)
        missile = esper.create_entity()
        esper.add_component(missile, CPosition(cx, cy))
        esper.add_component(missile, CVelocity(0.0, 0.0))
        tex = ServiceLocator.current().get("textures").load("assets/img/missile_homing.png")
        mcs = CSurface(tex, 4)
        esper.add_component(missile, mcs)
        manim = CAnimation(
            4,
            {"FLY": AnimClip("FLY", 0, 3, 8, loops=True)},
            initial="FLY"
        )
        esper.add_component(missile, manim)
        esper.add_component(missile, CRotation(0.0))
        speed = float(game_state.get_rule("homing_missile_speed", 250.0))
        blast_radius = float(game_state.get_rule("homing_missile_blast_radius", 100.0))
        esper.add_component(missile, CMissileHoming(speed, blast_radius))
        esper.add_component(missile, CMissileHoming(speed, blast_radius))
        esper.add_component(missile, CTagMissileHoming())
        homing = esper.component_for_entity(missile, CMissileHoming)
        homing.target_ent = target
        play_sound("assets/snd/missile_trail.ogg", 0.7)
        break

def _center(ent):
    pos = esper.try_component(ent, CPosition)
    if pos is None:
        return None
    surf = esper.try_component(ent, CSurface)
    if surf is not None:
        return pos.x + surf.area_w / 2.0, pos.y + surf.area_h / 2.0
    sz = esper.try_component(ent, CSize)
    if sz is not None:
        return pos.x + sz.w / 2.0, pos.y + sz.h / 2.0
    return None


def _find_nearest_enemy(mx, my):
    best_ent = None
    best_dist = float("inf")
    for ent, _ in esper.get_component(CTagEnemy):
        c = _center(ent)
        if c is None:
            continue
        d = math.hypot(c[0] - mx, c[1] - my)
        if d < best_dist:
            best_dist = d
            best_ent = ent
    return best_ent


def _blast(cx, cy, radius):
    import random
    to_kill = []
    for ent, _ in esper.get_component(CTagEnemy):
        c = _center(ent)
        if c is None:
            continue
        if math.hypot(c[0] - cx, c[1] - cy) <= radius:
            to_kill.append((ent, c[0], c[1]))

    # Explosiones en el área aunque no haya enemigos
    for ent, ex, ey in to_kill:
        game_state.add_score(score_for_destroyed_enemy(ent))
        spawn_explosion(ex, ey)
        try:
            esper.delete_entity(ent, immediate=True)
        except KeyError:
            pass

    # Explosiones decorativas en anillo para mostrar el área
    num_ring = 6
    for i in range(num_ring):
        angle = (2 * math.pi / num_ring) * i
        rx = cx + math.cos(angle) * radius * 0.6
        ry = cy + math.sin(angle) * radius * 0.6
        spawn_explosion(rx, ry, play_spawn_sound=False)

def system_missile_homing(delta_time: float):
    if game_state.paused:
        return

    for ent, (homing, pos, vel, _tag) in esper.get_components(
        CMissileHoming, CPosition, CVelocity, CTagMissileHoming
    ):
        mx = pos.x
        my = pos.y

        # Actualizar objetivo si el anterior murió
        if homing.target_ent is None or not esper.entity_exists(homing.target_ent):
            homing.target_ent = _find_nearest_enemy(mx, my)

        if homing.target_ent is not None:
            tc = _center(homing.target_ent)
            if tc is not None:
                dx = tc[0] - mx
                dy = tc[1] - my
                dist = math.hypot(dx, dy)

                # Impacto
                if dist < 12.0:
                    _blast(tc[0], tc[1], homing.blast_radius)
                    spawn_explosion(tc[0], tc[1])
                    play_sound("assets/snd/explosion.ogg", 0.7)
                    try:
                        esper.delete_entity(ent, immediate=True)
                    except KeyError:
                        pass
                    continue

                # Dirigir hacia el objetivo
                vel.vx = (dx / dist) * homing.speed
                vel.vy = (dy / dist) * homing.speed

                rot = esper.try_component(ent, CRotation)
                if rot is not None:
                    rot.angle = math.degrees(math.atan2(dy, dx))