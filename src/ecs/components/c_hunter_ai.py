class CHunterAI:
    """Perseguidor: persigue al jugador dentro de d; si se aleja más de d_o del origen, vuelve a p_o."""

    def __init__(
        self,
        origin_x,
        origin_y,
        chase_dist,
        return_dist,
        v_chase,
        v_return,
        sound_chase_path=None,
    ):
        self.origin_x = float(origin_x)
        self.origin_y = float(origin_y)
        self.chase_dist = float(chase_dist)
        self.return_dist = float(return_dist)
        self.v_chase = float(v_chase)
        self.v_return = float(v_return)
        self.state = "idle"
        self.sound_chase_path = sound_chase_path or ""
