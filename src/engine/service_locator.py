class ServiceLocator:
    """Registro central de servicios (texturas, sonido, fuentes)."""

    _instance = None

    def __init__(self):
        self._services = {}

    def register(self, name: str, service) -> None:
        self._services[name] = service

    def get(self, name: str):
        return self._services[name]

    @classmethod
    def bind(cls, locator: "ServiceLocator") -> None:
        cls._instance = locator

    @classmethod
    def current(cls) -> "ServiceLocator":
        if cls._instance is None:
            raise RuntimeError("ServiceLocator no inicializado")
        return cls._instance
