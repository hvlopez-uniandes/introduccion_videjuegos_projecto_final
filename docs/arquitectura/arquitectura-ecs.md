# Arquitectura ECS — visión técnica

Documentación del diseño **ECS** *(biblioteca `esper`)* y patrones relacionados aplicados en el código. *(Antes estaba fragmentada en otro `README`; ahora sólo existe **un [`README`](../../README.md) en la raíz del repo**.)*

## Enunciato MISW-4407 y este repositorio

El curso pide una **réplica cercana de *Defender*** con ECS, patrones vistos en clase (entre ellos Game Loop, Command, Service Locator, configuración externa), despliegue en **Python** y un conjunto grande de **mecánicas de juego** (menú, fondo parallax, wraparound, Landers/Mutants/astronautas, HUD, itch.io… — ver tabla en el [**README**](../../README.md) raíz).

**Este codebase** ya implementa la **columna vertebral técnica** (motor **`GameEngine`**, **esper**, entrada por **Command**, carga multimedia por **Service Locator**, JSON bajo **`assets/cfg/`**, pausa, spawner/Hunter/colisiones/explosiones). Parte del contenido Defender del enunciato **aún está en evolución o por integrar**: el **cruce requerimiento ↔ línea de código / archivo** está descrito en [**`estado-general.md`**](estado-general.md) — actualizar ese archivo al cerrar cada hito importante.

## Índice de documentos en esta carpeta

| Tema | Archivo |
|------|---------|
| **Enunciato ↔ código** (mapa de cobertura) | [**estado-general.md**](estado-general.md) |
| **Visión ECS, Command, pausa, servicios, deuda** | **§§1–3 más abajo** *(este documento)* |
| Listado por componentes | [**componentes.md**](componentes.md) |
| Listado por sistemas y orden de tick | [**sistemas.md**](sistemas.md) |
| Service Locator + JSON + rutas assets | [**recursos-y-config.md**](recursos-y-config.md) |
| Game loop, pausa, ausencia formal de escenas | [**flujo-de-juego.md**](flujo-de-juego.md) |

---

## 1. Idea general ECS

### ¿Qué entidades representamos y qué encaja en {componentes + sistemas}?

Usamos **`esper`** como *world*: las **entidades** son IDs; cada una lleva **componentes** (solo datos); el comportamiento repetible está en **sistemas** *(funciones que consultan `get_components` / `get_component`)*.

En la práctica del repo aparecen, entre otras:

| Tipo conceptual | Ejemplos de componentes | Sistemas (no exhaustivo) |
|-----------------|-------------------------|---------------------------|
| Jugador | `CPosition`, `CVelocity`, `CSurface`, `CAnimation`, `CInputCommand`, `CPlayerInputSpeed`, `CPlayerSfx`, `CShieldSpecial`, `CTagPlayer` | `system_input_command` → `system_execute_commands` → movimiento, límites, animación jugador, SFX, escudo HUD |
| HUD / texto | `CTagHud`, `CTagHudDynamic`, `CUiTextStyle`, etc. | `system_draw`, `system_shield_hud_refresh` |
| Oleadas / parámetros | Entidad portadora de `CEnemySpawner`, más `CBulletDef`, `CExplosionConfig` donde existan | `system_enemy_spawner`; disparo ligado también a `system_execute_commands` |
| Enemigos, balas, explosiones | `CTagEnemy`, `CHunterAI`, `CTagBullet`, `CTagExplosion`, … | Hunter IA, bounce, límites de balas, animaciones enemigos, colisiones, explosiones |

**Regla:** un sistema ≈ una responsabilidad por frame *(entrada→comando, física simple, dibujo…)*.

### ¿Cómo se comunican comandos entrada ↔ ejecución (patrón Command)?

1. **`system_input_command`** lee teclas y ratón; por cada **`CInputCommand`** rellena `command_queue` con instancias **`PlayerLeftCommand`** … **`PlayerFireCommand(mx,my)`** (`system_input_command.py`).
2. **`system_execute_commands`** arma un **`CommandContext`**, ejecuta `execute(ctx)` en cada comando y obtiene dirección de movimiento y opcional disparo (**`commands.py`** + **`system_execute_commands.py`**).

Es un **Command reducido**: sólo movimiento/disparo; pausa **no** pasa por la cola (va por **`game_state`**).

### ¿`GameState`, State y escenas?

- **`game_state.py`**: bandera global **`paused`** + `toggle_pause` / `set_paused`.
- **`GameEngine`**: tecla **`P`** alterna pausa; **`_update`** retorna si `paused` *(ECS no avanza)*; **`_draw`** sí pinta escena + overlay de pausa con **`FontService`** del Locator.
- Equivalente a un **trozo del patrón State** (solo “pausado vs jugando”), **sin** objetos `State` ni stack de escenas.

### ¿Patrón Escenas?

**No está modelado formalmente.** `GameEngine.run()` es una sola “escena”: no hay **`MenuScene` / `PlayScene`** separadas como subsistemas. Para el proyecto final Defender (menú, game over…) habrá que **añadir una capa de escenas** o estados más ricos (**deuda**, §3).

### ¿Dónde vive Service locator cargando sprites y sonidos?

En **`GameEngine._bind_services()`**:

- **`ServiceLocator`** registra **`textures`** → `TextureService` (**`textures.load_texture`**),
- **`sounds`** → **`SoundService`** (**`pygame.mixer.Sound`**, caché por ruta),
- **`fonts`** → **`FontService`**.

Acceso típico: **`ServiceLocator.current().get("textures").load(rel_path)`** en montaje del jugador y proyectiles sprite; **`play_sound`** / utilidades audio para SFX; **`fonts.get`** para HUD y texto PAUSA (**`game_engine.py`**, **`resource_services.py`**).

---

## 2. Decisiones de diseño hasta la fecha

- **ECS con `esper`** para no concentrar todo en jerarquías OO de “GameObject”; spawn de entidades nuevas desde sistemas cuando hace falta *(balas, explosion)*.
- **Separar entrada (`system_input_command`) de aplicación física/disparos (`system_execute_commands`)** mediante **Command + contexto**.
- **Datos de nivel / ventana desde JSON** bajo **`cfg_dir`** cargados en **`_create`** *(ventana, spawner enemigos, velocidades, rutas multimedia)* — cambiar comportamiento tocando configuración antes que recompilar lógica duplicada.
- **Pausa antes del bloque ECS `update`** para no integrar velocidades fantasma delta acumulativo.

---

## 3. Riesgos o deuda técnica conocidos

| Riesgo / deuda | Detalle breve |
|----------------|----------------|
| Sin **grafo de escenas** formal | Falta menú inicial / pantallas Defender como piezas sustituibles; todo arranca dentro **`GameEngine._create`** en una única rutina larga. |
| **`paused` global** mutable | Posible refactor a objeto controlador de estado para tests y menor acoplamiento modular. |
| Orden manual en **`GameEngine._update`** | Lista fija tipo “pipeline”; nuevos sistemas Defender deben insertarse sin romper dependencias ocultas — documentar en **`sistemas.md`** al crecer. |
| Colisiones **AABB/simples** | Adecuado para prototipo semanal; validar contra requisitos finales Defender (wraparound fricción láser más complejo quizá distinto modelo). |
| Deploy web itch | **`pygbag`** / **`pyinstaller`** están en **`requirements`**; falta playbook o CI reproducible documentado cuando el equipo lo tenga *(añadir al cerrar ciclo itch.io).* |
