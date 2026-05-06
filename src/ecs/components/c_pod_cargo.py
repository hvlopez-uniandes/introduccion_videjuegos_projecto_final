class CPodCargo:
    """Capsula Defender: al destruirse suelta swarmers configurados desde JSON."""

    def __init__(self, swarm_enemy_key: str, swarm_count: int):
        self.swarm_enemy_key = str(swarm_enemy_key)
        self.swarm_count = max(1, int(swarm_count))
