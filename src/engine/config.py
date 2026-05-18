import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from src.ecs.components.c_animation import AnimClip, CAnimation
from src.ecs.components.c_bullet_def import CBulletDef
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemySpawnEvent, clone_spawn_events
from src.ecs.components.c_explosion_config import CExplosionConfig
from src.ecs.components.c_astronaut import CAstronautFootprint
from src.ecs.components.c_astronaut_state import CAstronautState
from src.ecs.components.c_color import CColor
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagAstronaut
from src.ecs.components.c_velocity import CVelocity
import esper

import src.engine.game_state as game_state

from src.engine.enemy_defs import (
    AsteroidEnemyDef,
    BomberDef,
    ChaseMutantDef,
    ChaseVariantDef,
    HunterEnemyDef,
    LanderEnemyDef,
    PodCargoDef,
)
from src.engine.service_locator import ServiceLocator


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _clamp_byte(n):
    n = int(n)
    if n < 0:
        return 0
    if n > 255:
        return 255
    return n


def _parse_anim_clips(anim_block, loop_default=True):
    """Devuelve number_frames y dict nombre -> AnimClip."""
    nf = int(anim_block["number_frames"])
    clips = {}
    for item in anim_block["list"]:
        name = str(item["name"])
        loops = loop_default if name.upper() != "EXPLODE" else False
        clips[name] = AnimClip(
            name,
            int(item["start"]),
            int(item["end"]),
            float(item["framerate"]),
            loops=loops,
        )
    return nf, clips


def load_window_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    data = _read_json(cfg_dir / "window.json")
    if isinstance(data, dict) and "window" in data:
        data = data["window"]

    title = str(data.get("title", "Ventana"))
    fullscreen = bool(data.get("fullscreen", False))
    w = max(1, int(data["size"]["w"]))
    h = max(1, int(data["size"]["h"]))
    bg = data["bg_color"]
    bg_color = (_clamp_byte(bg["r"]), _clamp_byte(bg["g"]), _clamp_byte(bg["b"]))
    framerate = max(1, int(data["framerate"]))
    return title, w, h, bg_color, framerate, fullscreen


def _try_parse_lander_def(info):
    """Lander: rectálogo JSON o sprites (`image` + `animations`)."""
    try:
        if str(info.get("type", "")).lower() != "lander":
            return None
        bullet = info.get("bullet") or {}
        bs = bullet.get("size") or {"x": 4, "y": 4}
        bc = bullet.get("color") or {"r": 240, "g": 120, "b": 90}
        bip = str(bullet["image"]).strip() if bullet.get("image") else ""
        bnf = max(1, int(bullet.get("number_frames", 1)))

        shoot_sound_path = str(info["shoot_sound"]) if info.get("shoot_sound") else ""

        kwargs = dict(
            velocity_chase=float(info["velocity_chase"]),
            velocity_return=float(info["velocity_return"]),
            distance_start_chase=float(info["distance_start_chase"]),
            distance_start_return=float(info["distance_start_return"]),
            sound_path=str(info["sound"]) if info.get("sound") else "",
            sound_chase_path=str(info["sound_chase"]) if info.get("sound_chase") else "",
            shoot_interval_sec=float(info.get("shoot_interval_sec", 0.95)),
            bullet_velocity=float(bullet.get("velocity", 160)),
            bullet_width=float(bs["x"]),
            bullet_height=float(bs["y"]),
            bullet_r=_clamp_byte(bc.get("r", 255)),
            bullet_g=_clamp_byte(bc.get("g", 140)),
            bullet_b=_clamp_byte(bc.get("b", 90)),
            shoot_sound_path=shoot_sound_path,
            bullet_image_path=bip,
            bullet_num_frames=bnf,
        )

        if info.get("image"):
            ab = info["animations"]
            nf, clips = _parse_anim_clips(ab, loop_default=True)
            return LanderEnemyDef(
                sprite_image_path=str(info["image"]),
                number_frames=nf,
                clips_by_name=clips,
                rect_w=None,
                rect_h=None,
                rect_r=None,
                rect_g=None,
                rect_b=None,
                **kwargs,
            )

        rect = info["rect"]
        col = info["color"]
        return LanderEnemyDef(
            sprite_image_path="",
            number_frames=1,
            clips_by_name={},
            rect_w=float(rect["x"]),
            rect_h=float(rect["y"]),
            rect_r=_clamp_byte(col["r"]),
            rect_g=_clamp_byte(col["g"]),
            rect_b=_clamp_byte(col["b"]),
            **kwargs,
        )
    except (KeyError, TypeError, ValueError):
        return None


