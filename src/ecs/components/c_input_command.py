class CInputCommand:
    """Cola de comandos del jugador (patrón Command) llenada por el sistema de input."""

    def __init__(self):
        self.command_queue = []
        self.prev_mouse_down = False
