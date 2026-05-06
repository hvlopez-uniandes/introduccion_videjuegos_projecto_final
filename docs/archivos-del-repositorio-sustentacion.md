# Archivos del repositorio — qué son y por qué están *(sustentación)*

Documento para **exponer en viva voz** cómo está organizado el código: cada bloque cumple un rol en el clon *Defender* sobre **Pygame + ECS (`esper`)**. No sustituye [`guia-sustentacion.md`](guia-sustentacion.md) ni [`avance-equipo.md`](avance-equipo.md); **profundiza en nombres de archivo**.

**Idea clave:** separar **motor** (`src/engine`) de **juego declarativo ECS** (`src/ecs`). El motor carga JSON, crea el mundo y fija el orden del bucle; los **sistemas** aplican reglas por frame; los **componentes** son datos pegados a entidades.

---

## 1. Raíz del proyecto

| Archivo / carpeta | Para qué existe |
|-------------------|----------------|
| `main.py` | Punto de entrada mínimo: instancia `GameEngine` y ejecuta `run()`. Así el profesor ve dónde arranca todo. |
| `requirements.txt` | Dependencias del curso: **pygame-ce**, **esper**, herramientas de empaquetado (**pygbag**, **pyinstaller**) cuando toque entrega web/binario. |
| `README.md` | Instrucciones rápidas para humanos (si están actualizadas por el equipo). |
| `assets/` | Arte, fuentes y **JSON de configuración** (`assets/cfg/`); rutas relativas desde la raíz del repo. |
| `userdata/` | Datos generados en ejecución (**p. ej.** `high_score.json`); no suele versionarse el contenido, sí la carpeta si el curso lo pide. |
| `src/` | Código fuente del motor y del ECS. |

---

## 2. `src/engine/` — motor y datos globales de sesión

Archivos que **no** son sistemas ECS pero **orquestan** la partida.

| Archivo | Qué hace | Por qué lo creamos |
|---------|----------|---------------------|
| `game_engine.py` | Ventana Pygame, **fases** (`menu` / `play` / game over / victoria), `_reload_play_world`, orden de **update/draw** (`_update_play`, `_draw_play`), HUD superior, menú, overlays explosión/smart bomb. | Un solo lugar donde se ve el **game loop** y las dependencias entre sistemas (requisito típico de sustentación). |
| `game_state.py` | Variables globales de sesión: puntaje, vidas, fase defensa arcade, cámara, flashes, **high score** persistido, helpers `add_score`, `get_rule`, etc. | Evita pasar 20 parámetros por sistema; estado **transversal** (HUD, nivel, transiciones). |
| `config.py` | Lee **`assets/cfg/*.json`**, construye dataclasses/objetos Python: reglas, jugador, mundo, spawner con eventos, defs de enemigos, explosión, poblar astronautas… | **Datos del juego fuera del código** para balancear sin recompilar (alineado a rúbricas MISW). |
| `enemy_defs.py` | Tipos de datos para definiciones de enemigos (**Lander**, **Hunter**, **Pod**, **Bomber**, **Baiter**, variantes mutante, etc.) que `config.py` rellena desde JSON. | Una **tabla de especies** clara para el informe y para no mezclar parsing con IA. |
| `enemy_kill_score.py` | Función central **`score_for_destroyed_enemy`** (y similar) usada por láser, smart bomb, embestida. | Un solo criterio de **puntuación** ante docencia (“¿dónde suman puntos?”). |
| `service_locator.py` | Registro singleton: `textures`, `sounds`, `fonts`. | **Inyección simple** sin framework; los sistemas piden recursos por nombre. |
| `resource_services.py` | Implementaciones concretas que cargan archivos bajo la raíz del proyecto. | Encapsula Pygame `image.load` / `font` / `mixer` con política de rutas. |
| `paths.py` | `PROJECT_ROOT` y utilidades de rutas. | Imports y tests consistentes sin depender del CWD. |
| `viewport.py` | `horiz_overlaps_viewport`, `world_to_screen_x_positions`, AABB vs cámara + **wrap** de mundo ancho. | Defender necesita **“sólo lo visible”** para láser smart bomb y dibujo sin duplicar lógica en cada sistema. |
| `scenario_factory.py` | Crea entidades ECS del **fondo**: estrellas y perfil del planeta procedural (`build_periodic_offsets`, etc.). | Separar **generación de escenario** del `GameEngine` para testear y documentar. |
| `scenario_profile.py` | **`planet_edge_screen_y`**: altura del relieve en una X de pantalla (interpolación sobre `offsets`). | Astronautas y landers **tocan el suelo** alineado al dibujo del planeta, no a un valor fijo. |
| `scenario_query.py` | `get_planet_profile()` vía ECS. | Helpers de lectura donde hace falta el planeta sin acoplar a `game_engine`. |
| `frame_input.py` | Cola / flags de pedidos (**hyperspace**, **smart bomb**, escudo) desde teclas. | Desacoplar **evento** de **ejecución** en el frame correcto (orden ECS). |
| `input_keys.py` | Mapeo string → constante Pygame (p. ej. tecla escudo desde JSON). | Config legible en JSON sin números mágicos de tecla. |
| `textures.py` | Cache global de superficies y `clear_texture_cache` al recargar nivel. | Rendimiento y coherencia al cambiar partida/menú. |
| `audio_util.py` | `play_sound` con volumen tolerante a fallos. | Llamadas de una línea desde sistemas sin repetir try/except. |
| `__init__.py` | Paquete Python `engine`. | Permite `from src.engine...`. |