def depopulate_astronaut_entities() -> None:
    for ent in [e for e, _ in esper.get_component(CTagAstronaut)]:
        esper.delete_entity(ent, immediate=True)


def repopulate_surface_astronauts(cfg_dir, screen_h: int) -> int:
    depopulate_astronaut_entities()
    populate_astronaut_entities(cfg_dir, screen_h)
    return sum(1 for _ in esper.get_component(CTagAstronaut))


def _parse_wave_events(raw_list) -> list:
    events = []
    if not isinstance(raw_list, list):
        return events
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        try:
            pos = item["position"]
            events.append(
                EnemySpawnEvent(
                    float(item["time"]),
                    str(item["enemy_type"]),
                    float(pos["x"]),
                    float(pos["y"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return events


# Coordenadas Y de `level_01` diseñadas para mundo lógico alto ~256 px; se escalan con la ventana real.
_PLAY_AREA_REF_H = 256


def _scale_spawn_events_y(events: list, screen_h_px: Optional[int]) -> None:
    if screen_h_px is None or not events:
        return
    try:
        sh = max(1, int(screen_h_px))
    except (TypeError, ValueError):
        return
    sy = float(sh) / float(_PLAY_AREA_REF_H)
    for ev in events:
        ev.pos_y = float(ev.pos_y) * sy


def build_enemy_type_defs(cfg_dir):
    cfg_dir = Path(cfg_dir)
    path = cfg_dir / "enemies.json"
    if not path.is_file():
        return {}
    try:
        data = _read_json(path)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}

    result = {}
    if not isinstance(data, dict):
        return result

    for name, info in data.items():
        if not isinstance(info, dict):
            continue
        landed = _try_parse_lander_def(info)
        if landed is not None:
            result[str(name)] = landed
            continue

        subtype = str(info.get("type", "")).lower()
        try:
            if subtype == "mutant":
                img = info["image"]
                ab = info["animations"]
                nf, clips = _parse_anim_clips(ab, loop_default=True)
                snd = str(info["sound"]) if info.get("sound") else ""
                snd_chase = str(info["sound_chase"]) if info.get("sound_chase") else ""
                result[str(name)] = ChaseMutantDef(
                    str(img),
                    nf,
                    clips,
                    float(info["velocity_chase"]),
                    float(info["velocity_return"]),
                    float(info["distance_start_chase"]),
                    float(info["distance_start_return"]),
                    sound_path=snd,
                    sound_chase_path=snd_chase,
                )
                continue
            if subtype == "pod":
                img = info["image"]
                ab = info["animations"]
                nf, clips = _parse_anim_clips(ab, loop_default=True)
                snd = str(info["sound"]) if info.get("sound") else ""
                snd_chase = str(info["sound_chase"]) if info.get("sound_chase") else ""
                result[str(name)] = PodCargoDef(
                    str(img),
                    nf,
                    clips,
                    float(info["velocity_chase"]),
                    float(info["velocity_return"]),
                    float(info["distance_start_chase"]),
                    float(info["distance_start_return"]),
                    int(info.get("swarm_count", 4)),
                    str(info["swarm_enemy"]),
                    sound_path=snd,
                    sound_chase_path=snd_chase,
                )
                continue
            if subtype == "bomber":
                img = info["image"]
                ab = info["animations"]
                nf, clips = _parse_anim_clips(ab, loop_default=True)
                snd = str(info["sound"]) if info.get("sound") else ""
                bip = str(info.get("bomb_image", "") or "").strip()
                result[str(name)] = BomberDef(
                    str(img),
                    nf,
                    clips,
                    float(info.get("velocity_x", -40)),
                    float(info.get("velocity_y", 0)),
                    float(info.get("bomb_interval_sec", 2.0)),
                    float(info.get("bomb_fall_speed", 70)),
                    bomb_image_path=bip,
                    sound_path=snd,
                )
                continue
        except (KeyError, TypeError, ValueError):
            pass

        try:
            img = info["image"]
            if "distance_start_chase" in info or "velocity_chase" in info:
                ab = info["animations"]
                nf, clips = _parse_anim_clips(ab, loop_default=True)
                snd = str(info["sound"]) if info.get("sound") else ""
                snd_chase = str(info["sound_chase"]) if info.get("sound_chase") else ""
                variant = str(info.get("chase_variant", "hunter")).lower()
                if variant in ("swarmer", "baiter"):
                    result[str(name)] = ChaseVariantDef(
                        str(img),
                        nf,
                        clips,
                        float(info["velocity_chase"]),
                        float(info["velocity_return"]),
                        float(info["distance_start_chase"]),
                        float(info["distance_start_return"]),
                        sound_path=snd,
                        sound_chase_path=snd_chase,
                        variant=variant,
                    )
                else:
                    result[str(name)] = HunterEnemyDef(
                        str(img),
                        nf,
                        clips,
                        float(info["velocity_chase"]),
                        float(info["velocity_return"]),
                        float(info["distance_start_chase"]),
                        float(info["distance_start_return"]),
                        sound_path=snd,
                        sound_chase_path=snd_chase,
                    )
            else:
                vmin = float(info["velocity_min"])
                vmax = float(info["velocity_max"])
                if vmin > vmax:
                    vmin, vmax = vmax, vmin
                snd = str(info["sound"]) if info.get("sound") else ""
                result[str(name)] = AsteroidEnemyDef(str(img), vmin, vmax, sound_path=snd)
                # Marcar asteroides demo para rebote físico únicamente donde aplique Tag.
                # (Opcional futuro: segunda pasada registrar CTagAsteroid en spawner.)
        except (KeyError, TypeError, ValueError):
            continue
    return result


def populate_astronaut_entities(cfg_dir, screen_h: int) -> None:
    """Lee `level_01.json` y crea ECS astronautas antes del primer snap a terreno."""
    cfg_dir = Path(cfg_dir)
    level_path = cfg_dir / "level_01.json"
    if not level_path.is_file():
        return
    try:
        level = _read_json(level_path)
    except (OSError, json.JSONDecodeError):
        return
    raw = level.get("astronaut_spawns")
    if not isinstance(raw, list) or len(raw) == 0:
        return

    visuals = level.get("astronaut_visual", {}) if isinstance(level, dict) else {}
    clear = float(visuals.get("clearance_px_above_terrain", 9.0))
    wobble = float(visuals.get("wobble_amplitude_px", 4.0))
    hz = float(visuals.get("wobble_hz", 0.55))
    img_path = str(visuals["image"]).strip() if visuals.get("image") else ""
    astro_anim_block = visuals.get("animations")
    sz = visuals.get("size") or {"x": 11, "y": 16}
    col = visuals.get("color") or {"r": 230, "g": 230, "b": 255}

    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            x = float(item["x"])
        except (KeyError, TypeError, ValueError):
            continue
        ay = float(item.get("y", screen_h * 0.55))
        e = esper.create_entity()
        esper.add_component(e, CPosition(x, ay))
        esper.add_component(e, CVelocity(0.0, 0.0))
        esper.add_component(e, CAstronautFootprint(clear, wobble, hz))
        esper.add_component(e, CAstronautState(CAstronautState.GROUND))
        esper.add_component(e, CTagAstronaut())

        tex = ServiceLocator.current().get("textures")
        if img_path:
            surf = tex.load(img_path)
            if isinstance(astro_anim_block, dict) and isinstance(astro_anim_block.get("list"), list):
                nf, clips = _parse_anim_clips(astro_anim_block, loop_default=True)
            else:
                nf = 1
                clips = {"IDLE": AnimClip("IDLE", 0, 0, 6.0, loops=True)}
            cs = CSurface(surf, nf)
            esper.add_component(e, cs)
            esper.add_component(e, CAnimation(nf, clips, initial="IDLE"))
        else:
            ww = float(sz["x"])
            hh = float(sz["y"])
            hue = (_clamp_byte(col["r"]), _clamp_byte(col["g"]), _clamp_byte(col["b"]))
            esper.add_component(e, CSize(ww, hh))
            esper.add_component(e, CColor(hue[0], hue[1], hue[2]))


def _parse_player_spawn(level_data):
    default_x, default_y = 320.0, 180.0
    max_bullets = 99
    if not isinstance(level_data, dict):
        return max_bullets, default_x, default_y
    ps = level_data.get("player_spawn")
    if not isinstance(ps, dict):
        return max_bullets, default_x, default_y
    try:
        pos = ps["position"]
        default_x = float(pos["x"])
        default_y = float(pos["y"])
        max_bullets = int(ps["max_bullets"])
    except (KeyError, TypeError, ValueError):
        pass
    return max(0, max_bullets), default_x, default_y


def build_enemy_spawner_component(cfg_dir, enemy_types, screen_h_px: Optional[int] = None):
    cfg_dir = Path(cfg_dir)
    level_path = cfg_dir / "level_01.json"
    empty = CEnemySpawner([], enemy_types, 99, 160.0, 100.0)
    if not level_path.is_file():
        return empty
    level_data = _read_json(level_path)
    events: list = []
    max_bullets, px, py = _parse_player_spawn(level_data)

    if not isinstance(level_data, dict):
        return CEnemySpawner(events, enemy_types, max_bullets, px, py)

    dac = level_data.get("defense_arcade") if isinstance(level_data.get("defense_arcade"), dict) else None
    surf_raw = []
    space_templates: list[list] = []
    if dac and dac.get("enabled"):
        surf_raw = dac.get("surface_enemy_spawn_events") or []
        waves_r = dac.get("space_waves") or []
        if isinstance(waves_r, list):
            for w in waves_r:
                ew = _parse_wave_events(w)
                _scale_spawn_events_y(ew, screen_h_px)
                if ew:
                    space_templates.append(ew)
    if not surf_raw:
        surf_raw = level_data.get("enemy_spawn_events", []) if isinstance(level_data.get("enemy_spawn_events"), list) else []
    events = _parse_wave_events(surf_raw)
    _scale_spawn_events_y(events, screen_h_px)
    astro_len = len(level_data.get("astronaut_spawns") or []) if isinstance(level_data.get("astronaut_spawns"), list) else 0

    game_state.defense_arcade_enabled = bool(dac and dac.get("enabled") and len(space_templates) >= 1)
    game_state.defense_space_waves_total = len(space_templates) if game_state.defense_arcade_enabled else 0
    game_state.defense_phase = "surface"
    game_state.space_wave_index = 0
    game_state.surface_astronauts_initial = astro_len if game_state.defense_arcade_enabled else 0
    game_state.wave_survival_sec = 0.0
    game_state.baiter_spawned_this_wave = False
    game_state.play_cfg_dir = cfg_dir.resolve()

    spawner = CEnemySpawner(events, enemy_types, max_bullets, px, py)
    spawner.surface_template = clone_spawn_events(events)
    spawner.space_wave_templates = [clone_spawn_events(sw) for sw in space_templates]
    return spawner


def build_bullet_def(cfg_dir):
    cfg_dir = Path(cfg_dir)
    try:
        data = _read_json(cfg_dir / "bullet.json")
        snd = str(data["sound"]) if data.get("sound") else ""
        if "image" in data:
            nf = max(1, int(data.get("number_frames", 1)))
            return CBulletDef(
                float(data["velocity"]),
                image_path=str(data["image"]),
                num_frames=nf,
                sound_path=snd,
            )
        sz = data["size"]
        col = data["color"]
        return CBulletDef(
            float(data["velocity"]),
            None,
            float(sz["x"]),
            float(sz["y"]),
            _clamp_byte(col["r"]),
            _clamp_byte(col["g"]),
            _clamp_byte(col["b"]),
            sound_path=snd,
        )
    except (KeyError, TypeError, ValueError, FileNotFoundError):
        return CBulletDef(
            200,
            image_path="assets/img/bullet.png",
            num_frames=1,
            sound_path="assets/snd/laser.ogg",
        )


def build_player_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    try:
        data = _read_json(cfg_dir / "player.json")
        sm = str(data["sound"]) if data.get("sound") else ""
        sc = str(data["sound_collision"]) if data.get("sound_collision") else ""
        if "image" in data:
            ab = data["animations"]
            nf, clips = _parse_anim_clips(ab, loop_default=True)
            out = {
                "sprite": True,
                "image": str(data["image"]),
                "number_frames": nf,
                "clips": clips,
                "input_velocity": float(data["input_velocity"]),
                "motion_smoothing_hz": float(data.get("motion_smoothing_hz", 20)),
                "sound_move": sm,
                "sound_collision": sc,
                "arcade_defender_flight": bool(data.get("arcade_defender_flight", False)),
            }
            bid = data.get("burner_idle_image")
            bmv = data.get("burner_moving_image")
            if bid and bmv:
                out["burner_idle_image"] = str(bid)
                out["burner_moving_image"] = str(bmv)
                out["burner_idle_frames"] = max(1, int(data.get("burner_idle_frames", 3)))
                out["burner_moving_frames"] = max(1, int(data.get("burner_moving_frames", 3)))
                out["burner_anim_hz"] = float(data.get("burner_anim_hz", 12.0))
                out["burner_tuck_px"] = float(data.get("burner_tuck_px", 3.0))
            return out
        sz = data["size"]
        col = data["color"]
        return {
            "sprite": False,
            "w": float(sz["x"]),
            "h": float(sz["y"]),
            "r": _clamp_byte(col["r"]),
            "g": _clamp_byte(col["g"]),
            "b": _clamp_byte(col["b"]),
            "input_velocity": float(data["input_velocity"]),
            "motion_smoothing_hz": float(data.get("motion_smoothing_hz", 20)),
            "sound_move": sm,
            "sound_collision": sc,
            "arcade_defender_flight": bool(data.get("arcade_defender_flight", False)),
        }
    except (KeyError, TypeError, ValueError, FileNotFoundError):
        nf, clips = _parse_anim_clips(
            {
                "number_frames": 4,
                "list": [{"name": "IDLE", "start": 0, "end": 3, "framerate": 8}],
            },
            loop_default=True,
        )
        return {
            "sprite": True,
            "image": "assets/img/player.png",
            "number_frames": nf,
            "clips": clips,
            "input_velocity": 100.0,
            "motion_smoothing_hz": 20.0,
            "sound_move": "assets/snd/laser.ogg",
            "sound_collision": "assets/snd/explosion.ogg",
            "arcade_defender_flight": False,
        }


def build_explosion_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    try:
        data = _read_json(cfg_dir / "explosion.json")
        ab = data["animations"]
        nf, clips = _parse_anim_clips(ab, loop_default=False)
        snd = str(data["sound"]) if data.get("sound") else ""
        return CExplosionConfig(str(data["image"]), nf, clips, sound_path=snd)
    except (KeyError, TypeError, ValueError, FileNotFoundError):
        nf, clips = _parse_anim_clips(
            {
                "number_frames": 8,
                "list": [{"name": "EXPLODE", "start": 0, "end": 7, "framerate": 16}],
            },
            loop_default=False,
        )
        return CExplosionConfig(
            "assets/img/explosion.png",
            nf,
            clips,
            sound_path="assets/snd/explosion.ogg",
        )


def load_interface_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    path = cfg_dir / "interface.json"
    defaults = {
        "font": "assets/fnt/PressStart2P.ttf",
        "title": {
            "text": "ECS Shooter",
            "size": 14,
            "color": {"r": 255, "g": 220, "b": 64},
            "position": {"x": 10, "y": 6},
        },
        "pause": {
            "text": "PAUSA",
            "size": 28,
            "color": {"r": 255, "g": 120, "b": 120},
        },
        "instructions": {
            "text": "Defender: ↑↓ ←→ X=empuje C=invertir Z=láser ESP=bomba H=hiper P=pausa",
            "size": 8,
            "color": {"r": 200, "g": 200, "b": 210},
            "position": {"x": 4, "y": 246},
        },
        "shield_status": {
            "size": 10,
            "color": {"r": 120, "g": 220, "b": 255},
            "position": {"x": 8, "y": 234},
        },
    }
    if not path.is_file():
        return copy.deepcopy(defaults)
    try:
        data = _read_json(path)
        if not isinstance(data, dict):
            return copy.deepcopy(defaults)
        out = copy.deepcopy(defaults)
        if "font" in data:
            out["font"] = str(data["font"])
        for key in ("title", "pause", "instructions", "shield_status"):
            if key in data and isinstance(data[key], dict):
                out[key].update(data[key])
        return out
    except (OSError, json.JSONDecodeError, TypeError):
        return copy.deepcopy(defaults)


def load_special_shield_config(cfg_dir):
    cfg_dir = Path(cfg_dir)
    path = cfg_dir / "special.json"
    defaults = {
        "duration_sec": 2.0,
        "cooldown_sec": 5.0,
        "radius_px": 130.0,
        "activation_key": "SPACE",
    }
    if not path.is_file():
        return defaults
    try:
        data = _read_json(path)
        block = data.get("shield_pulse", data) if isinstance(data, dict) else {}
        if not isinstance(block, dict):
            return defaults
        out = defaults.copy()
        for k in defaults:
            if k in block:
                out[k] = block[k]
        out["duration_sec"] = float(out["duration_sec"])
        out["cooldown_sec"] = float(out["cooldown_sec"])
        out["radius_px"] = float(out["radius_px"])
        out["activation_key"] = str(out.get("activation_key", "SPACE"))
        return out
    except (OSError, json.JSONDecodeError, TypeError):
        return defaults


def _rgb_tuple(block):
    if not isinstance(block, dict):
        return 200, 210, 255
    return (
        _clamp_byte(block.get("r", 220)),
        _clamp_byte(block.get("g", 220)),
        _clamp_byte(block.get("b", 255)),
    )


def _world_json_defaults():
    return {
        "star_colors": [
            {"r": 213, "g": 0, "b": 0},
            {"r": 118, "g": 255, "b": 3},
            {"r": 65, "g": 105, "b": 225},
        ],
        "stars_number": 50,
        "stars_parallax_factor": 1.0,
        "stars_blink_rate": {"min": 0.25, "max": 0.5},
        "planet_terrain_colors": [
            {"r": 255, "g": 90, "b": 90},
            {"r": 118, "g": 255, "b": 118},
            {"r": 120, "g": 120, "b": 225},
        ],
        "planet_terrain_line_points": 50,
        "planet_parallax_factor": 1.25,
        "ambient_horizontal_scroll_px_s": 14.0,
        "planet_baseline_offset_from_bottom_px": 56,
        "scenario_seed": None,
        "play_area_top_px": None,
        "play_area_bottom_px": None,
    }


@dataclass(frozen=True)
class LoadedWorldCfg:
    star_colors: Tuple[Tuple[int, int, int], ...]
    stars_number: int
    stars_parallax_factor: float
    stars_blink_min_sec: float
    stars_blink_max_sec: float
    planet_colors: Tuple[Tuple[int, int, int], ...]
    planet_line_points: int
    planet_parallax_factor: float
    ambient_scroll_px_s: float
    planet_baseline_from_bottom_px: int
    play_area_top_px: Optional[int]
    play_area_bottom_px: Optional[int]


def load_world_bundle(cfg_dir) -> tuple[LoadedWorldCfg, int]:
    cfg_dir = Path(cfg_dir)
    raw = _world_json_defaults().copy()
    path = cfg_dir / "world.json"
    if path.is_file():
        try:
            blob = _read_json(path)
            if isinstance(blob, dict):
                for k, v in blob.items():
                    raw[k] = v
        except (OSError, json.JSONDecodeError, TypeError):
            pass

    star_colors = [_rgb_tuple(x) for x in raw.get("star_colors", []) if isinstance(x, dict)]
    if not star_colors:
        star_colors = [_rgb_tuple(c) for c in _world_json_defaults()["star_colors"]]
    planet_colors = [_rgb_tuple(x) for x in raw.get("planet_terrain_colors", []) if isinstance(x, dict)]
    if not planet_colors:
        planet_colors = [_rgb_tuple(c) for c in _world_json_defaults()["planet_terrain_colors"]]

    blink = raw.get("stars_blink_rate") or {}
    mn = float(blink.get("min", 0.25))
    mx = float(blink.get("max", 0.5))
    mn, mx = sorted((max(0.02, mn), max(0.02, mx)))

    def _opt_px(key):
        val = raw.get(key, None)
        if val is None:
            return None
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    cfg = LoadedWorldCfg(
        star_colors=tuple(star_colors),
        stars_number=max(0, int(raw.get("stars_number", 50))),
        stars_parallax_factor=max(0.0, float(raw.get("stars_parallax_factor", 1.0))),
        stars_blink_min_sec=mn,
        stars_blink_max_sec=max(mn, mx),
        planet_colors=tuple(planet_colors),
        planet_line_points=max(8, int(raw.get("planet_terrain_line_points", 50))),
        planet_parallax_factor=max(0.0, float(raw.get("planet_parallax_factor", 1.25))),
        ambient_scroll_px_s=max(0.0, float(raw.get("ambient_horizontal_scroll_px_s", 14.0))),
        planet_baseline_from_bottom_px=max(18, int(raw.get("planet_baseline_offset_from_bottom_px", 56))),
        play_area_top_px=_opt_px("play_area_top_px"),
        play_area_bottom_px=_opt_px("play_area_bottom_px"),
    )

    seed_blob = raw.get("scenario_seed")
    if seed_blob is None:
        import random as _random

        rng_seed = _random.randint(1, (1 << 30) - 1)
    else:
        rng_seed = int(seed_blob)
    return cfg, rng_seed


def build_game_rules(cfg_dir) -> dict:
    """Reglas económicas y tuning Defender (retroalimentadas en `game_state.rules_cache`)."""
    cfg_dir = Path(cfg_dir)
    defaults = {
        "initial_lives": 3,
        "score_lander_kill": 150,
        "score_mutant_kill": 150,
        "score_hunter_kill": 120,
        "score_asteroid_kill": 25,
        "score_human_rescue": 500,
        "score_human_friend_fire": -180,
        "gravity_human_px_s2": 520.0,
        "lander_capture_horizontal_px": 100.0,
        "lander_approach_speed": 48.0,
        "lander_ascend_speed": 58.0,
        "lander_mutate_y_px": 16.0,
        "mutant_velocity_chase": 115.0,
        "mutant_velocity_return": 70.0,
        "mutant_distance_chase_start": 400.0,
        "mutant_distance_return": 580.0,
        "missile_chance_per_sec": 0.1,
        "missile_speed": 95.0,
        "missile_cd_sec": 1.35,
        "fanfare_sound": "",
        "mutant_image": "assets/img/enemy_mutant.png",
        "mutant_number_frames": 5,
        "mutant_anim_framerate": 12.0,
        "sound_pause": "",
        "sound_game_over": "",
        "sound_lander_capture": "",
        "sound_lander_mutate": "",
        "sound_astronaut_fall": "",
        "initial_smart_bombs": 3,
        "score_extra_life_every": 10000,
        "smart_bomb_inventory_cap": 254,
        "extra_lives_cap": 255,
        "wave_bonus_per_human_alive": 100,
        "hyperspace_death_chance": 0.35,
        "arcade_thrust_accel_px_s2": 420.0,
        "arcade_drag_per_s": 0.72,
        "arcade_max_speed_x": 220.0,
        "arcade_vertical_speed_px_s": 150.0,
        "score_pod_kill": 1000,
        "score_bomber_kill": 250,
        "score_baiter_kill": 200,
        "score_swarmer_kill": 150,
        "score_bomb_destroy": 0,
        "baiter_spawn_after_wave_sec": 24.0,
        "baiter_enemy_key": "baiter_ufo",
        "bomber_bomb_image": "assets/img/bomber_bomb.png",
        "bomber_bomb_num_frames": 5,
        "bomber_bomb_anim_framerate": 14.0,
        "score_space_wave_clear_bonus": 200,
        "restore_surface_score_bonus": 1500,
        "planet_explosion_flash_sec": 2.2,
        "smart_bomb_flash_sec": 0.42,
        "scoreboard_reserve_top_px": 0,
        "playfield_air_bottom_px": -1,
        "playfield_air_bottom_frac": -1,
        "terrain_occlusion_alpha": 200,
        "terrain_occlusion_lip_px": 6.0,
        "sprite_draw_scale": 2.0,
        "radar_blip_scale": 2.0,
    }
    path = cfg_dir / "game_rules.json"
    if not path.is_file():
        return defaults
    try:
        raw = _read_json(path)
    except (OSError, json.JSONDecodeError, TypeError):
        return defaults
    if not isinstance(raw, dict):
        return defaults
    out = dict(defaults)
    for k, v in raw.items():
        if k in out:
            t0 = out[k]
            if isinstance(t0, int):
                out[k] = int(v)
            elif isinstance(t0, float):
                out[k] = float(v)
            else:
                out[k] = v
        else:
            out[k] = v
    return out
