# Guía para leer en el vídeo — Proyecto final Defender

**Uso:** una persona lee este documento en voz alta mientras otra persona (o la misma, en edición) muestra pantalla: menú, gameplay, carpetas del repo y archivos JSON.  
**Duración al leer con calma:** unos 14–18 minutos. Si el curso pide menos tiempo, acelera la §2 o resume tablas de la §5.  
**Enlaces:** [itch.io](https://hvmlopez.itch.io/projecto-final-introduccion-videjuegos) · [GitHub](https://github.com/hvlopez-uniandes/introduccion_videjuegos_projecto_final)

---

## PARTE 1 — Presentación del juego y del equipo

**[Pantalla: página itch.io o menú del juego]**

Hola. En este vídeo presentamos el **Proyecto final Defender**, desarrollado para el curso **Introducción al desarrollo de videojuegos — MISW-4407** de la Universidad de los Andes.

El encargo del curso no era hacer un shooter genérico “inspirado en” un clásico: buscamos una **réplica lo más fiel posible** al arcade **Defender** de Williams, de 1981. Eso implica sensación de vuelo lateral, defender humanos en un planeta, enemigos con roles distintos — Landers, mutantes, cápsulas Pod, Swarmers, bombarderos, Baiters —, economía de puntos, smart bombs, radar y un mundo **más ancho que la pantalla**, con cámara que sigue a la nave.

A nivel técnico el juego está hecho en **Python**, con **pygame-ce** para gráficos y audio, y **esper** como librería **ECS** — Entity Component System. La configuración del juego — ventana, reglas, enemigos, oleadas — vive en archivos **JSON** bajo `assets/cfg/`, no dispersa en constantes mágicas por todo el código.

Antes de entrar en arquitectura, presentamos al equipo:

**Leonardo L. Rueda** se encargó de todo lo relacionado con el **jugador**: lectura del teclado, patrón **Command**, movimiento, límites en pantalla, animación de la nave y la cadena de sistemas `system_player_*`. Su zona de código evita el spawner y la inteligencia artificial enemiga, para no pisar el trabajo del motor.

**Héctor López** asumió el **motor del juego** — el archivo `GameEngine` en `src/engine/game_engine.py` —, el **escenario** con estrellas y planeta procedural, el **spawner** de enemigos, la IA de Landers y mutantes, bombarderos y Baiters, las **transiciones de nivel** entre fase superficie y oleadas espaciales, gran parte de las **colisiones** del lado enemigo, el **HUD** superior dibujado desde el motor, la **puntuación unificada**, el récord en disco, y el **empaquetado** para web con pygbag y para escritorio con PyInstaller.

**Miguel Angel Moreno Páez** coordinó al equipo: revisión de avances, alineación con la rúbrica del curso, reparto de carpetas en Git para evitar conflictos, y cierre hacia la publicación en itch.io y los informes escritos. En esta entrega, el bloque de código de enemigos lo concentró Héctor para tener un solo responsable de esa capa; Miguel aporta seguimiento de producto y calidad de entrega.

El juego puede probarse en el **navegador** en nuestra página de itch.io; el repositorio completo está en GitHub.

---

## PARTE 2 — Qué hace el juego (demostración narrada)

**[Pantalla: ejecutar el juego — menú y partida]**

Al arrancar aparece una **pantalla de menú** con el logo y las instrucciones. Con **Enter** o **Espacio** cargamos la partida: en ese momento el motor llama a `_reload_play_world()`, que **reconstruye el mundo ECS** desde cero — lee los JSON, crea entidades de escenario, astronautas, jugador, spawner y HUD.

El jugador opera en **modo arcade Defender**, activado en `player.json` con la clave `arcade_defender_flight: true`. Los controles son:

- **Flechas arriba y abajo** para cabeceo vertical.  
- **Flechas izquierda y derecha** como empuje lateral además del thrust principal.  
- **X** para thrust — impulso hacia adelante en la dirección que lleva la nave.  
- **C** para **reverse**, invertir el sentido del empuje.  
- **Z** para el **láser**.  
- **Espacio** para la **smart bomb**, que destruye enemigos en la zona visible y suma puntos.  
- **H** para **hiperespacio**, teletransporte con riesgo.  
- **P** o **Escape** para **pausa**; la simulación se congela pero se sigue dibujando un overlay.

En la **franja superior del HUD** vemos **PUNTOS** con seis dígitos, el récord **MÁX** — que combina el mejor guardado en `userdata/high_score.json` y el puntaje de la partida actual —, **vidas**, **cantidad de smart bombs**, contadores **ENEM** y **MUT**, y un indicador de fase: **SUPERFICIE** cuando defendemos el planeta, u **OLA ESP** con el número de oleada espacial cuando ya no quedan astronautas en el suelo.

En la superficie, varios **astronautas** están alineados al **relieve del planeta**. Ese relieve no es solo decoración: el motor calcula `planet_edge_screen_y` en `scenario_profile.py` para que los humanos “pisen” la silueta correcta.

Los **Landers** patrullan, disparan cuando el jugador entra en la **vista** — no disparan a ciegas fuera de pantalla — y pueden iniciar una **captura**: el HUD muestra la alerta **“! RAPTOR !”** cuando un lander está en fase de acercamiento o ascenso con un humano. Si el lander completa el ascenso sin ser destruido, el sistema `system_lander_mutation` convierte la amenaza en un **mutante** mediante `mutate_spawn.py`. Si matamos al lander durante el ascenso, el astronauta **cae** y puede volver a rescatarse.

Otros enemigos vienen del catálogo en `enemies.json`: **Pods** que sueltan **Swarmers**, **Bombers** que dejan caer bombas animadas en una tira de cinco fotogramas, y **Baiters** que pueden aparecer si la oleada se alarga demasiado, según reglas en `game_rules.json` y `system_arcade_baiter_spawn.py`.

El **radar** en la parte inferior resume el mundo ancho: blips para nave, enemigos y humanos, con escala configurable en `game_rules.json` sin cambiar las cajas de colisión.

Cuando se destruyen todos los enemigos de una oleada en **superficie** pero **aún hay astronautas vivos**, el juego **no termina**: `system_level_progress` **repite la oleada de superficie**, estilo Defender, en lugar de dar victoria inmediata. Cuando **no quedan humanos**, `system_defense_arcade_transition` pasa a la fase **espacio** con varias oleadas definidas en `level_01.json` bajo `space_waves`. Tras completar el ciclo espacial, el planeta puede **repoblarse** según las reglas del nivel.

Esa es la experiencia que defendemos en la sustentación: mecánicas reconocibles de Defender, implementadas sobre una arquitectura ordenada.

---

## PARTE 3 — Idea general de la arquitectura

**[Pantalla: árbol de carpetas `main.py`, `src/engine`, `src/ecs`, `assets`]**

Separar el proyecto en capas fue una decisión de equipo desde los primeros avances, para poder trabajar en paralelo sin romper el mismo archivo cada semana.

**Primera capa — entrada:** `main.py` solo crea un `GameEngine` y llama a `run_async()`. En navegador, pygbag exige que `main()` devuelva rápido y el bucle corra en una tarea asyncio; por eso en `emscripten` usamos `asyncio.create_task(game.run_async())`.

**Segunda capa — motor:** la carpeta `src/engine/` **no** contiene la lógica de “qué hace un lander”, sino **cómo corre el programa**: ventana Pygame, reloj, fases `menu` / `play` / `game_over` / `victory` en `game_state.game_phase`, carga de JSON con `config.py`, registro de texturas y sonidos con **Service Locator**, y sobre todo el **orden fijo** en que se invocan los sistemas ECS cada frame dentro de `_update_play()`.

**Tercera capa — juego ECS:** `src/ecs/components/` guarda **datos** — posición, velocidad, sprite, IA, tags. `src/ecs/systems/` guarda **comportamiento** — una función por responsabilidad que recorre entidades con ciertos componentes usando `esper.get_components`.

**Cuarta capa — datos:** `assets/cfg/*.json` y `assets/img/`, `assets/snd/`. Cambiar la densidad de una oleada es editar `level_01.json`; cambiar puntos por mutante es `game_rules.json`; no hace falta tocar Python salvo que aparezca un tipo de enemigo totalmente nuevo.

Un diagrama mental simple: **JSON → config.py → GameEngine crea entidades → cada frame los sistemas actualizan componentes → system_draw pinta**.

---

## PARTE 4 — ECS: qué componentes creamos y por qué

**[Pantalla: `src/ecs/components/`]**

En ECS, una **entidad** es un número — un ID en esper. No hay clase `class Lander(Enemy)`. Lo que hace que algo sea un lander es que tenga, por ejemplo, `CPosition`, `CVelocity`, `CSurface`, `CLanderAI`, `CTagEnemy` y `CTagLander` al mismo tiempo.

### Componentes de transformación y dibujo

- **`CPosition` y `CVelocity`:** casi todo lo dinámico los lleva. `system_movement` integra posición más velocidad por delta de tiempo cada frame.  
- **`CSurface` y `CAnimation`:** sprites con varios fotogramas horizontales; `system_animation` avanza el clip. La nave, landers, bombas y explosiones usan este par.  
- **`CSize` y `CColor`:** fallback cuando no hay imagen — rectángulos de color para prototipos.

### Tags — por qué no basta un string `enemy_type`

En `c_tags.py` definimos marcadores vacíos: `CTagPlayer`, `CTagEnemy`, `CTagMutant`, `CTagLander`, `CTagHud`, etc.

Un sistema de colisión puede preguntar “todas las entidades con `CTagEnemy`” sin importar si es bomber o lander. El HUD cuenta **mutantes** con `CTagMutant` específicamente. La smart bomb deduplica víctimas porque algunas entidades — como bombas de bomber — llevan más de un tag; aprendimos a no borrar la misma entidad dos veces en `system_arcade_smart_bomb.py`.

### Jugador

- **`CInputCommand`:** cola de intenciones del frame.  
- **`CArcadeDefenderFlight`:** thrust, drag, facing, velocidad máxima — parámetros del modo Defender.  
- **`CPlayerArcadeBurner`:** sprites de quemador idle y moving; `system_draw` los pinta **detrás** de la nave cuando hay thrust.  
- **`CShieldSpecial`:** solo si **no** estamos en modo arcade; en arcade, Espacio es smart bomb, no escudo.

### Escenario

- **`CScenarioStarfield` y `CScenarioPlanetProfile`:** estrellas parpadeantes y offsets del relieve; `system_scenario_update` hace scroll; `system_scenario_draw` dibuja. El planeta usa una lista de offsets periódicos generada en `scenario_factory.py` con semilla nueva cada partida.

### IA y enemigos

- **`CLanderAI`:** máquina de estados del lander — patrulla, persecución, fases de captura `approach` y `ascend`, temporizadores de disparo.  
- **`CHunterAI`:** movimiento de cazador/mutante — persecución y retorno.  
- **`CPodCargo`:** la cápsula que al destruirse suelta swarmers vía `spawn_pod_swarm.py`.  
- **`CBomberDrop`:** control del bomber que suelta bombas con animación.  
- **`CMissileBurst`:** ráfagas del mutante; `system_mutant_missile` crea proyectiles con tag de misil enemigo.

### Nivel y astronautas

- **`CEnemySpawner`:** en una entidad “portadora” del nivel vive la lista de eventos `{ time, enemy_type, position }` clonada desde JSON; `system_enemy_spawner` compara el tiempo de sesión y crea enemigos.  
- **`CAstronautState`:** libre en suelo, cargado por lander, cayendo, rescatado; sincronizado con `system_astronaut_carried_sync`, gravedad, aterrizaje y rescate en `system_astronaut_rescue_ship.py`.

**Por qué ECS para Defender:** el arcade original mezcla muchas “especies” con comportamientos distintos pero comparten movimiento, dibujo y colisión. Componer componentes + reutilizar sistemas escala mejor que una jerarquía profunda `Enemy → Lander → CapturingLander`.

---

## PARTE 5 — ECS: qué sistemas creamos y por qué

**[Pantalla: `src/ecs/systems/` y scroll en `game_engine.py` → `_update_play`]**

Los sistemas son funciones llamadas **en orden manual** desde `GameEngine._update_play()`. Ese orden importa: primero input, luego comandos, luego spawner, luego IA, luego movimiento, luego colisiones. Si moviéramos colisiones antes de movimiento, veríamos un frame de retraso en los impactos.

Recorremos el pipeline real del código:

1. **`system_scenario_update`** — mueve estrellas y planeta.  
2. **`system_input_command`** — lee teclado; llena `command_queue` en `CInputCommand`.  
3. **`system_execute_commands`** — ejecuta Commands: thrust, disparo, creación de balas con `CBulletDef`.  
4. **`system_arcade_hyperspace`** y **`system_arcade_smart_bomb`** — habilidades especiales arcade.  
5. **`system_enemy_spawner`** — según reloj de sesión, instancia enemigos desde defs en `enemy_defs.py`.  
6. **`system_arcade_wave_time`** y **`system_arcade_baiter_spawn`** — tiempo de oleada y baiter tardío.  
7. **IA:** `system_hunter_ai`, `system_mutant_missile`, `system_lander_ai`.  
8. **Astronautas:** gravedad, sync con lander, aterrizaje, rescate, snap al terreno.  
9. **`system_movement`** — integra todas las entidades con posición y velocidad.  
10. **`system_bomber_drop_bombs`** — bombas en caída con animación de cinco frames.  
11. **`system_world_wrap`** — wrap horizontal del mundo ancho; **`system_camera_follow`** — mueve `camera_scroll_x` en `game_state`.  
12. **`system_player_bounds`**, **`system_bullet_bounds`**, **`system_bounce`**.  
13. **Animaciones** del jugador, hunter y genérica.  
14. **Colisiones:** bala–enemigo, bala–bala enemiga, bala–astronauta, jugador–enemigo, misil–jugador. Puntos vía **`enemy_kill_score.score_for_destroyed_enemy`**.  
15. **`system_defense_arcade_transition`** — ¿pasamos a espacio?  
16. **`system_lander_mutation`** — ¿lander terminó ascenso? → mutante.  
17. Sonido de movimiento del jugador y refresh del HUD de escudo si aplica.

En **dibujo**, `_draw_play()` llama `system_scenario_draw`, `system_draw` — que respeta `viewport.py` para no pintar fuera de vista —, anillo de escudo, radar `system_draw_radar_defender`, y el motor dibuja la franja HUD de puntos y vidas encima.

**Por qué un archivo por sistema:** cuando el profesor pregunta “¿dónde está el rapto?”, respondemos `system_lander_ai.py` y `c_lander_ai.py`. Cuando falló el récord en HUD, fue `game_state.py` y `_draw_play_hud`. Esa localización es deliberada.

---

## PARTE 6 — Archivos de configuración que usamos

**[Pantalla: abrir `assets/cfg/` archivo por archivo]**

El motor centraliza la lectura en **`config.py`**. Cada JSON tiene un rol concreto:

**`window.json`** — Título de la ventana, ancho y alto en píxeles — nosotros usamos 960 por 768 —, FPS, color de fondo. El motor escala el área de juego vertical si `world.json` define `play_area_top_px` y `play_area_bottom_px`.

**`world.json`** — Número de estrellas, colores, factores de parallax distintos para estrellas y planeta, puntos del perfil del relieve, colores del terreno. Al iniciar partida, `scenario_factory.create_scenario_entities` genera dos entidades de fondo con esos parámetros.

**`game_rules.json`** — Corazón del balance: vidas iniciales, puntos por destruir mutante, bonus por rescate, puntos por limpiar oleada de superficie, cantidad inicial de smart bombs, vida extra cada diez mil puntos, ancho del mundo `world_play_width_px` — en nuestro caso 896 píxeles —, escalas solo visuales `sprite_draw_scale` y `radar_blip_scale`, duración del flash de smart bomb, parámetros de bomba del bomber, tiempos de baiter, etc.

**`player.json`** — Activa `arcade_defender_flight`, rutas a `player.png`, quemadores `player_burner_idle` y `player_burner_moving`, velocidad y suavizado de entrada.

**`enemies.json`** — Tabla por `type`: `lander_green`, `mutant_arcade`, `pod_capsule`, `swarmer_dot`, `bomber_row`, `baiter_ufo`, cada uno con sprite, animaciones, velocidades, sonidos opcionales y parámetros de IA. `config.py` los convierte en objetos `LanderEnemyDef`, `ChaseMutantDef`, etc., en `enemy_defs.py`.

**`level_01.json`** — Posición inicial del jugador, lista de `astronaut_spawns` en X, y el bloque **`defense_arcade`**: `surface_enemy_spawn_events` con decenas de entradas `{ time, enemy_type, position }`, más un arreglo `space_waves` con varias oleadas espaciales. Aquí ajustamos la densidad del juego sin recompilar.

**`bullet.json` y `explosion.json`** — Velocidad y sprite del láser; sprite y clip EXPLODE de explosiones.

**`interface.json`** — Fuente, textos del título, instrucciones en pantalla, estilo del HUD estático.

**`special.json`** — Parámetros del escudo pulsante para el modo no arcade.

Al pulsar “nueva partida”, `GameEngine._reload_play_world()` hace `esper.clear_database()`, vuelve a leer reglas, reconstruye escenario, astronautas, jugador y entidad spawner con `CEnemySpawner` clonado desde la plantilla de superficie para poder repetir oleadas.

---

## PARTE 7 — Paradigmas además de ECS

**[Pantalla: `commands.py`, `service_locator.py`, `game_state.py`]**

El curso pide varios patrones además de ECS. Explicamos cómo aparecen en **nuestro** código:

### Game Loop

En `GameEngine.run_async()` — antes `run()` en escritorio — repetimos cada frame mientras `is_running` sea verdadero: calcular delta con `clock.tick`, procesar eventos Pygame — menú, pausa, teclas de habilidades —, si la fase es `play` y no hay pausa, llamar `_update_play()` con todos los sistemas, luego `_draw_play()`, luego `pygame.display.flip`, y en web un `await asyncio.sleep(0)` para no bloquear el navegador. En pausa, **no** llamamos `_update_play`, pero sí dibujamos overlay “PAUSED”.

### Command

En `commands.py` definimos clases como comandos de movimiento y disparo. `system_input_command` **no** mueve la nave directamente: solo encola comandos en `CInputCommand`. `system_execute_commands` los ejecuta: modifica `CVelocity`, crea entidades bala con tags, reproduce sonidos vía Service Locator. Ventaja: separar **hardware** — teclado — de **reglas** — física arcade. Mañana podríamos mapear gamepad sin reescribir landers.

### Service Locator

`ServiceLocator` en `service_locator.py` registra tres servicios al arrancar: `textures`, `sounds`, `fonts`, implementados en `resource_services.py`. Cualquier sistema hace `ServiceLocator.current().get("textures").load("assets/img/...")` con rutas relativas a la raíz del proyecto. Evita duplicar caché de imágenes y centraliza política de rutas — importante también en build empaquetado con PyInstaller o pygbag.

### Configuración externa (data-driven)

Ya detallamos los JSON; es el patrón que más usamos para **diseño de niveles**: el programador expone sistemas; el diseñador del equipo edita tiempos y tipos en `level_01.json`.

### Estado parcial (menú, pausa, fases)

No implementamos un `SceneManager` con clases `MenuScene` y `PlayScene` como en motores grandes. En su lugar, `game_state.game_phase` vale `menu`, `play`, `game_over` o `victory`, y `game_state.paused` congela simulación. `GameEngine.run_async` ramifica: en menú dibuja overlay de menú sin ECS de partida completa; en play corre el pipeline; en game over muestra banner. Es un **State ligero**, documentado como deuda si el proyecto creciera más.

### Estado global `game_state`

Concentran puntaje, vidas, índice de oleada espacial, fase defensa `surface` o `space`, scroll de cámara, flags de flash de smart bomb o explosión de planeta. Es un compromiso pragmático: el HUD del motor y `system_level_progress` leen esos valores sin buscar una entidad “singleton” en ECS. Para el tamaño del curso funcionó; en un motor comercial podríamos migrar a un componente `CWorldSession`.

---

## PARTE 8 — Trabajo detallado de cada integrante

**[Pantalla: tabla de roles o cada persona habla su párrafo]**

### Leonardo L. Rueda — jugador y comandos

Leonardo construyó el camino completo desde la tecla hasta el sprite de la nave. Archivos clave: `system_input_command.py`, `commands.py`, `system_execute_commands.py`, `system_player_bounds.py`, `system_player_animation.py`, `system_player_move_sound.py`, `frame_input.py` para solicitar hyperspace y smart bomb en el frame correcto, y componentes `CInputCommand`, `CPlayerInputSpeed`.

Su trabajo define la **sensación de control**: suavizado de velocidad en `player.json`, límites respecto al área de vuelo que el motor escala desde `world.json`, y coherencia entre modo arcade — thrust en X y C — y animación MOVE/IDLE. Leonardo **no** editó `system_enemy_spawner` ni `system_lander_ai`; el contrato del equipo fue que solo **lee** números que el motor ya cargó del JSON.

### Héctor López — motor, mundo y enemigos

Héctor integró la mayor parte del **producto Defender** fuera del jugador. `game_engine.py` concentra el loop, menú, recarga de mundo, orden de sistemas y HUD. `game_state.py` maneja fases, puntaje, récord persistente en `userdata/high_score.json`, y transiciones de defensa arcade. `config.py` y `enemy_defs.py` parsean JSON. `scenario_factory.py`, `scenario_profile.py` y sistemas `system_scenario_*` implementan el fondo. `viewport.py` unifica visibilidad para láser, smart bomb y dibujo en mundo ancho.

En enemigos: `system_enemy_spawner.py`, `system_lander_ai.py`, `system_lander_mutation.py`, `mutate_spawn.py`, `system_hunter_ai.py`, `system_bomber_drop_bombs.py`, `system_arcade_baiter_spawn.py`, `system_defense_arcade_transition.py`, `system_level_progress.py`, colisiones asociadas, `enemy_kill_score.py`, y `system_draw_radar_defender.py`. También builds: scripts `build_web.sh` y `build_desktop.sh`, y documentación en `docs/`.

### Miguel Angel Moreno Páez — coordinación

Miguel aseguró que los avances del syllabus se reflejaran en entregas: bitácora en `avance-equipo.md`, informe de arquitectura, publicación itch.io, y que el reparto Leonardo/Héctor no generara merges conflictivos en `game_engine.py`. Revisó coherencia entre lo que se muestra en vídeo y lo que el código realmente hace. El desarrollo diario de enemigos lo llevó Héctor en esta iteración; Miguel cierra el lado **gestión y calidad** del equipo.

---

## PARTE 9 — Cierre

**[Pantalla: gameplay o URL itch + GitHub]**

En conclusión: entregamos un **Defender jugable** con arquitectura **ECS** en Python, datos en **JSON**, patrones **Game Loop**, **Command** y **Service Locator**, mundo ancho con cámara y radar, ciclo superficie–espacio, y un reparto claro de responsabilidades entre Leonardo, Héctor y Miguel.

Invitamos a probar el juego en itch.io y a explorar el repositorio en GitHub para ver el detalle de cada sistema y cada archivo de configuración.

Gracias por su atención.

---

## Notas para quien graba (no leer en el vídeo)

| Si preguntan… | Respuesta en una frase |
|---------------|------------------------|
| ¿Por qué esper y no Unity? | Requisito del curso; Python + ECS explícito. |
| ¿Dónde se cambia la dificultad? | `level_01.json` y `game_rules.json`. |
| ¿Dónde el game loop? | `GameEngine.run_async`, `_update_play`, `_draw_play`. |
| ¿Cómo repartieron Git? | Leonardo: `system_player_*` y commands; Héctor: engine, ecs enemigos, cfg; Miguel: coordinación. |
