from src.engine.service_locator import ServiceLocator


def play_sound(relative_path: str, volume: float = 1.0) -> None:
    if not relative_path:
        return
    try:
        snd = ServiceLocator.current().get("sounds").load(relative_path)
        v = max(0.0, min(1.0, float(volume)))
        snd.set_volume(v)
        snd.play()
    except Exception:
        pass
