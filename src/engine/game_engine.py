from pathlib import Path

import esper
import pygame

from src.engine.config import (
    build_bullet_def,
    build_enemy_spawner_component,
    build_enemy_type_defs,
    build_explosion_config,
    build_player_config,
    load_interface_config,
    load_special_shield_config,
    load_window_config,
)
from src.engine.game_state import set_paused
import src.engine.game_state as game_state
from src.engine.frame_input import request_shield_pulse
from src.engine.input_keys import pygame_key_from_string
from src.engine.paths import set_project_root
from src.engine.resource_services import FontService, SoundService, TextureService
from src.engine.service_locator import ServiceLocator
from src.engine.textures import clear_texture_cache
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_color import CColor
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_input_speed import CPlayerInputSpeed
from src.ecs.components.c_player_sfx import CPlayerSfx
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_shield_special import CShieldSpecial
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagHud, CTagHudDynamic, CTagPlayer
from src.ecs.components.c_ui_text_style import CUiTextStyle
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.system_animation import system_animation
from src.ecs.systems.system_bounce import system_bounce
from src.ecs.systems.system_bullet_bounds import system_bullet_bounds
from src.ecs.systems.system_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.system_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.system_draw import system_draw
from src.ecs.systems.system_draw_shield_ring import system_draw_shield_ring
from src.ecs.systems.system_enemy_spawner import system_enemy_spawner
from src.ecs.systems.system_execute_commands import system_execute_commands
from src.ecs.systems.system_explosion_cleanup import system_explosion_cleanup
from src.ecs.systems.system_hunter_ai import system_hunter_ai
from src.ecs.systems.system_hunter_animation import system_hunter_animation
from src.ecs.systems.system_input_command import system_input_command
from src.ecs.systems.system_movement import system_movement
from src.ecs.systems.system_player_animation import system_player_animation
from src.ecs.systems.system_player_bounds import system_player_bounds
from src.ecs.systems.system_player_move_sound import system_player_move_sound
from src.ecs.systems.system_shield_hud_refresh import system_shield_hud_refresh
from src.ecs.systems.system_shield_pulse import system_shield_pulse


def _clamp_byte(n):
    n = int(n)
    return max(0, min(255, n))


class GameEngine:
    def __init__(self, cfg_dir=None):
        self._root = Path(__file__).resolve().parents[2]
        if cfg_dir is None:
            self._cfg_dir = self._root / "src" / "cfg"
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
        self._pause_text = "PAUSA"
        self._pause_font_size = 28
        self._pause_color = (255, 120, 120)

    def run(self):
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    def _bind_services(self):
        loc = ServiceLocator()
        loc.register("textures", TextureService(self._root))
        loc.register("sounds", SoundService(self._root))
        loc.register("fonts", FontService(self._root))
        ServiceLocator.bind(loc)

    def _setup_interface_entities(self):
        iface = load_interface_config(self._cfg_dir)
        self._iface = iface
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

        pause = iface["pause"]
        self._pause_text = str(pause.get("text", "PAUSA"))
        self._pause_font_size = int(pause.get("size", 28))
        c = pause.get("color", {})
        self._pause_color = (
            _clamp_byte(c.get("r", 255)),
            _clamp_byte(c.get("g", 120)),
            _clamp_byte(c.get("b", 120)),
        )

    def _create(self):
        clear_texture_cache()
        esper.clear_database()
        pygame.init()
        pygame.mixer.init()
        set_project_root(self._root)
        self._bind_services()

        title, w, h, self.bg_color, self.framerate = load_window_config(self._cfg_dir)
        self.screen_w = w
        self.screen_h = h

        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((w, h))
        self.clock = pygame.time.Clock()

        enemy_types = build_enemy_type_defs(self._cfg_dir)
        spawner_component = build_enemy_spawner_component(self._cfg_dir, enemy_types)
        bullet_def = build_bullet_def(self._cfg_dir)
        player_cfg = build_player_config(self._cfg_dir)
        explosion_cfg = build_explosion_config(self._cfg_dir)
        shield_cfg = load_special_shield_config(self._cfg_dir)
        self._shield_key = pygame_key_from_string(shield_cfg.get("activation_key", "SPACE"))

        entity_spawner = esper.create_entity()
        esper.add_component(entity_spawner, spawner_component)
        esper.add_component(entity_spawner, bullet_def)
        esper.add_component(entity_spawner, explosion_cfg)

        player_entity = esper.create_entity()
        esper.add_component(
            player_entity,
            CPosition(spawner_component.player_spawn_x, spawner_component.player_spawn_y),
        )
        esper.add_component(player_entity, CVelocity(0.0, 0.0))
        esper.add_component(player_entity, CInputCommand())
        esper.add_component(player_entity, CPlayerInputSpeed(player_cfg["input_velocity"]))
        esper.add_component(player_entity, CTagPlayer())
        esper.add_component(
            player_entity,
            CPlayerSfx(
                player_cfg.get("sound_move") or "",
                player_cfg.get("sound_collision") or "",
            ),
        )
        esper.add_component(
            player_entity,
            CShieldSpecial(
                shield_cfg["duration_sec"],
                shield_cfg["cooldown_sec"],
                shield_cfg["radius_px"],
                self._shield_key,
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

    def _calculate_time(self):
        ms = self.clock.tick(self.framerate)
        self.delta_time = ms / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state.toggle_pause()
                elif event.key == self._shield_key:
                    request_shield_pulse()

    def _update(self):
        if game_state.paused:
            return
        system_input_command()
        system_execute_commands()
        system_enemy_spawner(self.delta_time)
        system_hunter_ai()
        system_movement(self.delta_time)
        system_player_bounds(self.screen_w, self.screen_h)
        system_bounce(self.screen_w, self.screen_h)
        system_bullet_bounds(self.screen_w, self.screen_h)
        system_animation(self.delta_time)
        system_player_animation()
        system_hunter_animation()
        system_shield_pulse(self.delta_time)
        system_collision_bullet_enemy()
        system_collision_player_enemy()
        system_explosion_cleanup()
        system_player_move_sound()
        system_shield_hud_refresh()

    def _draw_pause_overlay(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        font = ServiceLocator.current().get("fonts").get(self._iface["font"], self._pause_font_size)
        surf = font.render(self._pause_text, False, self._pause_color)
        rect = surf.get_rect(center=(w // 2, h // 2))
        self.screen.blit(surf, rect)

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_draw(self.screen)
        system_draw_shield_ring(self.screen)
        if game_state.paused:
            self._draw_pause_overlay()
        pygame.display.flip()

    def _clean(self):
        pygame.quit()
