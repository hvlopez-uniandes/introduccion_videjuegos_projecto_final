# Estado general del proyecto — enunciado MISW-4407 y código

Este documento cruza el **enunciato del curso** (clon tipo *Defender*, **MISW-4407**) con el **estado real del repositorio**, para orientar la planificación hacia la entrega final y el informe de arquitectura.

## Contexto del curso (enunciato)

- **Producto:** reproducción lo más **exacta posible** del arcade *Defender* (Williams, 1981): dimensiones, comportamientos y sensación cercanos al original ([recursos cohorte](https://misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-12/), resolución de referencia típica **320 × 256**).
- **Obligatorios de diseño:** arquitectura **ECS** predominante, **Game Loop**, **Command** (input), **State** / **Escenas** donde aplique, **Service Locator** para assets, **configuración externa** (JSON u equivalente), **despliegue** Python (web/escritorio).
- **Gameplay Defender** (lista amplia en el README raíz): menú, fondo estrellas/planeta con parallax, nave con inercia, disparo láser, oleadas, **Landers / Mutants / astronautas**, wraparound, rapto, colisiones completas, pausa con overlay, fanfare, HUD puntaje/vidas, game over/victoria, itch.io, etc.

## Contexto técnico del repositorio *(qué hay hoy)*

| Elemento | Implementación |
|-----------|----------------|
| Motor | **Python** + **pygame-ce**; bucle en **`GameEngine.run()`** (**`src/engine/game_engine.py`**). |
| ECS | Librería **`esper`** — entidades = ids, lógica en **sistemas** bajo **`src/ecs/systems/`**. |
| Patrones | **Command** (`src/ecs/commands.py`, `system_input_command`, `system_execute_commands`), **Service Locator** (`service_locator.py` + **`TextureService`/`SoundService`/`FontService`**), **config** vía JSON en **`assets/cfg/`** (ver **`recursos-y-config.md`**). |
| Estado / escenas | **Sólo** pausa global (**`game_state.paused`**); **no** hay menú / game over / nivel como escenas sustituibles todavío (ver **`flujo-de-juego.md`**). |
| Arte | Sprites HUD, jugador, enemigos (Hunter/asteroides), explosiones cargados desde paths en JSON o valores por defecto en **`config.py`**. |

## Mapa rápido: enunciato Defender ↔ estado del código

Interpretación orientativa (**✓** bastante cubierto en el código actual · **○** parcial o prototipo · **—** pendiente de encajar en este repo):

| Temática *(enunciato / rúbrica)* | Estado | Notas sobre el codebase |
|----------------------------------|--------|---------------------------|
| **ECS obligatorio** | ✓ | `esper` + mayoría de lógica en sistemas; motor delgado. |
| **Game loop** | ✓ | `_calculate_time` → eventos → `_update` ECS → `_draw`. |
| **Command + input** | ✓ | Cola por frame sobre `CInputCommand`; teclas + clic disparo. |
| **Service Locator + assets** | ✓ | Texturas, sonidos, fuentes registradas en arranque. |
| **Archivos de configuración** | ○ | `window.json`, `interface.json`; **`world.json`** aún sin lectura desde `src/`. Otros (`level_01.json`, `enemies.json`, …) esperados por **`config.py`** — ver **`recursos-y-config.md`**. |
| **Resolución 320 × 256** | ✓ | Fijada en **`assets/cfg/window.json`**. |
| **Menú con título/instrucciones** | ○ | Texto HUD al vuelo vía **`load_interface_config`** + entidades HUD; **no** hay escena menú previa configurable como producto Defender final. |
| **Fondo estrellas / planeta / parallax** | — / ○ | Parámetros en **`world.json`**; **sin cable** al motor en `src/` a fecha de esta documentación. |
| **Nave**: flechas/ratón, inercia, disparo | ○ | Movimiento y disparo con **Command**; la **inercia** tipo arcade completa puede requerir ajuste de modelo fuera de velocidad directa. |
| **Láser** atraviesa enemigos; no daña fuera de pantalla | ○ | Balas con tags; **`system_bullet_bounds`** elimina fuera de vista — reglas finales Defender (láser vs entidades off-screen) **revisar** al portar. |
| **Landers, Mutants, astronautas, rapto** | — | Prototipo con **spawner** + tipos en JSON; en código base hay **Hunter** + enemigos más simples — extender hacia enunciato. |
| **Wraparound** mundo | — | No aparece lógica `wrap` en `src/` todavía. |
| **Pausa** + texto PAUSED | ○ | Pausa + overlay; alinear texto/visibilidad con **rúbrica** vs texto del enunciato. |
| **Fanfare inicio** | — | Puede añadirse vía audio al entrar en partida o al primer frame no pausado. |
| **Explosiones partículas / colores** | ○ | `CExplosionConfig` + animación **EXPLODE**; afinar colores por tipo según Defender. |
| **HUD puntaje / vidas** | ○ | HUD dinámico parcial (escudo); **puntaje/vidas** completos pendientes. |
| **Game over / victoria / olas** | — | Requiere **estado de juego** o **escenas** nuevas + condiciones de nivel. |
| **Publicación itch.io** | ○ | Dependencias `pygbag` / `pyinstaller` en **`requirements.txt`**; pipeline documentado en deuda ([**`arquitectura-ecs.md`**](arquitectura-ecs.md) §3 *Riesgos o deuda*). |

## Diagrama textual del flujo actual (1 frame lógico)

```text
pygame eventos  →  system_input_command  →  system_execute_commands  →  … sistemas ECS …
        ↑ si no hay pausa                                                      ↓
   game_state.paused (tecla P)                                        posiciones / colisiones / FX
                                                                           ↓
                                                              system_draw + anillo escudo + overlay pausa
```

Para el **informe del curso**: usar esta tabla como “línea base” y actualizar filas conforme integren **Defender** completo; citar **rutas de archivos** concretas al explicar decisiones ECS.

---

*Documento vivo: alinear con el **README** raíz del repo y con los **entregables** del syllabus al cerrar el sprint.*