---

## 3. `src/ecs/components/` — datos por entidad

Cada archivo define **structs**/`dataclass`/clases livianas que **esper** asocia a entidades.

### 3.1 Transformación y dibujo genéricos

| Archivo | Rol |
|---------|-----|
| `c_position.py` | Posición mundo/pantalla según uso. |
| `c_velocity.py` | Velocidad para integración en `system_movement`. |
| `c_size.py` | Caja cuando no hay sprite (rectángulos). |
| `c_color.py` | Color cuando no hay sprite. |
| `c_surface.py` | Superficie Pygame + metadatos (p. ej. frames horizontales). |
| `c_animation.py` | Clips, frame actual, `CAnimation`. |
| `c_ui_text_style.py` | Estilo para regenerar texto HUD dinámico. |

### 3.2 Jugador y controles

| Archivo | Rol |
|---------|-----|
| `c_input_command.py` | Comandos lógicos generados por input. |
| `c_player_input_speed.py` | Velocidad máxima / suavizado (modo clásico). |
| `c_arcade_defender_flight.py` | Parámetros de vuelo arcade (thrust, drag, facing…). |
| `c_player_arcade_burner.py` | Sprites y estado del **quemador** detrás de la nave. |
| `c_player_sfx.py` | Rutas de sonido movimiento/colisión del jugador. |
| `c_shield_special.py` | Escudo **no arcade** (duración, cooldown, tecla). |

### 3.3 Identidad y escenario

| Archivo | Rol |
|---------|-----|
| `c_tags.py` | Marcadores **CTagPlayer**, **CTagEnemy**, **CTagMutant**, **CTagLander**, **CTagHud**, etc. — filtran queries ECS. |
| `c_scenario.py` | Componentes de **estrellas** y **perfil planetario** (offsets, scroll, colores). |

### 3.4 Proyectiles, explosiones, spawner

| Archivo | Rol |
|---------|-----|
| `c_bullet_def.py` | Definición del disparo del jugador desde `bullet.json`. |
| `c_explosion_config.py` | Config animación/ruta explosión. |
| `c_enemy_spawner.py` | Lista de eventos tiempo→enemigo; clonado para repetir oleadas. |

### 3.5 IA y enemigos específicos

| Archivo | Rol |
|---------|-----|
| `c_hunter_ai.py` | Parámetros IA “cazador” / mutante genérico. |
| `c_lander_ai.py` | Fases de vuelo, rapto, disparo lander. |
| `c_pod_cargo.py` | Capsula que suelta swarmers. |
| `c_bomber_drop.py` | Estado de fila bomber + intervalo de bombas. |
| `c_missile_burst.py` | Disparo secundario mutante (misil). |

### 3.6 Astronautas

| Archivo | Rol |
|---------|-----|
| `c_astronaut.py` | Huella / datos visuales en suelo. |
| `c_astronaut_state.py` | Máquina de estados: libre, cargado, caída, etc. |

### 3.7 Paquete

| Archivo | Rol |
|---------|-----|
| `__init__.py` | Marca `components` como paquete. |

