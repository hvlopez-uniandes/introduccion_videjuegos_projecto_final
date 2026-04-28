# Documento de avance — equipo MISW-4407

> Mantener actualizado: **miembros**, **roles** y **lo que cada uno trabajó** en el periodo más reciente (y acumular hitos pasados si el curso lo pide).

## Datos del grupo

- **Nombre del grupo:** Proyecto final Defender — MISW-4407 *(cohorte 2026-12)*
- **Última actualización:** `2026-04-28`

## Integrantes, roles y trabajo realizado

| Miembro | Rol en el equipo | Labor / entregables concretos *(periodo más reciente / estado del repo)* |
|---------|-----------------|--------------------------------------------------------------------------|
| **Leonardo L. Rueda** | Jugador, comandos de entrada y sensación base | Ciclo relacionado con **input → Command**, movimiento/atributos del jugador, límites y animación/UI que dependan de la nave (módulos bajo `src/ecs/` orientados al jugador y `frame_input`). |
| **Miguel Angel Moreno Páez** | Enemigos, IA y contenido procedural | Spawn de entidades (**spawner**, Hunter), comportamientos de persecución, animaciones de adversarios y efectos cuando impactan otros sistemas (colisiones bala-enemigo, explosiones donde corresponda). |
| **Héctor López** | Motor ECS, ciclo del juego e integración | **Game Loop**, configuración cargada desde `assets/cfg/` (`window.json`, `world.json`), **Service Locator** de recursos, arranque en `main.py` / `GameEngine`, línea base audio/HUD donde aplique (`src/engine/`). |

> *Si en una semana concreta el curso pidió granularidad día a día, añádase un párrafo abajo por sprint.*

## Hitos acumulados *(referencia rápida — ampliar si docencia lo exige línea cronológica)*

- Ejecutable **`main.py`** con `GameEngine` y ECS operativo sobre configuración JSON semana 3+ (sprites Hunter, explosiones).

## Notas opcionales

- **Dependencias y herramientas externas** en uso o previstas esta iteración:

  | Tema | Detalle breve |
  |------|-----------------|
  | Bibliotecas Python | **`pygame-ce`**, **`esper`** (ECS), opcional **`pygbag`** (exportación web empaquetada), **`pyinstaller`** (binarios de escritorio) |
  | Configuración / assets | Recursos MISW cohorte oficial resolución de referencia **320 × 256** vía JSON en **`assets/cfg/`** |
  | Repositorio / entrega | Código enlazado en este mismo repo Git; **itch.io / Game Jolt** cuando el build esté cerrado *(pendiente hasta tag final según syllabus)* |

- Sin **pipeline CI/CD** automatizado configurado por ahora más allá del entorno local; si se incorpora más adelante, anótese aquí (GitHub Actions, etc.).
