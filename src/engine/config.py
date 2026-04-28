import copy
import json
from pathlib import Path

from src.ecs.components.c_animation import AnimClip
from src.ecs.components.c_bullet_def import CBulletDef
from src.ecs.components.c_enemy_spawner import CEnemySpawner, EnemySpawnEvent
from src.ecs.components.c_explosion_config import CExplosionConfig
from src.engine.enemy_defs import AsteroidEnemyDef, HunterEnemyDef


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
    w = max(1, int(data["size"]["w"]))
    h = max(1, int(data["size"]["h"]))
    bg = data["bg_color"]
    bg_color = (_clamp_byte(bg["r"]), _clamp_byte(bg["g"]), _clamp_byte(bg["b"]))
    framerate = max(1, int(data["framerate"]))
    return title, w, h, bg_color, framerate


def build_enemy_type_defs(cfg_dir):
    cfg_dir = Path(cfg_dir)
    data = _read_json(cfg_dir / "enemies.json")
    result = {}
    if not isinstance(data, dict):
        return result

    for name, info in data.items():
        if not isinstance(info, dict):
            continue
        try:
            img = info["image"]
            if "distance_start_chase" in info or "velocity_chase" in info:
                ab = info["animations"]
                nf, clips = _parse_anim_clips(ab, loop_default=True)
                snd = str(info["sound"]) if info.get("sound") else ""
                snd_chase = str(info["sound_chase"]) if info.get("sound_chase") else ""
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
        except (KeyError, TypeError, ValueError):
            continue
    return result


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


def build_enemy_spawner_component(cfg_dir, enemy_types):
    cfg_dir = Path(cfg_dir)
    level_data = _read_json(cfg_dir / "level_01.json")
    events = []
    max_bullets, px, py = _parse_player_spawn(level_data)

    if not isinstance(level_data, dict):
        return CEnemySpawner(events, enemy_types, max_bullets, px, py)

    raw_list = level_data.get("enemy_spawn_events", [])
    if not isinstance(raw_list, list):
        return CEnemySpawner(events, enemy_types, max_bullets, px, py)

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

    return CEnemySpawner(events, enemy_types, max_bullets, px, py)


def build_bullet_def(cfg_dir):
    cfg_dir = Path(cfg_dir)
    try:
        data = _read_json(cfg_dir / "bullet.json")
        snd = str(data["sound"]) if data.get("sound") else ""
        if "image" in data:
            return CBulletDef(
                float(data["velocity"]),
                image_path=str(data["image"]),
                num_frames=1,
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
            return {
                "sprite": True,
                "image": str(data["image"]),
                "number_frames": nf,
                "clips": clips,
                "input_velocity": float(data["input_velocity"]),
                "sound_move": sm,
                "sound_collision": sc,
            }
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
            "sound_move": sm,
            "sound_collision": sc,
        }
    except (KeyError, TypeError, ValueError, FileNotFoundError):
        return {
            "sprite": True,
            "image": "assets/img/player.png",
            "number_frames": 4,
            "clips": {},
            "input_velocity": 100.0,
            "sound_move": "assets/snd/laser.ogg",
            "sound_collision": "assets/snd/explosion.ogg",
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
            "text": "Flechas mover | Clic disparar | P pausa | ESP pulso",
            "size": 8,
            "color": {"r": 200, "g": 200, "b": 210},
            "position": {"x": 8, "y": 338},
        },
        "shield_status": {
            "size": 10,
            "color": {"r": 120, "g": 220, "b": 255},
            "position": {"x": 8, "y": 318},
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
