# Documento de avance

## Datos del grupo

- **Nombre del grupo:** Proyecto final Defender
- **Última actualización:** `2026-04-28`

## Integrantes, roles y trabajo realizado

| Miembro | Rol en el equipo | Labor |
|---------|-----------------|--------------------------------------------------------------------------|
| **Leonardo L. Rueda** | Jugador, comandos de entrada y sensación base | Ciclo relacionado con **input → Command**, movimiento/atributos del jugador, límites y animación/UI que dependan de la nave (módulos bajo `src/ecs/` orientados al jugador y `frame_input`). |
| **Miguel Angel Moreno Páez** | Enemigos, IA y contenido procedural | Spawn de entidades (**spawner**, Hunter), comportamientos de persecución, animaciones de adversarios y efectos cuando impactan otros sistemas (colisiones bala-enemigo, explosiones donde corresponda). |
| **Héctor López** | Motor ECS, ciclo del juego e integración | **Game Loop**, configuración cargada desde `assets/cfg/` (`window.json`, `world.json`), **Service Locator** de recursos, arranque en `main.py` / `GameEngine`, línea base audio/HUD donde aplique (`src/engine/`). |

## Hitos

- Ejecutable **`main.py`** con `GameEngine` y ECS operativo sobre configuración JSON semana 3+ (sprites Hunter, explosiones).

## Notas opcionales

- **Dependencias y herramientas externas** en uso o previstas esta iteración:

  | Tema | Detalle breve |
  |------|-----------------|
  | Bibliotecas Python | **`pygame-ce`**, **`esper`** (ECS), opcional **`pygbag`** (exportación web empaquetada), **`pyinstaller`** (binarios de escritorio) |
  | Configuración / assets | Recursos MISW cohorte oficial resolución de referencia **320 × 256** vía JSON en **`assets/cfg/`** |
  | Repositorio / entrega | Repo Git del proyecto; publicación en **itch.io / Game Jolt** cuando haya build estable. |

- No hay CI/CD automatizado fuera del entorno local por ahora.
