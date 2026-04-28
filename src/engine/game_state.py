paused = False


def toggle_pause() -> None:
    global paused
    paused = not paused


def set_paused(value: bool) -> None:
    global paused
    paused = bool(value)
