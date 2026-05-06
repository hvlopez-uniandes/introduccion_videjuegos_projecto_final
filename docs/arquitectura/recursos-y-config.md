# Recursos y configuración

El **enunciato** y los [recursos oficiales](https://misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-12/) fijan **320 × 256**, JSON de ejemplo y piezas multimedia; este repo debe **crecer** niveles (**`level_01.json`**, **`enemies.json`**, oleadas…) hasta cubrir Defender. Aquí sólo describe **qué lee `config.py` hoy** y cómo enlaza **Service Locator**.

## Carpeta de configuración (`cfg_dir`)

El motor recibe un directorio de JSON en **`GameEngine(cfg_dir=…)`**. En **`main.py`** se puede pasar como argumento:

```text
python main.py assets/cfg
```

Si no pasás ruta, el motor usa por defecto **`assets/cfg/`**. **Todos los `.json`** que lee `config.py` deben estar en esa misma carpeta (`cfg_dir`).

---

## Archivos `.json` presentes hoy en `assets/cfg/`

| Archivo | Contenido observado | Uso en código |
|---------|---------------------|----------------|
| [**`window.json`**](../../assets/cfg/window.json) | `title`, `size.w/h`, `bg_color`, `framerate` | **`load_window_config`** → `pygame.display.set_mode`, título, color de fondo, `Clock` |
| [**`interface.json`**](../../assets/cfg/interface.json) | Colores de texto (p. ej. `title_text_color`, `high_score_color`, …) | **`load_interface_config`** **fusiona** con valores por defecto internos (fuente pixel, textos de título, instrucciones, pausa, HUD del escudo). Las claves que no coincidan con el esquema esperado **no sustituyen** bloques `title` / `pause` salvo que el JSON traiga esos mismos nombres de bloque. |
| [**`world.json`**](../../assets/cfg/world.json) | **Estrellas**, **relleno bajo línea-planeta procedural** (órbita períodica por partida cuando `scenario_seed` es `null`), parallax horizontal vía **`ambient_horizontal_scroll_px_s`** × factores estrella/planeta, `play_area_*` opcional (límites verticales de la nave). | **`load_world_bundle`** → **`create_scenario_entities`** (`scenario_factory`): entidades ECS con `system_scenario_update` / `system_scenario_draw`. Altura borde-planeta observable: **`planet_edge_screen_y`** en `scenario_profile.py`. |

---

## Otros JSON que espera `src/engine/config.py` *(misma carpeta `cfg_dir`)*

Estos nombres los lee el código; si **faltan**, varias funciones tienen **valores por defecto** o **except** — salvo los que hacen `_read_json` **sin** capturar `FileNotFoundError`:

| Archivo | Función | Si falta |
|---------|---------|-----------|
| **`enemies.json`** | `build_enemy_type_defs` | Retorna `{}` (sin definiciones de enemigos). |
| **`level_01.json`** | `build_enemy_spawner_component` | Si falta el archivo → spawner sin eventos, spawn jugador centrado alto (`160`, `100`). |
| **`bullet.json`** | `build_bullet_def` | Default: velocidad 200, sprite `assets/img/bullet.png`, sonido `assets/snd/laser.ogg`. |
| **`player.json`** | `build_player_config` | Default: sprite jugador, clip animación básico, sonidos movimiento/colisión. |
| **`explosion.json`** | `build_explosion_config` | Default: `assets/img/explosion.png` + sonido `assets/snd/explosion.ogg`. |
| **`special.json`** | `load_special_shield_config` | Default: duración/cooldown/radio tecla escudo. |

---

## Service Locator: registro y uso de imágenes / sonidos / fuentes

1. **Registro** (una sola vez al crear el juego): en **`GameEngine._bind_services()`** se instancia **`ServiceLocator`**, se **registran** tres servicios por nombre y se hace **`ServiceLocator.bind(loc)`**:

   | Nombre registrado | Clase | Rol |
   |------------------|-------|-----|
   | `"textures"` | `TextureService` | Carga **`pygame.Surface`** vía **`load_texture`**, con caché en el módulo de texturas. |
   | `"sounds"` | `SoundService` | Carga **`pygame.mixer.Sound`** por **ruta relativa al proyecto**, con **caché por ruta resuelta**. |
   | `"fonts"` | `FontService` | Devuelve **`pygame.font.Font`** por **`(ruta .ttf, tamaño_px)`**, con caché. |

2. **Acceso global:** **`ServiceLocator.current().get("textures")`** (o `"sounds"` / `"fonts"`) después de inicializado desde **`engine`**.

3. **Imágenes (sprites HUD, jugador, balas)**  
   - Rutas típicamente vienen del **JSON** (`player.json`, `bullet.json`, enemigos, etc.).  
   - Se llama **`TextureService.load(ruta_string)`** al armar **`CSurface`** (jugador, balas sprite, animaciones).

4. **Sonidos**  
   - Rutas en componentes/config (`sound_path`, `sound_move`, …).  
   - Muchos efectos pasan por helpers como **`play_sound`** en **`audio_util`**, que acaban usando **`SoundService`** del locator *(revisar implementación para rutas exactas).*

5. **Fuentes**  
   - **`FontService.get(font_path, size_px)`** — por ejemplo texto del HUD y overlay de pausa usando la fuente tipo **`assets/fnt/PressStart2P.ttf`** por defecto en **`load_interface_config`**.

---

## Resolución **320 × 256** px

- En [**`assets/cfg/window.json`**](../../assets/cfg/window.json) está explícito:

```json
"size": { "w": 320, "h": 256 }
```

- Coincide con la **referencia del curso MISW-4407** (resolución arcade *Defender* en material de cohorte).
- **`load_window_config`** usa esos valores tal cual para **`set_mode((w, h))`**: todo el layout lógico (posiciones HUD en `defaults` de `interface`, spawns en JSON de nivel, etc.) debe mantenerse **coherente con ese rectángulo** si se cambian `w/h` más adelante.

---

## Resumen operativo para el equipo

- Centralizar configuración jugable en **`assets/cfg/`** y arrancar siempre con **`python main.py assets/cfg`** (o documentar otro directorio único).
- Completar **`level_01.json`** / **`enemies.json`** según contrato en **`config.py`** para que oleadas y enemigos reflejen el estado real del proyecto.
- **`world.json`**: cuando el sistema de **estrellas/planeta** esté enlazado al motor, cargarlo desde el mismo esquema (lectura única tipo `_read_json(cfg_dir / "world.json")`) para no duplicar constantes.