---

## 4. `src/ecs/systems/` — lógica por frame

Cada archivo es una **función** (o conjunto pequeño) invocada desde `game_engine` en un **orden fijo**.

### 4.1 Entrada y comandos

| Archivo | Rol |
|---------|-----|
| `system_input_command.py` | Pygame → rellena `CInputCommand`. |
| `system_execute_commands.py` | Comandos → thrust/disparo/smart bomb/escudo según componentes del jugador. |

### 4.2 Arcade Defender (habilidades)

| Archivo | Rol |
|---------|-----|
| `system_arcade_hyperspace.py` | Teletransporte con riesgo/bounds. |
| `system_arcade_smart_bomb.py` | Destrucción en vista, puntuación, flash, limpieza de proyectiles. |
| `system_arcade_wave_time.py` | Temporiza oleadas / fases espaciales. |
| `system_arcade_baiter_spawn.py` | Aparece baiter si la oleada se alarga (reglas JSON). |

### 4.3 Escenario y cámara

| Archivo | Rol |
|---------|-----|
| `system_scenario_update.py` | Scroll estrellas/planeta. |
| `system_scenario_draw.py` | Dibuja fondo. |
| `system_camera_follow.py` | Actualiza `camera_scroll_x` en `game_state`. |
| `system_player_terrain_occlusion.py` | Flag de jugador oculto tras relieve (alpha/túnel). |

### 4.4 Spawner y enemigos

| Archivo | Rol |
|---------|-----|
| `system_enemy_spawner.py` | Dispara eventos de `CEnemySpawner` en el tiempo de partida. |
| `system_hunter_ai.py` | IA cazador/mutante. |
| `system_hunter_animation.py` | Animación enemigos tipo hunter. |
| `system_lander_ai.py` | Patrulla, disparo en vista, fases de captura. |
| `system_lander_mutation.py` | Fin de ascenso → mutante (integra con `mutate_spawn`). |
| `system_mutant_missile.py` | Misiles del mutante. |
| `system_bomber_drop_bombs.py` | Bombas animadas en caída. |
| `spawn_pod_swarm.py` | Lógica de soltar swarmers desde pod. |
| `mutate_spawn.py` | **`spawn_mutant_at`**: crea entidad mutante con sprite/reglas. |

### 4.5 Astronautas y rescate

| Archivo | Rol |
|---------|-----|
| `system_astronaut_gravity_and_land.py` | Gravedad y resolución de aterrizaje. |
| `system_astronaut_snap.py` | Alineación al terreno. |
| `system_astronaut_carried_sync.py` | Posición con lander que carga humano. |
| `system_astronaut_rescue_ship.py` | Recogida y depósito en superficie (puntos). |

### 4.6 Movimiento y límites

| Archivo | Rol |
|---------|-----|
| `system_movement.py` | Integra `CVelocity` → `CPosition`. |
| `system_world_wrap.py` | Wrap horizontal (y vertical donde aplica). |
| `system_player_bounds.py` | Límites del jugador al área de vuelo. |
| `system_bullet_bounds.py` | Destruye balas fuera de mundo/pantalla. |
| `system_bounce.py` | Rebotes legacy/ajustes de enemigos. |

### 4.7 Colisiones

| Archivo | Rol |
|---------|-----|
| `system_collision_bullet_enemy.py` | Láser jugador ↔ enemigos visibles. |
| `system_collision_bullet_enemy_bullet.py` | Láser ↔ disparos enemigos. |
| `system_collision_bullet_astronaut.py` | Friendly fire / penalización. |
| `system_collision_player_enemy.py` | Embestida nave ↔ enemigo. |
| `system_collision_enemy_bullet_player.py` | Daño al jugador. |

### 4.8 Progresión de nivel (Defender arcade)

| Archivo | Rol |
|---------|-----|
| `system_defense_arcade_transition.py` | Cambia superficie ↔ espacio según humanos vivos. |
| `system_level_progress.py` | Fin de oleada, bonus, repetición superficie, victoria/game over. |

### 4.9 Animación, FX, limpieza

| Archivo | Rol |
|---------|-----|
| `system_animation.py` | Avanza clips genéricos. |
| `system_player_animation.py` | Estado visual del jugador. |
| `system_explosion_cleanup.py` | Borra entidades de explosión terminadas. |
| `spawn_explosion.py` | Crea explosión donde hace falta (helper usado por colisiones/bomba). |

