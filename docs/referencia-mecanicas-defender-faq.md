# Mecánicas Defender (referencia FAQ arcade)

Resumen operativo para el **proyecto MISW** — no sustituye el **enunciado** ni el vídeo de referencia del curso.  
Texto de partida: FAQ de *Defender* (Williams, 1980) en GameFAQs, autor **Kevin Butler** (“War Doc”), v1.03; la reproducción literal del FAQ no está permitida sin permiso del autor — aquí solo hay **hechos de juego** y **cruce con nuestro código**.

---

## 1. Controles arcade (FAQ §6.1) ↔ teclado/ratón actual

| Arcade (original) | Rol | Estado en el repo |
|-------------------|-----|-------------------|
| Joystick **arriba / abajo** | Inclinación vertical | [x] ↑ ↓ *(modo `arcade_defender_flight` en `player.json`)* |
| **Thrust** | Empuje horizontal con inercia | [x] **X / Shift** |
| **Fire** | Láser según frente | [x] **Z / CTRL / clic** |
| **Reverse** | Invierte frente y `vx` | [x] **C** |
| **Smart bomb** | Borrar enemigos | [x] **ESPACIO** + stock; romper **Pods** también suelta swarmers *(comportamiento FAQ típico)* |
| **Hyperspace** | Salto + riesgo | [x] **H** |

---

## 2. Campo de juego (FAQ §6.2)

| Mecánica | Estado |
|---------|--------|
| Mundo **wrap** horizontal | [x] `system_world_wrap` |
| **Radar** / minimapa | [x] `system_draw_radar_defender` (Lander, Mutant, Pod, Bomber, Baiter, Swarmer, bomba…) |
| **Disparos jugador** sin wrap horizontal | [x] `system_bullet_bounds` |
| Volar **por debajo del terreno** — colisión fina relieve | [~] `system_player_terrain_occlusion`: alpha semitransparente bajo la silueta en fase **`defense_arcade` superficie** (sin física contra cada polígono; umbrales `terrain_occlusion_*` en `game_rules.json`) |
| **Mundo más ancho + cámara** que sigue al jugador | [x] `world_play_width_px` ≥ ancho ventana · `system_camera_follow` · sprites con wrap en dibujo (`viewport.world_to_screen_x_positions`) |
| **Planeta perdido ⇒ fase espacio** + **olas** ⇒ **repoblar superficie** | [x] `defense_arcade` en `level_01.json` + `game_state.defense_phase` (`SUP` / `ESP` en HUD) |

---

## 3. Puntuación FAQ (§6.3) ↔ `assets/cfg/game_rules.json`

| Evento FAQ | Puntos FAQ | Clave / notas |
|------------|-----------|---------------|
| Lander | 150 | `score_lander_kill` |
| Mutant | 150 | `score_mutant_kill` |
| Bomber | 250 | `score_bomber_kill` |
| Pod | 1000 | `score_pod_kill` |
| Baiter | 200 | `score_baiter_kill` |
| Swarmer | 150 | `score_swarmer_kill` |
| Rescatar humano del Lander | 500 | `score_human_rescue` |
| Bonus fin de oleada en superficie | humanos × 100 | `wave_bonus_per_human_alive` |
| Limpieza de **ola espacial** | configurable | `score_space_wave_clear_bonus` |
| Volver a tener planeta (tras ciclo espacio) | configurable | `restore_surface_score_bonus` |
| Nave + smart bomb / **10 000** pts | — | Arcade: `score_extra_life_every` |

---

## 4. Jugabilidad clave (FAQ §7)

| Idea | Estado |
|------|--------|
| Mutante / Landers / swarmers IA `CHunterAI` | [x] Varios tipos ECS + puntajes FAQ |
| 10 humanos en `level_01.json` (`astronaut_spawns`), si **se pierden todos** ⇒ **5 oleadas espacio** | [x] `defense_arcade.space_waves` (5 arrays) · transición `system_defense_arcade_transition` |
| Pantalla tras explosión planetaria (sin relieve dibujado) | [x] Mismo borrado visual del relieve **`+`** overlay rojizo pulsante **`planet_explosion_flash_sec`** (`game_state.planet_explosion_flash_remaining`; `_draw_planet_explosion_flash_overlay`) |
| **Baiter** si tardas en la oleada | [x] Sólo fase **`space`** · `baiter_spawn_after_wave_sec` · `system_arcade_baiter_spawn` |
| Bomber deja **hilera de bombas** | [x] `CBomberDrop` + `CTagBomb` |
| Pods → swarmers (+ smart bomb abre Pods) | [x] `CPodCargo` + `spawn_pod_swarm` / smart bomb |

---

## 5. Configuración mínima

- **`assets/cfg/level_01.json`**: bloque **`defense_arcade`** (`surface_enemy_spawn_events`, **`space_waves`**).
- **`assets/cfg/enemies.json`**: `type: mutant | pod | bomber` · `chase_variant: swarmer | baiter`.

---

Actualizar tras nuevos cambios también **`docs/avance-equipo.md`** (checklist paridad arcade).
