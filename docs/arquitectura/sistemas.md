# Sistemas (ECS)

El **enunciato *Defender*** exige muchas mecánicas adicionales (wraparound global, IA Landers/Mutants, balas enemigas, pausa/HUD como en rúbrica, …). Este documento lista el **orden actual** del prototipo (**input → comandos → spawner → IA Hunter → física → colisiones → FX**): al añadir sistemas nuevos, **insertar donde indique la dependencia** y documentarlo aquí (ver también [**`estado-general.md`**](estado-general.md)).

Orden **`≈ orden de llamada`** en **`GameEngine._update()`** cuando **no** hay pausa (`src/engine/game_engine.py`). Los dibujados van en **`_draw`** al final de la sección.

---

## Orden de actualización (simulación)

| # | Sistema | Entrada esperada (componentes / datos) | Efectos |
|---|---------|----------------------------------------|---------|
| 1 | **`system_input_command`** | `CInputCommand` + **pygame** (`key.get_pressed`, ratón) | Rellena **`command_queue`** con comandos (`PlayerLeftCommand`, …, `PlayerFireCommand`). |
| 2 | **`system_execute_commands`** | `CInputCommand`, `CVelocity`, `CPosition`, `CPlayerInputSpeed`, `CTagPlayer` + (`CSurface`+`CAnimation` **o** `CSize` rectángulo); consulta `CEnemySpawner`, `CBulletDef`, cuenta `CTagBullet` | Ejecuta cola **`Command`** → fuerza velocidad jugador y **opcionalmente crea balas** (y **SFX disparo**) usando **`TextureService`**. |
| 3 | **`system_enemy_spawner`** | `CEnemySpawner` *(+ tipos cargados desde config)* | Crea entidades **enemigo** según tiempo/eventos (**posición**, `CSurface`/`CAnimation`, `CTagEnemy`, Hunter con `CHunterAI` donde aplique). |
| 4 | **`system_hunter_ai`** | `CPosition`,`CVelocity`,`CHunterAI`,`CTagHunter` + jugador `CTagPlayer` | Ajusta **velocidad** del Hunter hacia fugas/retorno. |
| 5 | **`system_movement`** | `CPosition`, `CVelocity` (**todas** las entidades con ambos) | Integra **`pos ← pos + vel·Δt`**. |
| 6 | **`system_player_bounds`** | `CPosition`, `CTagPlayer` (+ `CSurface`/`CSize`) | **Clamp** del jugador al rectángulo de pantalla. |
| 7 | **`system_bounce`** | `CPosition`,`CVelocity`,`CSurface`,`CTagEnemy` **sin** `CTagHunter` | Rebote asteroides/simples en **bordes** (Hunter **omitido**). |
| 8 | **`system_bullet_bounds`** | `CPosition`, `CTagBullet` (+ `CSurface`/`CSize`) | Elimina balas **fuera** de pantalla. |
| 9 | **`system_animation`** | `CAnimation` | Avanza **frame** y clip actual genérico. |
| 10 | **`system_player_animation`** | `CVelocity`, `CAnimation`, `CTagPlayer` | Elige clip animación según movimiento. |
| 11 | **`system_hunter_animation`** | `CVelocity`, `CHunterAI`, `CAnimation`, `CTagHunter` | Clips Hunter según IA. |
| 12 | **`system_shield_pulse`** | Jugador: `CShieldSpecial`, `CTagPlayer`, `CPosition` (+ `CSurface` o `CSize`); **evento** vía `consume_shield_pulse`; enemigos: `CPosition`, `CTagEnemy` dentro del radio | Pulso SFX, timers activo/enfriamiento; **elimina enemigos** cercanos y **`spawn_explosion`** cada uno. |
| 13 | **`system_collision_bullet_enemy`** | `CPosition`+ `CTagBullet` vs `CTagEnemy` *(dimensiones por `CSurface`/`CSize`)* | AABB; **elimina** bala+enemigo; **`spawn_explosion`** centro impacto. |
| 14 | **`system_collision_player_enemy`** | `CPosition` jugador/enemigos, `CTag*`; `CPlayerSfx` | Choque jugador–enemigo; **elimina enemigo**; explosión; **SFX** colisión opcional *(helper `spawn_explosion`)*. |
| 15 | **`system_explosion_cleanup`** | `CAnimation`, `CTagExplosion` | Borra entidad cuando animación **`EXPLODE`** termina. |
| 16 | **`system_player_move_sound`** | `CVelocity`, `CPlayerSfx`, `CTagPlayer` | Reproduce sonidos de **motor** jugador si hay velocidad/no. |
| 17 | **`system_shield_hud_refresh`** | `CTagHudDynamic`, `CUiTextStyle`, `CSurface` + `CShieldSpecial` jugador | Actualiza texto **HUD** del escudo tras datos del componente especial. |

> **`spawn_explosion`** (`spawn_explosion.py`) **no** es un sistema del bucle; es una **función** invocada desde colisiones / escudo que lee **`CExplosionConfig`** desde el mundo y crea una entidad explosión nueva.

---

## Orden en render (solo dibujo ECS)

Ejecutado después de **`screen.fill(bg)`** en **`_draw`**:

| # | Sistema | Entrada | Efectos |
|---|---------|---------|---------|
| R1 | **`system_draw`** | `CPosition`+`CSurface`; `CPosition`+`CSize`+`CColor`; orden capas interno | **Blit** sprites y rectángulos al **Surface** principal. |
| R2 | **`system_draw_shield_ring`** | `CPosition`, `CShieldSpecial`, `CTagPlayer`, `CSurface`… | **Dibuja anillo**/aura del escudo encima donde aplique |

Luego el **motor** aplica **`_draw_pause_overlay`** si **`game_state.paused`** (*no ECS*).

---

## Dependencias conocidas entre sistemas

La lista es **manual** ⇒ el **orden importa**:

1. **Entrada antes que física:** `system_input_command` → `system_execute_commands` debe ir **antes** de `system_movement` para que **`CVelocity`** lleve la intención del frame *(y crear balas antes de mover todo)*.

2. **Spawner antes de IA de enemigos recién nacidos:** `system_enemy_spawner` debe preceder **`system_hunter_ai`** cuando en el mismo `Δt` aparecen Hunters.

3. **Movimiento antes de límites y colisiones:** `system_movement` → **`system_*_bounds`** + **`system_bounce`** para que las posiciones ya estén actualizadas; **balas fuera de pantalla** antes de overlap con enemigos evita trabajo extra opcional pero aquí orden es **bounds balas tras movimiento general**.

4. **Animación tras posiciones finas por frame:** los **`*_animation`** conviene tras **movimiento/IA** para reflejar estado actual.

5. **Colisiones destructivas al final (casi):** **bullet–enemy** y **player–enemy** tras posiciones y animaciones del frame; **explosion_cleanup** **después** de crear explosiones en colisiones/pulso.

6. **Feedback de audio/HUD al cierre lógico:** **`system_player_move_sound`** y **`system_shield_hud_refresh`** leen estado **ya actualizado** del frame (escudo, velocidad).

7. **Dibujo:** todo lo anterior determina **qué entidades existen** al llamar **`system_draw`**.

**Regla práctica:** al añadir un sistema nuevo Defender (wraparound mundial, nuevo enemigo), insertarlo donde sus **lecturas escrituras** no rompan supuestos del punto anterior—y documentarlo aquí.
