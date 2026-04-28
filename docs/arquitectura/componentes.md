# Componentes (ECS)

Los **componentes** modelan datos de entidades *Defender* y del prototipo actual (jugador, proyectiles, enemigos con **tags**, HUD, configuración **`CBulletDef`** / **`CExplosionConfig`** en la entidad spawner). El **enunciato** pedirá pronto más roles (**Landers**, **Mutants**, astronautas, partículas acordes): cada nuevo tipo supone **nuevos componentes** o extender tags — mantener esta tabla alineada con **`estado-general.md`** (mapa curso ↔ código).

Convención de archivos en código: **`c_<algo>.py`** en `src/ecs/components/` (clases **PascalCase**). Los tags suelen **no tener campos** (solo discriminan tipo de entidad en consultas **`get_components`**).

---

## Tabla principal

| Componente *(nombre en código)* | Qué datos guarda |
|--------------------------------|-------------------|
| **`CPosition`** | `x`, `y` (**float**) — mundo 2D. |
| **`CVelocity`** | `vx`, `vy` (**float**) — píxeles por segundo (integrado por `system_movement` con Δt). |
| **`CInputCommand`** | `command_queue` (lista de **Command** por frame), `prev_mouse_down` (**bool**) para disparo por flanco. |
| **`CPlayerInputSpeed`** | `pixels_per_second` (**float**) — viene de configuración (**`player.json`** / default). |
| **`CSurface`** | `surface` (**pygame.Surface**), `num_frames`, `frame_w`/`frame_h`, **`area_w`/`area_h`** (collision/dibujo por fotograma). Métodos estáticos `from_text`, `update_from_text`. |
| **`CAnimation`** | `number_frames`, `clips` (dict **`AnimClip`** por nombre), `current_name`, `current_frame`, `subframe_accum`, `finished`. |
| **`AnimClip`** *(en `c_animation.py`)* | Ventana dentro de spritesheet (`start/end`, `framerate`, `loops`). |
| **`CColor`** | `r`, `g`, `b` — rectáculos simples cuando no hay textura (**jugador provisional / balas color**). |
| **`CSize`** | `w`, `h` — tamaño AABB cuando no hay **`CSurface`**. |
| **`CPlayerSfx`** | `move_sound_path`, `collision_sound_path` (strings), `_last_move_sound_ms`; método **`mark_move_sound`**. |
| **`CShieldSpecial`** | **`duration_sec`**, **`cooldown_sec`**, **`radius_px`**, código tecla (**`activation_key`**), **`active_remaining`**, **`cooldown_remaining`**. |

### Tags *(sin datos útiles aparte del tipo)*

| Tag | Rol |
|-----|-----|
| **`CTagPlayer`** | Marca jugador único habitual. |
| **`CTagEnemy`** | Todo enemigo (asteroide Hunter u otro más adelante). |
| **`CTagBullet`** | Proyectil jugador (sprite o rectángulo color). |
| **`CTagHunter`** | Subtipo enemigo con **`CHunterAI`**. |
| **`CTagExplosion`** | VFX temporal de explosion (se borra cuando animación termina). |
| **`CTagHud`** / **`CTagHudDynamic`** | Texto HUD fijo vs texto que **`system_shield_hud_refresh`** puede actualizar cada frame **+** opcional **`CUiTextStyle`**. |

### IA y nivel

| Componente | Qué datos guarda |
|-------------|------------------|
| **`CHunterAI`** | `origin_x`,`origin_y`, `chase_dist`, `return_dist`, `v_chase`, `v_return`, `state`, `sound_chase_path` — máquina mínima perseguir / volver. |
| **`CEnemySpawner`** | `accumulated_time`, lista **`EnemySpawnEvent`** (`time_sec`, tipo, coords, **`fired`**, etc.), **`enemy_types`** (defs cargados desde JSON), `max_bullets`, `player_spawn_x/y`. |

### Globales pegados al “punto singleton” *(misma entidad que el spawner en `game_engine`)*

| Componente | Qué datos guarda |
|-------------|------------------|
| **`CBulletDef`** | Velocidad bala; **sprite** (`image_path`, `num_frames`) **o** rectángulo (`w`,`h`, `rgb`); opcional **`sound_path`**. |
| **`CExplosionConfig`** | `image_path`, `number_frames`, `clips`, `sound_path` — sólo sirve cuando **`spawn_explosion`** necesita crear el FX. |

### UI textual dinámico

| Componente | Qué datos guarda |
|-------------|------------------|
| **`CUiTextStyle`** | Ruta fuente, tamaño, RGB, antialias, cache `_last_rendered` cuando se evita trabajo extra. |

---

## Notas

- **Dos formas visuales** de entidades: **sprite** (`CSurface` [+ opcional `CAnimation`]) **vs** **`CColor` + `CSize`** (**rect collider** viejo ECS semana anterior). **`system_execute_commands`** distingue por presencia **`CSurface`** en el jugador.
- **`CTagHudDynamic`** lleva habitualmente **`CUiTextStyle` + `CSurface`** porque el texto se **re-renderiza** al cambiar el buffer de escudo (**`system_shield_hud_refresh`**).

---

## Combinaciones típicas (“qué lleva cada entidad”)

| Rol en el juego | Componentes habituales |
|-----------------|------------------------|
| **Jugador (sprite)** | `CPosition` + `CVelocity` + `CInputCommand` + `CPlayerInputSpeed` + `CSurface` + `CAnimation` + `CPlayerSfx` + `CShieldSpecial` + **`CTagPlayer`**. *(Si no hay JSON sprite:* `CColor` + `CSize` *en lugar de* `CSurface` + `CAnimation`.) |
| **Bala (sprite)** | `CPosition` + `CVelocity` + `CSurface` + **`CTagBullet`**. |
| **Bala (rect)** | `CPosition` + `CVelocity` + `CSize` + `CColor` + **`CTagBullet`**. |
| **Asteroide / rebote** | `CPosition` + `CVelocity` + `CSurface` + `CAnimation?` + **`CTagEnemy`**. (**`system_bounce`** salta Hunters.) |
| **Hunter IA** | Lo anterior **`CTagEnemy`**, más **`CTagHunter`**, **`CHunterAI`, `CAnimation`**. |
| **Explosion entity** | `CPosition` + `CSurface` + `CAnimation` (clip **EXPLODE**) + **`CTagExplosion`**. |
| **HUD** | `CPosition` + `CSurface` + **`CTagHud`** *o* **`CTagHudDynamic`** *(+ `CUiTextStyle` sólo texto dinámico)*. |
| **Config nivel** *(una sola entidad típico)* | `CEnemySpawner` + en el mismo host `CBulletDef` + `CExplosionConfig` *(como en `game_engine` al crear la entidad spawner)*. |

> **Regla ECS:** las combinaciones útiles son las que algún **sistema** consulta en la práctica; ver orden y dependencias en [**`sistemas.md`**](sistemas.md). Mezclas “huérfanas” no rompen `esper`, pero no aportan comportamiento.
