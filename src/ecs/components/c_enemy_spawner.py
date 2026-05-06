# Componente del spawner: acá guardo lo que saqué del level_01.json
# y una copia del diccionario de enemigos (AsteroidEnemyDef / HunterEnemyDef).


class EnemySpawnEvent:
    # Un evento = a qué segundo spawnea, qué tipo, dónde, y si ya lo hice
    def __init__(self, time_sec, enemy_type, pos_x, pos_y):
        self.time_sec = time_sec
        self.enemy_type = enemy_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.fired = False


def clone_spawn_events(events):
    """Copia eventos sin disparos (plantilla para olas espacio / restaurar superficie)."""
    return [
        EnemySpawnEvent(float(e.time_sec), str(e.enemy_type), float(e.pos_x), float(e.pos_y))
        for e in events
    ]


class CEnemySpawner:
    def __init__(self, events, enemy_types, max_bullets=99, player_spawn_x=320.0, player_spawn_y=180.0):
        self.accumulated_time = 0.0
        self.events = events
        self.enemy_types = enemy_types
        self.max_bullets = int(max_bullets)
        self.player_spawn_x = float(player_spawn_x)
        self.player_spawn_y = float(player_spawn_y)
        # Plantillas Defender FAQ: superficie y varias oleadas espacio vacías hasta parse.
        self.surface_template: list = []
        self.space_wave_templates = []

    def load_event_wave(self, new_events):
        """Nueva lista de spawn (ola); reinicia tiempo y pendientes."""
        self.events = new_events
        self.accumulated_time = 0.0