### 4.10 Dibujo de entidades e interfaz jugable

| Archivo | Rol |
|---------|-----|
| `system_draw.py` | Sprites, rectáculos, burner detrás del jugador, orden general. |
| `system_draw_radar_defender.py` | Radar inferior tipo Defender. |
| `system_draw_shield_ring.py` | Anillo de escudo (modo no arcade). |

### 4.11 Escudo y audio jugador auxiliar

| Archivo | Rol |
|---------|-----|
| `system_shield_pulse.py` | Lógica temporal del escudo. |
| `system_shield_hud_refresh.py` | Texto “pulso escudo” / estado. |
| `system_player_move_sound.py` | SFX de movimiento. |

### 4.12 Paquete

| Archivo | Rol |
|---------|-----|
| `__init__.py` | Paquete `systems`. |

---

## 5. `src/ecs/commands.py`

| Archivo | Rol |
|---------|-----|
| `commands.py` | Tipos **`Command`** (datos inmutables o enums) que el pipeline input → ejecutar interpreta. | **Patrón docente**: separar **intención** del jugador del **efecto** sobre el ECS. |

---

## 6. `assets/cfg/` — configuración declarativa

| JSON | Qué parametriza | Por qué está separado del `.py` |
|------|-----------------|-----------------------------------|
| `window.json` | Título, tamaño, FPS, color fondo. | Cambiar resolución sin tocar código. |
| `world.json` | Estrellas, planeta (puntos/colores), parallax, a veces ancho mundo / play area. | Arte de fondo **data‑driven**. |
| `game_rules.json` | Vidas, puntos por kill/rescate, smart bombs, escalas dibujo radar, bomber frames, tiempo flash, mundo ancho (`world_play_width_px`), etc. | **Balance** y reglas de negocio en un solo lugar. |
| `player.json` | Sprite o rect, velocidades, **arcade_defender_flight**, rutas burner. | Dos modos de juego sin bifurcar el motor en exceso. |
| `enemies.json` | Tabla de tipos: lander, hunter, pod, bomber, baiter, mutante… | Diseñar enemigos como **catálogo**. |
| `level_01.json` | Spawns por tiempo, `defense_arcade` (superficie + oleadas espacio), astronautas. | Nivel = **datos**, no código. |
| `bullet.json` | Velocidad/tamaño/imagen del láser. | Ajuste feel del disparo. |
| `explosion.json` | Sprite y clips de explosión. | Coherencia visual de destrucción. |
| `interface.json` | Fuentes, textos HUD/menú. | Localización y estilo sin recompilar. |
| `special.json` | Escudo (duración, tecla) cuando **no** es modo arcade. | Regla “especial” aislada. |

---

## 7. `docs/` — material de equipo y sustentación

| Ruta *(ejemplos)* | Uso |
|-------------------|-----|
| `avance-equipo.md` | Bitácora, avances MISW, **listo / no listo / revisar**. |
| `guia-sustentacion.md` | Guion conceptual motor + ECS para oral. |
| `archivos-del-repositorio-sustentacion.md` | **Este archivo**: mapa archivo↔motivo. |
| `referencia-mecanicas-defender-faq.md` | Cruce con FAQ Williams (sin copiar texto con copyright). |
| `arquitectura/` | Notas más profundas (flujo, componentes, sistemas). |
| `enunciado.md` | Enlace o texto del curso. |

---

## 8. Cómo usar esto en la sustentación (30 s)

1. **“Entrada”** → `main.py` → `GameEngine`.  
2. **“Datos”** → `assets/cfg` + `config.py`.  
3. **“Comportamiento”** → `src/ecs/systems/*` llamados en orden desde `game_engine.py`.  
4. **“Estado que cruza todo”** → `game_state.py` + algunos helpers `viewport.py` / `enemy_kill_score.py`.

Si preguntan *“¿por tantos archivos?”*: **un archivo ≈ una responsabilidad** — facilita pruebas, merge en equipo y localizar bugs (“el fallo está en colisión X” / “el lander en `system_lander_ai`”).

---

*Documento para sustentación — mayo 2026. Si se añaden sistemas, actualizar la sección 4 y el orden real en `game_engine.py`.*
