# Flujo del juego (estados / escenas)

El **curso** pide eventualmente **menú**, **partida**, **game over**, **victoria** y comportamiento tipo *Defender* (ver README raíz). Hoy el motor ejecuta **una sola superficie de juego** con **pausa** global; migrar al flujo completo implica **Escenas / State** adicionales — ver [**`estado-general.md`**](estado-general.md).

## Game loop (`GameEngine.run`)

No hay una clase aparte llamada “GameLoop”: el ciclo está en **`GameEngine.run()`** (`src/engine/game_engine.py`):

| Fase por iteración | Método | Rol |
|--------------------|--------|-----|
| Tiempo | `_calculate_time()` | `Clock.tick(framerate)` → **`delta_time`** en segundos para sistemas ECS. |
| Entrada OS | `_process_events()` | `QUIT`, tecla **`P`** → pausa (`game_state.toggle_pause`), tecla escudo → `request_shield_pulse`. |
| Actualización ECS | `_update()` | Si **`game_state.paused`** → **no ejecuta sistemas de simulación** (sale al instante). |
| Render | `_draw()` | Limpiar pantalla → sistemas de dibujo → opcional overlay de pausa → **`flip()`**. |
| Salida | `_clean()` | `pygame.quit()` cuando `is_running` es falso. |

Es el **único flujo principal**: arranca pygame + ECS en **`_create()`**, luego entra el **`while self.is_running`** anterior.

---

## Estado global: “jugando” vs “pausado”

- **`src/engine/game_state.py`**: variable global **`paused`** (`bool`) y **`toggle_pause` / `set_paused`**.
- **No** es el patrón **State** completo (no hay clases `PlayingState` / `PausedState`); es un **interruptor** leído en **`_update`** y **`_draw`**.
- Con **pausa activa**:
  - **`_update`** no corre ningún sistema ECS → el “mundo” queda congelado en el último frame de lógica.
  - **`_draw`** **sí** redibuja escena + overlay semitransparente + texto centrado configurado en **`interface.json` / defaults** (`_draw_pause_overlay`).

**Menú inicial, game over, victoria** como estados o escenas **separados** **no existen** en este código todavío: el juego parte directamente en **`_create()`** con entidades jugador HUD spawner montadas. Eso será extensión natural del proyecto Defender (ver **`arquitectura-ecs.md`** §3 *Riesgos / deuda*).

---

## Patrón Escena en este repo

- **Formalmente:** no hay gestor tipo **`SceneManager`**, **`push/pop` de escenas** ni entidades cargadas sólo para “Menú”.
- **`GameEngine.run()`** equivaldría conceptualmente a **una única escena** (“partida en curso”) más el overlay opcional pausa (**subestado visual**, no nueva escena ECS).

---

## Frame típico cuando **no** hay pausa

Orden fijo dentro **`_update()`** *(misma secuencia que en código; aquí agrupado por tema)*:

1. Entrada→acción: `system_input_command` → `system_execute_commands`.
2. Contenido dinámico: `system_enemy_spawner(dt)` · `system_hunter_ai`.
3. Física básica: `system_movement` · límites jugador/balas · `system_bounce` (enemigos).
4. Animación: `system_animation`, `system_player_animation`, `system_hunter_animation`, pulsos **`system_shield_pulse`**.
5. Colisiones / limpieza: bala-enemigo, jugador-enemigo, **`system_explosion_cleanup`**.
6. Retroalimentación: sonidos jugador **`system_player_move_sound`**, HUD escudo **`system_shield_hud_refresh`**.

Luego **`_draw`**: `fill` · `system_draw` · anillo escudo **`system_draw_shield_ring`** · overlay pausa si aplica.

---

## Resumen

| Pregunta | Respuesta en el código actual |
|----------|-------------------------------|
| ¿**State** patrón completo? | Solo el bit **pausado** vía módulo **`game_state`**. |
| ¿**Escenas** múltiples? | **No**; una sola “escena” de juego + overlay pausa. |
| ¿Dónde vive el **game loop**? | **`GameEngine.run()`** — bucle clásico **input → update → render**. |

Para el informe del curso: planificar **menú / game over** implicará introducir **estados o escenas** adicionales encima o dentro de este esqueleto.
