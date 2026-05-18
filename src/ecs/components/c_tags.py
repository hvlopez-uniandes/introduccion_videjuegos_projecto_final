class CTagPlayer:
    pass


class CTagEnemy:
    pass


class CTagBullet:
    pass


class CTagHunter:
    """Enemigo tipo Hunter (IA de persecución / retorno)."""


class CTagLander:
    """Enemigo Lander Defender (disp. frente jugador visible)."""


class CTagMutant:
    """Ex-Lander metamorfoseado: persigue nave (Defender arcade)."""


class CTagSwarmer:
    pass


class CTagBaiter:
    pass


class CTagPod:
    pass


class CTagBomber:
    pass


class CTagBomb:
    """Mina dejada por Bomber (daña jugador; láser la destruye)."""


class CTagEnemyMissile:
    """Misil corto lanzado por mutant (opcional rápido de reglas curso)."""


class CTagAsteroid:
    """Asteroide clásico demo (rebota en pantalla)."""


class CTagEnemyBullet:
    """Proyectil enemigo."""


class CTagAstronaut:
    """Humano sobre el borde-planeta procedural."""


class CTagExplosion:
    """Entidad temporal de explosión."""


class CTagHud:
    """Texto de interfaz estático (título, ayuda)."""


class CTagHudDynamic:
    """Texto de interfaz que se regenera por frame (p. ej. cooldown)."""

class CTagMissileHoming:
    """Misil de rastreo con daño en área."""