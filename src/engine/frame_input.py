"""Eventos de un solo frame (p. ej. teclas con KEYDOWN) compartidos entre motor y sistemas."""

shield_pulse_requested = False


def request_shield_pulse() -> None:
    global shield_pulse_requested
    shield_pulse_requested = True


def consume_shield_pulse() -> bool:
    global shield_pulse_requested
    t = shield_pulse_requested
    shield_pulse_requested = False
    return t
