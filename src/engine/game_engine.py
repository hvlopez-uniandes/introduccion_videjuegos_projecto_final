from pathlib import Path
import random

import esper
import pygame

from src.engine.config import (
    build_bullet_def,
    build_enemy_spawner_component,
    build_enemy_type_defs,
    build_explosion_config,
    build_game_rules,
    build_player_config,
    load_interface_config,
    load_special_shield_config,
    populate_astronaut_entities,
    load_world_bundle,
    load_window_config,
)
from src.engine.game_state import set_paused
import src.engine.game_state as game_state
from src.engine.frame_input import request_hyperspace, request_shield_pulse, request_smart_bomb
from src.engine.input_keys import pygame_key_from_string
from src.engine.paths import set_project_root
from src.engine.resource_services import FontService, SoundService, TextureService
from src.engine.service_locator import ServiceLocator
from src.engine.textures import clear_texture_cache
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_arcade_defender_flight import CArcadeDefenderFlight
from src.ecs.components.c_player_arcade_burner import CPlayerArcadeBurner
from src.ecs.components.c_color import CColor
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_input_speed import CPlayerInputSpeed
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_shield_special import CShieldSpecial
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import (
    CTagEnemy,
    CTagHud,
    CTagHudDynamic,
    CTagLander,
    CTagMutant,
    CTagPlayer,
)
from src.ecs.components.c_lander_ai import CLanderAI
from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_ui_text_style import CUiTextStyle
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.system_arcade_baiter_spawn import system_arcade_baiter_spawn
from src.ecs.systems.system_arcade_hyperspace import system_arcade_hyperspace
from src.ecs.systems.system_arcade_smart_bomb import system_arcade_smart_bomb
from src.ecs.systems.system_arcade_wave_time import system_arcade_wave_time
from src.ecs.systems.system_animation import system_animation
from src.ecs.systems.system_bounce import system_bounce
from src.ecs.systems.system_astronaut_carried_sync import system_astronaut_carried_sync
from src.ecs.systems.system_astronaut_gravity_and_land import (
    system_astronaut_gravity,
    system_astronaut_landing_resolve,
)
from src.ecs.systems.system_astronaut_rescue_ship import (
    system_astronaut_rescue_deposit,
    system_astronaut_rescue_pickup,
)
from src.ecs.systems.system_bullet_bounds import system_bullet_bounds
from src.ecs.systems.system_astronaut_snap import system_astronaut_terrain_snap
from src.ecs.systems.system_collision_bullet_astronaut import system_collision_bullet_astronaut
from src.ecs.systems.system_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.system_collision_bullet_enemy_bullet import system_collision_bullet_enemy_bullet
from src.ecs.systems.system_collision_enemy_bullet_player import system_collision_enemy_bullet_player
from src.ecs.systems.system_bomber_drop_bombs import system_bomber_drop_bombs
from src.ecs.systems.system_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.system_defense_arcade_transition import system_defense_arcade_transition
from src.ecs.systems.system_draw_radar_defender import system_draw_radar_defender
from src.ecs.systems.system_draw import system_draw
from src.ecs.systems.system_draw_shield_ring import system_draw_shield_ring
from src.ecs.systems.system_enemy_spawner import system_enemy_spawner
from src.ecs.systems.system_execute_commands import system_execute_commands
from src.ecs.systems.system_explosion_cleanup import system_explosion_cleanup
from src.ecs.systems.system_hunter_ai import system_hunter_ai
from src.ecs.systems.system_hunter_animation import system_hunter_animation
from src.ecs.systems.system_lander_ai import system_lander_ai
from src.ecs.systems.system_lander_mutation import system_lander_mutate_to_alien
from src.ecs.systems.system_mutant_missile import system_mutant_missile
from src.ecs.systems.system_input_command import system_input_command
from src.ecs.systems.system_level_progress import system_level_progress
from src.ecs.systems.system_movement import system_movement
from src.ecs.systems.system_player_animation import system_player_animation
from src.ecs.systems.system_camera_follow import system_camera_follow
from src.ecs.systems.system_player_bounds import system_player_bounds
from src.ecs.systems.system_player_terrain_occlusion import system_player_terrain_occlusion
from src.ecs.systems.system_player_move_sound import system_player_move_sound
from src.ecs.systems.system_shield_hud_refresh import system_shield_hud_refresh
from src.ecs.systems.system_shield_pulse import system_shield_pulse
from src.ecs.systems.system_scenario_draw import system_scenario_draw
from src.ecs.systems.system_scenario_update import system_scenario_update
from src.ecs.systems.system_world_wrap import system_world_wrap
from src.engine.scenario_factory import create_scenario_entities
from src.engine.frame_input import request_hyperspace, request_shield_pulse, request_smart_bomb, request_missile
from src.ecs.systems.system_missile_homing import system_missile_homing
from src.ecs.systems.system_missile_homing import system_missile_homing, system_missile_launch
from src.ecs.systems.system_hyperspace_effect import system_hyperspace_effect
from src.ecs.systems.system_shockwave import system_shockwave

