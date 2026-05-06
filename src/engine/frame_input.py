"""Eventos de un solo frame (p. ej. teclas con KEYDOWN) compartidos entre motor y sistemas."""

shield_pulse_requested = False
smart_bomb_requested = False
hyperspace_requested = False


def request_shield_pulse() -> None:
    global shield_pulse_requested
    shield_pulse_requested = True


def consume_shield_pulse() -> bool:
    global shield_pulse_requested
    t = shield_pulse_requested
    shield_pulse_requested = False
    return t


def request_smart_bomb() -> None:
    global smart_bomb_requested
    smart_bomb_requested = True


def consume_smart_bomb() -> bool:
    global smart_bomb_requested
    t = smart_bomb_requested
    smart_bomb_requested = False
    return t


def request_hyperspace() -> None:
    global hyperspace_requested
    hyperspace_requested = True


def consume_hyperspace() -> bool:
    global hyperspace_requested
    t = hyperspace_requested
    hyperspace_requested = False
    return t
