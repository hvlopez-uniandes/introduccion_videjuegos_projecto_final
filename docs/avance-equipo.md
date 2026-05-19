# Documento de avance

## Datos del grupo

- **Nombre del grupo:** Proyecto final Defender
- **Última actualización:** `2026-05-06` *(lectura rápida: [**Listo / no listo / por revisar**](#estado-explicito-listo-no-listo-falta-revisar); detalle técnico: [**Resumen ejecutivo**](#resumen-hecho-pendiente); informe curso: [`analisis-arquitectura-post-mortem.md`](analisis-arquitectura-post-mortem.md); sustentación: [`guia-sustentacion.md`](guia-sustentacion.md), [`archivos-del-repositorio-sustentacion.md`](archivos-del-repositorio-sustentacion.md).)*

## Meta del producto

El entregable que buscan docencia y rúbricas no es un “inspirado en” *Defender*: es un **clon lo más fiel posible** (proporciones, sensación, comportamientos, HUD, sonido, etc.). Los **avances** ordenan trabajo y merges; cada cierre se juzga así: **¿esto nos acerca a Defender real o a un shooter genérico?**

- **Avances 1–2:** base escenario + nave en ECS (**no** clon cerrado).
- **Avances 3–9:** lo que lleva la **paridad Defender** hasta portal y checklist contra referencia.

### Mapa rápido (9 avances)

| Avance | Entrega *(orientativa)* |
|--------|-------------------------|
| **1** | Escenario desde `world.json` (estrellas, planeta, parallax). |
| **2** | Nave: inercia/feel, láser inicial, Command, pausa estable sobre fondo. |
| **3** | Wrap horizontal y reglas jugador/enemigos según enunciato. |
| **4** | Astronautas en suelo + `planet_edge_screen_y` / offsets. |
| **5** | **Landers** Defender (mover, disparar con jugador en pantalla). |
| **6** | Rapto · **Mutant** arriba · caída humano · puntos rescate/suelo. |
| **7** | Colisiones enunciato completas + misil/proyectiles rivales. |
| **8** | HUD · pausa rúbrica · fanfare · GAME OVER · victoria/olas mínimas. |
| **9** | Menú · audio/anim finales · **itch** + checklist fidelidad vs vídeo. |

<a id="estado-explicito-listo-no-listo-falta-revisar"></a>
### Estado explícito — listo · no listo · falta revisar *(mayo 2026)*

Resumen **en una pantalla** para docencia y sustentación. Lo que sigue en [**Resumen ejecutivo**](#resumen-hecho-pendiente) amplía *dónde* está cada cosa en código/JSON.

| Estado | Qué significa |
|--------|----------------|
| **Listo** | Implementado y usable al correr `python3 main.py` con `assets/cfg/` actual; no requiere acuerdo extra del equipo para demostrarlo. |
| **No listo** | Falta trabajo o entrega reglada (portal, documento, assets en masa, etc.). |
| **Falta revisar** | Puede estar implementado, pero **el equipo no ha cerrado verificación** (playtest, enunciato, audio, build). |

#### Listo

- Motor + **ECS** en bucle estable: escenario (estrellas, planeta procedural, parallax), **mundo ancho** + wrap horizontal, **cámara** y helper de **viewport** para dibujo/culling.
- **Modo arcade Defender** en `player.json`: thrust/reverse, láser, hyperspace, smart bomb con stock, radar, textos HUD; **quemadores** `player_burner_*` si están en JSON.
- **Modo defensa arcade** en `level_01.json`: fase **superficie** vs **oleadas espacio**, transición al perder humanos, **repetición de oleada superficie** con humanos vivos, repoblación tras ciclo espacial según reglas.
- **Enemigos** vía `enemies.json` + spawner: Landers (IA/rapto), mutante, Pod/Swarmer (sprites enlazados), Bomber con **bomba en tira de frames**, Baiter por tiempo de oleada, etc.
- **Colisiones** núcleo (láser, balas rivales, jugador–enemigo, friendly fire astronautas según reglas), **puntuación** centralizada y **MÁX** con persistencia en **`userdata/high_score.json`**.
- **Smart bomb** operativa (sin duplicar entidades bomba, flash, puntos por kill, limpieza de proyectiles en vista donde aplica).
- **Menú** inicial, **pausa**, **GAME OVER** / **victoria** según `game_phase` y reglas del modo arcade.
- **HUD** superior: puntos, MÁX, vidas, bombas, conteo enemigos/mutantes, indicador superficie/ola espacial, alerta rapto · **escala visual** sprites/radar en `game_rules.json` sin romper colisiones.

#### No listo

- **Publicación itch.io** (o canal que defina MISW): build empaquetada + **página** del proyecto (**Avance 9**).
- **Documento checklist** en `docs/`: comparación **enunciato + vídeo referencia** fila a fila (texto grupal firmado o equivalente).
- **Audio/animaciones “en masa”** según cohorte: muchas rutas de SFX/sonidos en JSON siguen **vacías u opcionales**; falta pasada de cierre.
- **Arte/SFX finales** Landers (y otros) donde aún hay placeholder o sonido omitido.
- *(Opcional rúbrica)* **Explosiones diferenciadas** jugador vs enemigo (hoy mismo asset genérico en lo esencial).

#### Falta revisar *(QA / alineación docente — marcar en reunión)*

- [ ] **Playtest wrap** “borde a borde” y **registro breve** vs Defender de referencia (**Avance 3** sigue con ítem abierto en este doc).
- [ ] **Condición de victoria** en modo arcade largo vs lo que pida el profesor (demo finita / informe): hoy el ciclo arcade puede **no** coincidir con “victoria clásica de un solo nivel” — validar con enunciato.
- [ ] **Recorrido FAQ** [`referencia-mecanicas-defender-faq.md`](referencia-mecanicas-defender-faq.md): marcar casillas “implementado / parcial / no” para el informe (no asumir paridad sin leer).
- [ ] **Balance** de `level_01.json` (densidad, tiempos, baiter) tras **sesión grupal** de juego; ajuste iterativo.
- [ ] **Pruebas de audio**: partidas con volumen, rutas rotas, silencios no intencionados.
- [ ] Cuando exista **build web**: probar carga, input y rendimiento en el navegador objetivo (post–itch).

### Referencia arcade (GameFAQs / FAQ Williams)

Las mecánicas detalladas del arcade (thrust, reverse, hyperspace, smart bomb real, radar, 10 humanos / planeta, Baiter por tiempo, Pod/Swarmer/Bomber, bonus oleada ×100, nave+bomb cada 10 000 pts, etc.) están **cruzadas con el código** en:

[**`docs/referencia-mecanicas-defender-faq.md`**](referencia-mecanicas-defender-faq.md)

Úsalo para **huecos conscientes** hacia paridad Defender y para el informe/post-mortem (**no** copiar el FAQ completo por copyright; citar fuente si el profesor lo pide).

**Puntos alineados con tabla §6.3 del FAQ** (JSON): mutant kill **150**, rescate **500** (`game_rules.json`). El resto de filas del FAQ siguen pendientes hasta existan los tipos enemigo/olas.

---

<a id="resumen-hecho-pendiente"></a>
## Resumen ejecutivo — hecho vs pendiente (mayo 2026)

Desglose **por área técnica** y tablas de seguimiento. La lectura **binaria** listo / no listo / revisar está arriba: [**Estado explícito**](#estado-explicito-listo-no-listo-falta-revisar). *(No sustituye el FAQ ni el enunciato.)*

### Ya hecho (iteración reciente sobre el código actual)

| Área | Detalle breve *(dónde tocar si hace falta)* |
|------|---------------------------------------------|
| **Olas Defender arcade** | En **superficie**, al limpiar enemigos con humanos vivos ya **no** se gana la partida: se **repite la oleada** (`system_level_progress` + plantilla superficie). Transición **espacio** al perder todos los astronautas (`system_defense_arcade_transition`). Tras **5 oleadas espacio**, **repoblación** planeta (`_restore_planet_phase`). |
| **Densidad de juego** | `level_01.json`: más eventos de spawn en superficie y espacio; **mutantes también en superficie**; posiciones **X** repartidas en el ancho de mundo (`world_play_width_px` 896). |
| **Spawns escalados en Y** | `build_enemy_spawner_component(..., screen_h_px)`: escalado de **Y** de eventos desde referencia ~256 px como el spawn del jugador (`config.py`, `game_engine.py`). |
| **Smart bomb** | Corrige **KeyError**: bombas llevan **CTagEnemy + CTagBomb** — lista de víctimas **sin duplicar**. Suma **puntos** (`enemy_kill_score`). **Destello** pantalla (`smart_bomb_flash_remaining`). Elimina también **balas/misiles/plasma** rivales visibles cuando aplica. |
| **HUD / marcador** | `esper.clear_cache()` antes de leer conteos · **mutantes** vía **CTagMutant** · **PUNTOS**: scoring unificado láser · bomba · embestida · **MÁX** con `high_score_best_display()` y **`record_high_score_if_best`** al sumar puntos, **GAME OVER**, **victoria**, **nueva partida** y **al cerrar** el juego · persistencia **`userdata/high_score.json`**. Quitada clave **`high_score_max_value`** irrelevante del `interface.json`. |
| **Legibilidad en pantalla** | `sprite_draw_scale` y **`radar_blip_scale`** en `game_rules.json` (escala solo **dibujo**, no colisión). |
| **Propulsión jugador arcade** | `player_burner_idle.png` / `player_burner_moving.png` · componente **`CPlayerArcadeBurner`** · dibujo detrás de la nave (`system_draw`, `system_execute_commands`, `player.json`). |
| **Sprites enemigos** | **Pod** (`enemy_pod.png`) y **Swarmer** (`enemy_swarmer.png`) enlazados en **`enemies.json`** (payload suelta swarmers igual). |
| **Bombas del bomber** | `bomber_bomb.png`: **5 fotogramas** animados en caída · reglas **`bomber_bomb_num_frames`**, **`bomber_bomb_anim_framerate`** · spawn centrado al ancho real del frame (`system_bomber_drop_bombs.py`). **Explosion** ya usaba la misma hoja con clip `EXPLODE`. |

### Pendiente conocido *(priorizado para cierre Avance 9)*  
*Equivale a columna **No listo** + parte de **Falta revisar** en [Estado explícito](#estado-explicito-listo-no-listo-falta-revisar); aquí ordenado por entrega.*

| Tema | Notas |
|------|------|
| **Distribución itch.io** *(Avance 9)* | Build web/pyinstaller según política MISW · página proyecto. |
| **Checklist fidelidad** | Documento grupal vídeo/enunciato en `docs/`. |
| **Playtest wrap** *(Avance 3)* | Registro corto contra referencia Defender (borde‑a‑borde). |
| **Audio cohorte “en masa”** | Muchas rutas de sonido aún opcionales o vacías; repasar `game_rules.json` / `enemy` / placeholders. |
| **Arte Landers/SFX definitivos** | Landers siguen usando sprite cohorte donde aplique · polish **sfx** capturas/alertas. |
| **Explosiones por tipo** | Mismo asset genérico; opcional tinte/colores jugador vs enemigo (Avance 7). |
| **Extras enunciato/bonus** | Tabla HIGH-SCORE inicial ejemplo (21 270) es referencia docente — el juego usa **solo** récord persistente en disco; otros bonus: modo atracción, editor niveles, gamepad, etc. |

---

## Próximos avances *(plan Mayo — entrega 19 may)*

Distribución del código en los **Avances 1 y 2**: **dos frentes paralelos** — **Leonardo L. Rueda** (jugador y comandos) y **Héctor López**, quien también **asume el bloque que tenía Miguel** (spawner, Hunter/IA enemiga, colisiones/explosiones del lado enemigo, etc.). Para **Avance 3 en adelante** se reparten igual por capas de gameplay sin duplicar zonas de archivo.

**Regla anti-choque:** cada uno tiene una **zona de archivos**. En el mismo avance, el otro no edita esa zona sin avisar.

| Quién | Preferencia de archivos *(Avance 1 y 2)* |
|-------|------------------------------------------|
| **Héctor** | Carga de **`world.json`** · **escenario** (estrellas, planeta, parallax) · **motor** (`GameEngine`, configs, Locator, audio base) · línea de **enemigos** que era de Miguel (`system_enemy_spawner`, Hunter/IA, animación enemiga, `enemy_defs`, colisiones donde el enemigo/es bala enemiga sea quien define reglas, explosiones al destruir enemigo, etc.) · en `game_engine.py` el **registro del orden** de sistemas **fondo**, **enemigos** y todo lo que **no** sea jugador/Command. |
| **Leonardo** | `commands.py` · `frame_input.py` · `system_execute_commands.py` · `system_input_command.py` · todos los **`system_player_*`** · componentes **`C*` del jugador** · colisiones **láser del jugador ↔ mundo** y lo que sea **estrictamente nave** (sin tocar IA ni spawner de Miguel/Héctor). |

**Contrato compartido:** rectángulo/zona en **config**; Leonardo solo **lee números**; sin imports al dibujo del planeta.

Sin cerrar hasta **Avance 9** no cuenta como **producto terminado** ante rúbrica típica (portal + contenido Defender). Sin **5–8** no hay sensación de **clon fiel**.

---

### Avance 1 — base escenario *(en paralelo; escenario cargado desde `assets/cfg/` en el repo)*


**Héctor — escenario** *(independiente del avance de Leonardo; el bloque enemigos también es tuyo cuando toque, sin mezclarlo con los `system_player_*`)*

- [x] Leer **`assets/cfg/world.json`** · entidades + sistemas ECS solo para **fondo**.
- [x] Estrellas: `star_colors`, `stars_number`, `stars_blink_rate`, `stars_parallax_factor`.
- [x] Planeta: relieve procedural con **`planet_terrain_line_points`** y **`planet_terrain_colors`** · **seed nueva cada partida** para la forma · **`planet_parallax_factor`** ≠ capa estrellas donde toque el diseño.
- [x] **Orden de sistemas**: fondos **antes** que jugador/sprites encima *(Héctor ajusta el registro del motor solo para estos sistemas nuevos).*  
- [x] Opcional recomendado: en config, **`play_area_top_px`** / **`play_area_bottom_px`** *(o uno solo después)* para que Leonardo no adivine márgenes; si no están aún, Leonardo usa toda la altura de **`window.json`**.

**Leonardo — comandos + nave** *(no toca mundo ni dibuja planeta)*

- [x] **`Command`** estable: pygame → comandos únicamente vía cadena ya prevista (**sin meta en el handler de eventos del motor más allá del encolar**).
- [x] **Inercia / movimiento** del jugador hacia Defender usando **solo** límites de ventana cargados (**320 × 256** como hoy hasta existir play area opcional).
- [x] Sin editar ficheros que Héctor cree para estrellas/planeta.
- [x] Rama propia viable aunque el fondo del `main` aún no sea el final.

**Integración al cerrar Avance 1:** merge del escenario → Leonardo, en **una PR pequeña**, conecta bounds del jugador a `play_area_*` **si ya existen** *(típicamente solo `system_player_bounds` / init)* — **[x]** con `world.json` + `system_player_bounds`.

---

### Avance 2 — nave + comandos coherentes con el escenario *(aún NO es Defender completo)*

**Héctor**

- [x] Una sola fuente para **rectángulo/zona de vuelo** respecto al planeta si el enunciato lo exige · documentar en `docs/arquitectura/recursos-y-config.md` las claves que el jugador **lee de forma indirecta** (solo datos, no dibujo).
- [x] Orden draw/update: **fondo → jugador/enemigos/proyectiles** → HUD → pausa.

**Leonardo**

- [x] **Inercia** acercamiento Defender · **bounds** usando `play_area_*` donde aplique · **disparo** láser/reglas primera iteración Defender · **pausa** con escenario nuevo.

**Conjunto**

- [x] Sin regresiones de FPS ni orden de dibujo · mecánica nueva en **sistemas ECS** y patrones que pide docencia · orden global sistemas en **`game_engine`**: coordinación **Héctor** si hay conflicto.

---

### Avance 3 — mundo horizontal y wrap

- [x] Wrap **horizontal** del espacio donde el enunciato lo pide para entidades pertinentes · **jugador sin wrap vertical** como en Defender.
- [x] Comportamiento de **wrap vertical** en adversarios donde corresponda.
- [x] Límites y lecturas desde **config** o estado mundial para no tener magic numbers repartidos.
- [ ] Prueba borde‑a‑borde manual/playtest registrado contra referencia Defender *(pendiente revisión equipo / vídeo)*.

**Cierre:** el cruce de límites reproduce la sensación arcade, no un clip arbitrario.

---

### Avance 4 — astronautas en superficie

- [x] Entidades ECS de **astronautas** con spawn y **suelo** alineado a la silueta del planeta (**`planet_edge_screen_y`** / offset).
- [x] Ligero movimiento en suelo como pide texto curso · sin atravesar el relleno del planeta donde se prohíba.
- [ ] Opcional provisional: etiqueta cuenta humanos hasta que el HUD final exista (**Avance 8**).

**Cierre:** humanos visibles y creíbles sobre el terreno Defender.

---

### Avance 5 — Landers como en Defender

- [x] Sustituir o ramificar desde Hunter‑prototipo hacia **`Lander`**: patrulla/intercepta según referencia Defender.
- [x] Disparo sólo cuando el jugador entra **en vista** pantalla Defender *(AABB en pantalla)*.
- [x] Todo desde JSON/`enemy_defs`/spawner ECS sin lógica gorda fuera sistemas donde se pueda.
- [ ] Arte final y **sfx** cohorte desde **`assets/`** *(landers en JSON usan rect/colores y sonidos vacíos; sustituir cuando haya arte aprobado)*.

**Cierre:** combate Lander-vs-nave se reconoce como Defender antes de cargar todas las criaturas raras del port.

---

### Avance 6 — rapto · mutante · economía puntos/rescate

- [x] Máquina de estados ECS **captura** (`CAstronautState` + `CLanderAI.capture_phase` + alerta HUD **`! RAPTOR !`** cuando abducen).
- [x] Ciclo ascendente · **Mutant** arriba (`system_lander_mutate_to_alien` + `CTagMutant` + `CHunterAI`).
- [x] Astronauta con **caída** si el Lander muere en ascenso (`release_human_from_dead_lander`).
- [x] Puntos **rescate** al depositar en superficie y penalización friendly-fire (`game_rules.json`).

**Cierre:** la mini‑novela Defender (secuestro → mutación → rescate/destruir) existe en ECS.

---

### Avance 7 — colisiones y disparos rivales cerrados

- [x] Colisiones núcleo: láser↔enemigos (visibles) **sin consumir** el láser · láser↔astros (penaliza) · láser↔balas enemigas · enemigo/bala↔jugador (vidas + respawn spawn nivel).
- [x] **Misil pequeño:** `system_mutant_missile` + `CTagEnemyMissile` + mismo pipeline que `CTagEnemyBullet`.
- [x] Láser ignora enemigos **fuera de pantalla** (viewport 320×256 lógico).
- [ ] Explosiones diferenciadas jugador vs familia enemiga *(mismo asset; mejora opcional con tinte o segundo sprite)*.

**Cierre:** sesión larga sin fallos de hitbox “imposibles de defender” en informe.

---

### Avance 8 — HUD · pausa · fanfare · GAME OVER · victoria/olas

- [x] **HUD** superior: **PUNTOS** · **MÁX** (récord + partida visible) · vidas · bombas · **ENEM** / **MUT** · fase **SUPERFICIE** / **OLA ESP** · bandera **`! RAPTOR !`**.
- [x] **Pausa** (`P` / `ESC`): texto centrado **parpadeante** durante pausa (`pause_overlay_visible`).
- [x] Gancho **fanfare** al salir del menú con `fanfare_sound` opcional en `game_rules.json`.
- [x] Estados **GAME OVER / victoria** mediante `game_phase`.
- [~] **Victoria arcade**: con **defense_arcade** habilitado, **no** hay “victoria” al vaciar sólo superficie con humanos: el ciclo sigue hasta **GAME OVER por vidas**. La condición **`mark_victory`** legacy aplica antes del modo Defender infinito/olas (revisión enunciato vs demo finita si la pide docencia).

**Cierre:** barra superior y estados finales listos para vídeo + rúbrica HUD.

---

### Avance 9 — menú · build público · checklist fidelidad

- [x] **Menú** inicial + estado `game_phase` (`menu` / `play` / `game_over` / `victory`) antes de ECS de partida; reinicio nivel con ENTER.
- [ ] Audio/animaciones finales de cohorte cargadas en masa *(parcial — muchos sfx aún rutas vacías)*.
- [ ] Build **itch** (web/pygbag/pyinstaller según política MISW): **manual** equipo + página portal.
- [ ] **Checklist enunciato** frente a vídeo referencia en `docs/` *(pendiente texto grupal)*.
- [~] **Paridad FAQ arcade**: [x] vuelo thrust/reverse/láser (**Z**); smart bomb (**ESP**) + stock · destello y puntuación por kill; hyperspace (**H**); radar; **repetición oleada superficie** con humanos vivos; ciclo superficie⇄5 oleadas espacio · Pod/Swarmer sprites propios · bomba bomber **5 frames** · Baiter/`mutant`/bonus oleadas según reglas · HIGH-SCORE **`userdata/high_score.json`** + HUD **MÁX** (`high_score_best_display`) · quemador nave (`player_burner_*`) · [x] cámara + mundo ancho (`world_play_width_px`, `viewport`) · [~] túnel/ocultación relieve (`terrain_occlusion_*`) — ver [`referencia-mecanicas-defender-faq.md`](referencia-mecanicas-defender-faq.md).

**Cierre:** clon **fiel** para entrega sumativa y portal.

## Integrantes, roles y trabajo realizado

| Miembro | Rol en el equipo | Labor |
|---------|-----------------|--------------------------------------------------------------------------|
| **Leonardo L. Rueda** | Jugador, comandos de entrada y sensación base | Ciclo **input → Command**, movimiento/atributos del jugador, límites y animación/UI de la nave (`frame_input`, `system_player_*`, sin spawner ni IA enemiga). |
| **Miguel Angel Moreno Páez** | *(En esta iteración el código de enemigos lo lleva Héctor.)* | Coordinación de equipo / revisión cuando pueda; sin duplicar línea de spawner–Hunter en paralelo con Héctor. |
| **Héctor López** | Motor, escenario y **enemigos** (bloque que era de Miguel) | **Game Loop**, `window.json` / `world.json`, **Service Locator**, `GameEngine`; **fondo** estrellas/planeta/parallax; **spawner**, Hunter/IA, animación de adversarios, colisiones explosión del lado enemigo donde corresponda. |

## Hitos

- **Repos actual:** jugabilidad Defender arcade **bastante cerrada** (olas, enemigos, smart bomb, radar, puntos/récord, sprites clave). Pendiente **principal**: **itch** · **checklist fidelidad** en `docs/` · **masa de audio** cohorte · playtest corto wrap · polish explosiones opcional.
- **Meta final:** **Avance 9** con build público + informe/playtest contra enunciato.

---

## Cómo ejecutar y probar el juego (local)

1. **Entorno**  
   Desde la raíz del repo (donde está `main.py`): instala dependencias si hace falta:

   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar**  

   ```bash
   python3 main.py
   ```

   Opcionalmente, otra carpeta de JSON de configuración:

   ```bash
   python3 main.py ruta/a/mi/cfg
   ```

3. **Controles** *(modo **`arcade_defender_flight: true`** en `player.json` — ayuda HUD/inferior)*  

   - **↑ ↓:** cabeceo vertical; **← →:** empuje lateral además del thrust.  
   - **X:** thrust/pulso principal arcade; **C:** invertir sentido (**reverse**).  
   - **Z:** láser.  
   - **ESPACIO:** **smart bomb** (no pulso escudo en este modo).  
   - **H:** hiperespacio.  
   - **P / ESC:** pausa.  

   Sin modo arcade, pueden aplicarse **ratón** / **pulso escudo** según `special.json`; ver `game_engine` y textos menú según configuración cargada.

4. **Menú**  
   Al arrancar aparece pantalla inicial: **ENTER** o **ESPACIO** cargan oleada desde `assets/cfg`. Tras **GAME OVER / victoria**, las mismas teclas —o **ESC**— vuelven al menú.

5. **Tuneo** — `assets/cfg/game_rules.json` (`initial_lives`, puntos, `sprite_draw_scale`, `radar_blip_scale`, smart bomb, bomba bomber, `world_play_width_px`, etc.).

6. **Récord** — `userdata/high_score.json` (`best`); se actualiza al superar el máximo durante la partida y al cerrar partida/nueva run/salida del programa.

7. **Smoke headless:** ver conversación/ci — el bucle público usa `run()` → menú antes de ECS; desarrollo rápido con `SDL_VIDEODRIVER=dummy` es posible inicializando pygame y llamando `_reload_play_world()` + `_update_play()` igual que las pruebas internas del repo.

## Notas opcionales

- **Dependencias y herramientas externas** en uso o previstas esta iteración:

  | Tema | Detalle breve |
  |------|-----------------|
  | Bibliotecas Python | **`pygame-ce`**, **`esper`** (ECS), opcional **`pygbag`** (exportación web empaquetada), **`pyinstaller`** (binarios de escritorio) |
  | Configuración / assets | Recursos MISW cohorte oficial resolución de referencia **320 × 256** vía JSON en **`assets/cfg/`** |
  | Repositorio / entrega | Repo Git del proyecto; publicación en **itch.io / Game Jolt** cuando haya build estable. |

- No hay CI/CD automatizado fuera del entorno local por ahora.