def _clamp_byte(n):
    n = int(n)
    return max(0, min(255, n))


class GameEngine:
    _MENU_LOGO_REL = "assets/img/game_logo.png"
    # `world.json` play_area_* se diseña para esta altura lógica (clásico ~256 px).
    _PLAY_AREA_REFERENCE_WORLD_H = 256

    def __init__(self, cfg_dir=None):
        self._root = Path(__file__).resolve().parents[2]
        if cfg_dir is None:
            self._cfg_dir = self._root / "assets" / "cfg"
        else:
            self._cfg_dir = Path(cfg_dir)
            if not self._cfg_dir.is_absolute():
                self._cfg_dir = (self._root / self._cfg_dir).resolve()

        self.is_running = False
        self.delta_time = 0.0

        self.screen = None
        self.clock = None
        self.framerate = 60
        self.bg_color = (0, 0, 0)
        self.screen_w = 640
        self.screen_h = 360

        self._iface = None
        self._shield_key = pygame.K_SPACE
        self._pause_text = "PAUSED"
        self._pause_font_size = 28
        self._pause_color = (255, 220, 80)
        self._pygame_started = False
        self._menu_font_hint = None
        self._hud_font = None
        self._menu_player_cfg = {}
        self._menu_logo_cache_key = None
        self._menu_logo_cache_surf = None
        self._hud_instructions_ent = None
        self._hud_arcade_strip_ent = None

    def _layout_play_hints_corner(self) -> None:
        """Última línea de ayuda y franja HUD dinámica (bombas / escudo) abajo derecha."""
        margin_x = max(14, int(self.screen_w * 0.018))
        margin_y = max(12, int(self.screen_h * 0.02))
        rx = float(self.screen_w) - float(margin_x)
        radar_reserve = 20.0 if game_state.arcade_defender_flight else 0.0
        dy = float(self.screen_h) - float(margin_y) - radar_reserve

        dyn = self._hud_arcade_strip_ent
        if dyn is None or not esper.entity_exists(dyn):
            return
        p_d = esper.try_component(dyn, CPosition)
        s_d = esper.try_component(dyn, CSurface)
        if p_d is None or s_d is None:
            return

        if game_state.arcade_defender_flight:
            ins = self._hud_instructions_ent
            if ins is None or not esper.entity_exists(ins):
                p_d.x = rx - float(s_d.area_w)
                p_d.y = dy - float(s_d.area_h)
                return
            p_i = esper.try_component(ins, CPosition)
            s_i = esper.try_component(ins, CSurface)
            if p_i is None or s_i is None:
                return
            gap = max(8.0, float(margin_y) * 0.55)
            p_i.x = rx - float(s_i.area_w)
            p_i.y = dy - float(s_i.area_h)
            p_d.x = rx - float(s_d.area_w)
            p_d.y = p_i.y - gap - float(s_d.area_h)
        else:
            p_d.x = rx - float(s_d.area_w)
            p_d.y = dy - float(s_d.area_h)

    def _menu_logo_surface(self):
        w, h = self.screen_w, self.screen_h
        key = (w, h)
        if self._menu_logo_cache_key == key and self._menu_logo_cache_surf is not None:
            return self._menu_logo_cache_surf
        try:
            raw = ServiceLocator.current().get("textures").load(self._MENU_LOGO_REL)
        except (FileNotFoundError, pygame.error, OSError):
            self._menu_logo_cache_key = key
            self._menu_logo_cache_surf = None
            return None
        rw, rh = raw.get_size()
        if rw <= 0 or rh <= 0:
            self._menu_logo_cache_key = key
            self._menu_logo_cache_surf = None
            return None
        target_w = int(min(max(220, int(w * 0.52)), rw * 6))
        target_h = max(1, int(rh * target_w / float(rw)))
        max_logo_h = int(h * 0.24)
        if target_h > max_logo_h:
            target_h = max_logo_h
            target_w = max(1, int(rw * target_h / float(rh)))
        scaled = pygame.transform.smoothscale(raw, (target_w, target_h))
        self._menu_logo_cache_key = key
        self._menu_logo_cache_surf = scaled
        return scaled

    def _menu_pick_font_for_overlay(self, logo_h: int):
        """Fuente que cabe el ancho y, si hace falta, el alto disponible sobre el relieve."""
        w, h = self.screen.get_size()
        margin = max(24, min(64, int(w * 0.05)))
        max_w_px = max(100, int(w - 2 * margin))

        arcade = isinstance(self._menu_player_cfg, dict) and bool(
            self._menu_player_cfg.get("arcade_defender_flight")
        )
        if arcade:
            hint_lines = [
                "Arcade: ↑↓ ←→ empuje(X) invertir(C)",
                "láser(Z) bomba(ESP) hiper(H) P pausa",
            ]
        else:
            hint_lines = [
                "Flechas · Z/CTRL disparo",
                "ESP pulso · P pausa",
            ]

        width_probe = list(
            {
                "Proyecto MISW · curso vídeojuegos",
                "ENTER / ESPACIO — jugar",
                "DEFENDER — Proyecto curso",
                *hint_lines,
            }
        )

        font_path = str(self._iface["font"])
        svc = ServiceLocator.current().get("fonts")
        inst = max(8, int(self._iface["instructions"].get("size", 8)))
        max_try = max(28, min(48, inst + 24, int(min(w, h) * 0.045)))

        def fits_width(cand_font) -> bool:
            return all(cand_font.size(str(s))[0] <= max_w_px for s in width_probe)

        def stack_height_px(cand_font) -> int:
            line = cand_font.get_linesize()
            small_gap = max(10, line // 6)
            n_txt = 2 + len(hint_lines)
            text_block = n_txt * line + max(0, n_txt - 1) * small_gap
            return int(small_gap + logo_h + small_gap + text_block + small_gap)

        content_bottom = int(h * 0.58)
        avail_h = max(220, content_bottom - int(h * 0.035))

        picked = svc.get(font_path, 8)
        for size_px in range(max_try, 7, -1):
            cand = svc.get(font_path, size_px)
            if not fits_width(cand):
                continue
            picked = cand
            if stack_height_px(cand) <= avail_h:
                break
        text_gap = max(14, picked.get_linesize() // 4)
        return picked, hint_lines, text_gap

    def run(self):
        pygame.init()
        pygame.mixer.init()
        set_project_root(self._root)
        self._pygame_started = True
        self._bind_services()
        game_state.load_high_score_from_disk()

        title, w, h, self.bg_color, self.framerate, fullscreen = load_window_config(self._cfg_dir)
        pygame.display.set_caption(title)
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((w, h))
        self.screen_w, self.screen_h = self.screen.get_size()
        self.clock = pygame.time.Clock()

        iface = load_interface_config(self._cfg_dir)
        self._iface = iface
        fonts = ServiceLocator.current().get("fonts")
        self._menu_font_hint = fonts.get(iface["font"], max(16, iface["instructions"].get("size", 8) + 2))
        self._hud_font = fonts.get(iface["font"], max(11, iface["title"]["size"]))
        self._menu_player_cfg = build_player_config(self._cfg_dir)
        pause = iface.get("pause", {})
        self._pause_text = str(pause.get("text", "PAUSED"))
        self._pause_font_size = int(pause.get("size", 28))

        pc = pause.get("color", {})
        self._pause_color = (
            _clamp_byte(pc.get("r", 255)),
            _clamp_byte(pc.get("g", 220)),
            _clamp_byte(pc.get("b", 80)),
        )

        game_state.return_to_menu()
        self.is_running = True

        while self.is_running:
            self._calculate_time()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    ek = event.key
                    ph = game_state.game_phase

                    if ph == "menu" and ek in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state.reset_session_for_new_level()
                        game_state.begin_play_after_menu()
                        self._reload_play_world()
                    elif ph in ("game_over", "victory") and ek in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                        pygame.K_ESCAPE,
                    ):
                        game_state.return_to_menu()
                        self._reset_ecs_menu_backdrop()
                    elif ph == "play":
                        if ek == pygame.K_p:
                            game_state.toggle_pause()
                        elif ek == pygame.K_ESCAPE:
                            game_state.toggle_pause()
                        elif ek == pygame.K_h:
                            if game_state.arcade_defender_flight:
                                request_hyperspace()
                        elif ek == self._shield_key:
                            if game_state.arcade_defender_flight:
                                request_smart_bomb()
                            else:
                                request_shield_pulse()
                        elif ek == pygame.K_f:
                            request_missile()

            ph = game_state.game_phase if self.is_running else "menu"

            if ph == "menu":
                self._draw_main_menu_overlay()
                pygame.display.flip()
                continue

            if ph in ("game_over", "victory"):
                system_scenario_update(self.delta_time)
                system_animation(self.delta_time)
                self.screen.fill(self.bg_color)
                system_scenario_draw(self.screen)
                system_draw(self.screen)
                system_draw_shield_ring(self.screen)
                self._draw_end_state_banner(ph == "victory")
                pygame.display.flip()
                continue

            if ph != "play":
                pygame.display.flip()
                continue

            self._fanfare_maybe()

            if game_state.paused:
                system_scenario_update(self.delta_time)
                self._update_play_always_background()
                self._draw_play()
                self._draw_pause_overlay()
                pygame.display.flip()
                continue

            self._update_play()
            system_level_progress()

            self._draw_play()
            pygame.display.flip()

        game_state.record_high_score_if_best(game_state.score)
        pygame.quit()

    def _apply_scaled_play_area(self, world_cfg, screen_h: int) -> None:
        """Escala play_area del JSON (referencia 256 px) a la altura real de la ventana."""
        top_px = getattr(world_cfg, "play_area_top_px", None)
        bottom_px = getattr(world_cfg, "play_area_bottom_px", None)
        rh = max(1, int(GameEngine._PLAY_AREA_REFERENCE_WORLD_H))
        hh = max(1, int(screen_h))
        if top_px is None and bottom_px is None:
            game_state.set_play_area_vertical(None, None)
            return
        scale = hh / float(rh)
        st = None if top_px is None else int(round(float(top_px) * scale))
        sb = None if bottom_px is None else int(round(float(bottom_px) * scale))
        if st is not None:
            st = max(0, min(st, hh - 2))
        if sb is not None:
            sb = max(2, min(sb, hh - 8))
            if st is not None and sb <= st:
                sb = min(hh - 8, st + max(64, hh // 3))
        game_state.set_play_area_vertical(st, sb)

    def _reset_ecs_menu_backdrop(self) -> None:
        """Quita entidades de partida para que el menú no dibuje niveles GAME OVER como pausa."""
        esper.clear_database()
        self._hud_instructions_ent = None
        self._hud_arcade_strip_ent = None
        _world_cfg, sc_seed = load_world_bundle(self._cfg_dir)
        create_scenario_entities(random.Random(int(sc_seed)), _world_cfg, self.screen_w, self.screen_h)
        self._apply_scaled_play_area(_world_cfg, self.screen_h)
        game_state.set_world_metrics(self.screen_w, self.screen_h)

    def _reload_play_world(self):
        """Reconstruye ECS de partida tras menú o reinicio."""
        if self._iface is None:
            self._iface = load_interface_config(self._cfg_dir)
        clear_texture_cache()
        self._menu_logo_cache_key = None
        self._menu_logo_cache_surf = None
        esper.clear_database()
        rule_block = build_game_rules(self._cfg_dir)
        game_state.set_rules(rule_block)
        self._shield_key = pygame_key_from_string(load_special_shield_config(self._cfg_dir).get("activation_key", "SPACE"))

        w, h = self.screen_w, self.screen_h
        _world_cfg, sc_seed = load_world_bundle(self._cfg_dir)
        self._scenario_seed = sc_seed
        create_scenario_entities(random.Random(int(sc_seed)), _world_cfg, w, h)
        self._apply_scaled_play_area(_world_cfg, h)
        game_state.set_world_metrics(w, h)
        game_state.play_screen_h_int = int(h)
        game_state.scenario_space_skirmish = False
        game_state.planet_explosion_flash_remaining = 0.0
        game_state.smart_bomb_flash_remaining = 0.0
        populate_astronaut_entities(self._cfg_dir, h)

        enemy_types = build_enemy_type_defs(self._cfg_dir)
        spawner_component = build_enemy_spawner_component(self._cfg_dir, enemy_types, h)
        spawn_sy = float(h) / float(GameEngine._PLAY_AREA_REFERENCE_WORLD_H)
        scaled_spawn_y = float(spawner_component.player_spawn_y) * spawn_sy
        game_state.set_spawn(spawner_component.player_spawn_x, scaled_spawn_y)
        bullet_def = build_bullet_def(self._cfg_dir)
        player_cfg = build_player_config(self._cfg_dir)
        arcade_on = bool(player_cfg.get("arcade_defender_flight"))
        game_state.set_arcade_defender_flight(arcade_on)
        explosion_cfg = build_explosion_config(self._cfg_dir)
        shield_cfg = load_special_shield_config(self._cfg_dir)

        entity_spawner = esper.create_entity()
        esper.add_component(entity_spawner, spawner_component)
        esper.add_component(entity_spawner, bullet_def)
        esper.add_component(entity_spawner, explosion_cfg)

        player_entity = esper.create_entity()
        esper.add_component(player_entity, CPosition(spawner_component.player_spawn_x, scaled_spawn_y))
        esper.add_component(player_entity, CVelocity(0.0, 0.0))
        esper.add_component(player_entity, CInputCommand())
        esper.add_component(
            player_entity,
            CPlayerInputSpeed(
                player_cfg["input_velocity"],
                float(player_cfg.get("motion_smoothing_hz", 20.0)),
            ),
        )
        esper.add_component(player_entity, CTagPlayer())
        esper.add_component(
            player_entity,
            CPlayerSfx(
                player_cfg.get("sound_move") or "",
                player_cfg.get("sound_collision") or "",
            ),
        )
        if not arcade_on:
            esper.add_component(
                player_entity,
                CShieldSpecial(
                    shield_cfg["duration_sec"],
                    shield_cfg["cooldown_sec"],
                    shield_cfg["radius_px"],
                    self._shield_key,
                ),
            )
        else:
            esper.add_component(
                player_entity,
                CArcadeDefenderFlight(
                    facing=1,
                    thrust_accel_px_s2=float(game_state.get_rule("arcade_thrust_accel_px_s2", 420.0)),
                    drag_per_s=float(game_state.get_rule("arcade_drag_per_s", 0.72)),
                    max_speed_x=float(game_state.get_rule("arcade_max_speed_x", 220.0)),
                    vertical_speed_px_s=float(game_state.get_rule("arcade_vertical_speed_px_s", 150.0)),
                ),
            )

        if (
            arcade_on
            and player_cfg.get("sprite")
            and player_cfg.get("burner_idle_image")
            and player_cfg.get("burner_moving_image")
        ):
            tex = ServiceLocator.current().get("textures")
            bi = tex.load(player_cfg["burner_idle_image"])
            bm = tex.load(player_cfg["burner_moving_image"])
            ni = max(1, int(player_cfg.get("burner_idle_frames", 3)))
            nm = max(1, int(player_cfg.get("burner_moving_frames", 3)))
            esper.add_component(
                player_entity,
                CPlayerArcadeBurner(
                    CSurface(bi, ni),
                    CSurface(bm, nm),
                    anim_hz=float(player_cfg.get("burner_anim_hz", 12.0)),
                    tuck_px=float(player_cfg.get("burner_tuck_px", 3.0)),
                ),
            )

        if player_cfg.get("sprite"):
            psurf = ServiceLocator.current().get("textures").load(player_cfg["image"])
            pcs = CSurface(psurf, player_cfg["number_frames"])
            panim = CAnimation(player_cfg["number_frames"], player_cfg["clips"], initial="IDLE")
            esper.add_component(player_entity, pcs)
            esper.add_component(player_entity, panim)
        else:
            esper.add_component(player_entity, CSize(player_cfg["w"], player_cfg["h"]))
            esper.add_component(
                player_entity,
                CColor(player_cfg["r"], player_cfg["g"], player_cfg["b"]),
            )

        self._setup_interface_entities()
        set_paused(False)

    def _setup_interface_entities(self):
        iface = self._iface
        fonts = ServiceLocator.current().get("fonts")
        font_path = iface["font"]

        def _rgb(block):
            c = block.get("color", {})
            return _clamp_byte(c.get("r", 255)), _clamp_byte(c.get("g", 255)), _clamp_byte(c.get("b", 255))

        title = iface["title"]
        pos = title["position"]
        f = fonts.get(font_path, int(title["size"]))
        rgb = _rgb(title)
        surf = CSurface.from_text(f, str(title["text"]), rgb, False)
        e = esper.create_entity()
        esper.add_component(e, CPosition(float(pos["x"]), float(pos["y"])))
        esper.add_component(e, surf)
        esper.add_component(e, CTagHud())

        ins = iface["instructions"]
        p = ins["position"]
        f2 = fonts.get(font_path, int(ins["size"]))
        rgb2 = _rgb(ins)
        surf2 = CSurface.from_text(f2, str(ins["text"]), rgb2, False)
        e2 = esper.create_entity()
        esper.add_component(e2, CPosition(float(p["x"]), float(p["y"])))
        esper.add_component(e2, surf2)
        esper.add_component(e2, CTagHud())

        sh = iface["shield_status"]
        sp = sh["position"]
        f3 = fonts.get(font_path, int(sh["size"]))
        rgb3 = _rgb(sh)
        init = "Pulso: --"
        surf3 = CSurface.from_text(f3, init, rgb3, False)
        e3 = esper.create_entity()
        esper.add_component(e3, CPosition(float(sp["x"]), float(sp["y"])))
        esper.add_component(e3, surf3)
        esper.add_component(
            e3,
            CUiTextStyle(
                font_path,
                int(sh["size"]),
                rgb3[0],
                rgb3[1],
                rgb3[2],
                False,
            ),
        )
        esper.add_component(e3, CTagHudDynamic())
        self._hud_instructions_ent = e2
        self._hud_arcade_strip_ent = e3

    def _bind_services(self):
        loc = ServiceLocator()
        loc.register("textures", TextureService(self._root))
        loc.register("sounds", SoundService(self._root))
        loc.register("fonts", FontService(self._root))
        ServiceLocator.bind(loc)

    def _calculate_time(self):
        ms = self.clock.tick(self.framerate)
        self.delta_time = ms / 1000.0
        game_state.tick_session(self.delta_time)

    def _update_play_always_background(self):
        system_explosion_cleanup()
        system_shield_hud_refresh()
        self._layout_play_hints_corner()

    def _update_play(self):
        game_state.tick_dt = self.delta_time
        system_scenario_update(self.delta_time)
        system_input_command()
        system_execute_commands()
        system_arcade_hyperspace()
        system_arcade_smart_bomb()
        system_enemy_spawner(self.delta_time)
        system_arcade_wave_time(self.delta_time)
        system_arcade_baiter_spawn()
        system_hunter_ai()
        system_mutant_missile(self.delta_time)
        system_lander_ai(self.delta_time)
        system_astronaut_gravity(self.delta_time)
        system_movement(self.delta_time)
        system_bomber_drop_bombs(self.delta_time)
        system_astronaut_rescue_pickup()
        system_astronaut_carried_sync()
        system_astronaut_landing_resolve()
        system_lander_mutate_to_alien()
        system_astronaut_terrain_snap(self.delta_time)
        system_astronaut_rescue_deposit()
        system_world_wrap(self.screen_w, self.screen_h)
        system_player_bounds(self.screen_w, self.screen_h)
        system_camera_follow()
        system_player_terrain_occlusion()
        system_bounce(self.screen_w, self.screen_h)
        system_bullet_bounds(self.screen_w, self.screen_h)
        system_animation(self.delta_time)
        system_player_animation()
        system_hunter_animation()
        system_shield_pulse(self.delta_time)
        system_missile_launch()
        system_missile_homing(self.delta_time)
        system_missile_homing(self.delta_time)
        system_collision_bullet_enemy_bullet()
        system_collision_bullet_enemy()
        system_collision_bullet_astronaut()
        system_collision_player_enemy()
        system_collision_enemy_bullet_player()
        system_defense_arcade_transition()
        system_explosion_cleanup()
        system_player_move_sound()
        system_shield_hud_refresh()
        system_hyperspace_effect(self.delta_time)
        self._layout_play_hints_corner()
        if game_state.planet_explosion_flash_remaining > 0.0:
            game_state.planet_explosion_flash_remaining = max(
                0.0,
                float(game_state.planet_explosion_flash_remaining) - float(self.delta_time),
            )
        if float(getattr(game_state, "smart_bomb_flash_remaining", 0.0) or 0.0) > 0.0:
            game_state.smart_bomb_flash_remaining = max(
                0.0,
                float(game_state.smart_bomb_flash_remaining) - float(self.delta_time),
            )

    def _draw_play(self):
        self.screen.fill(self.bg_color)
        system_scenario_draw(self.screen)
        system_draw(self.screen)
        system_shockwave(self.delta_time, self.screen)
        system_draw_shield_ring(self.screen)
        self._draw_flash_overlay(
            "planet_explosion_flash_remaining",
            "planet_explosion_flash_sec",
            2.2,
            0.2,
            (218, 38, 52),
            (25, 50, 30),
            45,
            205,
            235,
            pulse_factor=1.15,
        )
        self._draw_flash_overlay(
            "smart_bomb_flash_remaining",
            "smart_bomb_flash_sec",
            0.42,
            0.08,
            (180, 240, 255),
            (40, 15, 0),
            40,
            170,
            220,
            stripes=True,
        )
        system_draw_radar_defender(self.screen)
        self._draw_play_hud()

    def _draw_flash_overlay(
        self,
        state_attr: str,
        rule_key: str,
        default_sec: float,
        min_sec: float,
        base_rgb: tuple[int, int, int],
        pulse_add: tuple[int, int, int],
        alpha_base: int,
        alpha_add: int,
        alpha_max: int,
        pulse_factor: float = 1.0,
        stripes: bool = False,
    ) -> None:
        t = float(getattr(game_state, state_attr, 0.0) or 0.0)
        if t <= 0.0:
            return
        w, h = self.screen.get_size()
        max_t = float(game_state.get_rule(rule_key, default_sec))
        max_t = max(min_sec, max_t)
        pulse = min(1.0, (t / max_t) * pulse_factor)
        alpha = int(min(alpha_max, alpha_base + int(alpha_add * pulse)))
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill(
            (
                min(255, int(base_rgb[0] + pulse_add[0] * pulse)),
                min(255, int(base_rgb[1] + pulse_add[1] * pulse)),
                min(255, int(base_rgb[2] + pulse_add[2] * pulse)),
                alpha,
            )
        )
        if stripes:
            band_h = max(2, h // 80)
            stripe_a = min(90, int(50 + 40 * pulse))
            for i in range(0, h, band_h * 3):
                pygame.draw.rect(ov, (255, 255, 255, stripe_a), (0, i, w, band_h))
        self.screen.blit(ov, (0, 0))

    def _draw_pause_overlay(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        if not game_state.pause_overlay_visible():
            return
        font = ServiceLocator.current().get("fonts").get(self._iface["font"], self._pause_font_size)
        surf = font.render(self._pause_text, False, self._pause_color)
        rect = surf.get_rect(center=(w // 2, h // 2))
        self.screen.blit(surf, rect)

    def _draw_main_menu_overlay(self):
        self.screen.fill(self.bg_color)
        system_scenario_draw(self.screen)
        system_draw(self.screen)
        if self._iface is None:
            return
        w, h = self.screen.get_size()
        logo = self._menu_logo_surface()
        logo_h = logo.get_height() if logo is not None else 0
        f, hint_lines, text_gap = self._menu_pick_font_for_overlay(logo_h)

        line_h = f.get_linesize()
        n_txt = 2 + len(hint_lines)
        small_gap = max(10, line_h // 6)
        stack_h = small_gap + logo_h + small_gap + n_txt * line_h + max(0, n_txt - 1) * small_gap
        top_m = max(24, int(h * 0.035))
        bottom_m = int(h * 0.58)
        y = top_m + max(0, (bottom_m - top_m - stack_h) // 2)

        if logo is not None:
            lr = logo.get_rect(midtop=(w // 2, y))
            self.screen.blit(logo, lr)
            y = lr.bottom + text_gap
        else:
            t_fb = f.render("DEFENDER — Proyecto curso", False, (255, 240, 120))
            br = t_fb.get_rect(midtop=(w // 2, y))
            self.screen.blit(t_fb, br)
            y = br.bottom + text_gap

        for text, rgb in (
            ("Proyecto MISW · curso vídeojuegos", (230, 220, 150)),
            ("ENTER / ESPACIO — jugar", (220, 220, 255)),
        ):
            surf = f.render(text, False, rgb)
            r = surf.get_rect(midtop=(w // 2, y))
            self.screen.blit(surf, r)
            y = r.bottom + small_gap

        for hl in hint_lines:
            surf = f.render(hl, False, (180, 200, 255))
            r = surf.get_rect(midtop=(w // 2, y))
            self.screen.blit(surf, r)
            y = r.bottom + small_gap

    def _draw_end_state_banner(self, victory: bool):
        w, h = self.screen.get_size()
        f = self._hud_font
        if f is None:
            return
        msg = "! NIVEL COMPLETADO ¡" if victory else "GAME OVER"
        clr = (90, 255, 170) if victory else (255, 92, 92)
        surf = f.render(msg, False, clr)
        self.screen.blit(surf, surf.get_rect(center=(w // 2, max(48, int(h * 0.08)))))
        hint = f.render("ENTER / SPACE — menú    ESCAPE — salir (GO)", False, (200, 200, 230))
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 50)))

    def _draw_play_hud(self):
        if self._iface is None:
            return
        esper.clear_cache()
        iface = self._iface
        w, _h = self.screen.get_size()

        margin_x = max(14, int(w * 0.022))
        pad_y = max(8, int(_h * 0.013))

        n_enemies = sum(1 for _, __ in esper.get_component(CTagEnemy))
        mutants = sum(1 for _, __ in esper.get_component(CTagMutant))

        grabbing = False
        for _, (ai, _tl) in esper.get_components(CLanderAI, CTagLander):
            if ai.capture_phase in ("approach", "ascend"):
                grabbing = True
                break
        banner_alien = "! RAPTOR !" if grabbing else ""

        row2_bits = []
        if game_state.arcade_defender_flight:
            row2_bits.append(f"BOMBAS ×{game_state.smart_bombs}")
            row2_bits.append(f"MISILES ×{game_state.homing_missiles}")
        row2_bits.append(f"VIDAS ×{game_state.lives}")
        row2_bits.append(f"ENEM {n_enemies:02d}")
        row2_bits.append(f"MUT {mutants:02d}")
        if game_state.defense_arcade_enabled:
            if game_state.defense_phase != "space":
                row2_bits.append("SUPERFICIE")
            else:
                tw = max(1, int(getattr(game_state, "defense_space_waves_total", 1) or 1))
                row2_bits.append(f"OLA ESP {game_state.space_wave_index + 1}/{tw}")
        line2_mid = "  ·  ".join(row2_bits)
        if banner_alien:
            line2_mid = f"{line2_mid}      {banner_alien}"

        font_path = str(iface["font"])
        fonts = ServiceLocator.current().get("fonts")
        fz_hi = max(18, int(iface["title"]["size"]) + 10)
        fz_lo = max(12, int(iface["instructions"].get("size", 8)) + 5)
        f_big = fonts.get(font_path, fz_hi)
        f_sub = fonts.get(font_path, fz_lo)

        col_num = (255, 228, 102)
        col_lbl = (160, 200, 255)
        lbl_sc = f_sub.render("PUNTOS ", False, col_lbl)
        num_sc = f_big.render(f"{game_state.score:06d}", False, col_num)
        lbl_hi = f_sub.render("MÁX ", False, col_lbl)
        num_hi = f_big.render(f"{game_state.high_score_best_display():06d}", False, col_num)

        line1_h = max(lbl_sc.get_height(), num_sc.get_height(), lbl_hi.get_height(), num_hi.get_height())

        sf2 = f_sub.render(line2_mid.strip(), False, (218, 224, 255))
        strip_h = pad_y + line1_h + 8 + sf2.get_height() + pad_y

        hud_strip = pygame.Surface((w, strip_h), pygame.SRCALPHA)
        hud_strip.fill((12, 16, 40, 244))
        self.screen.blit(hud_strip, (0, 0))

        cy = pad_y
        lx = margin_x
        self.screen.blit(lbl_sc, (lx, cy + max(0, (line1_h - lbl_sc.get_height()) // 2)))
        lx += lbl_sc.get_width()
        self.screen.blit(num_sc, (lx, cy + max(0, (line1_h - num_sc.get_height()) // 2)))

        block_w_hi = lbl_hi.get_width() + 6 + num_hi.get_width()
        hx0 = w - margin_x - block_w_hi
        self.screen.blit(lbl_hi, (hx0, cy + max(0, (line1_h - lbl_hi.get_height()) // 2)))
        self.screen.blit(num_hi, (hx0 + lbl_hi.get_width() + 6, cy + max(0, (line1_h - num_hi.get_height()) // 2)))

        y2 = pad_y + line1_h + 10
        self.screen.blit(sf2, (margin_x, y2))

    def _fanfare_maybe(self):
        if not game_state.consume_fanfare_flag():
            return
        path = str(game_state.get_rule("fanfare_sound", "") or "")
        if not path:
            return
        try:
            snd = ServiceLocator.current().get("sounds").load(path)
            snd.play()
        except Exception:
            pass
