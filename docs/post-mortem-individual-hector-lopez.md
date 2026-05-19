# Post-mortem individual — Proyecto final Defender

**Estudiante:** Héctor López  
**Correo Uniandes:** hv.lopez@uniandes.edu.co  
**Curso:** MISW-4407 — Introducción al desarrollo de videojuegos  
**Proyecto:** Clon arcade *Defender* (grupo: Proyecto final Defender)  
**Fecha:** mayo 2026  

---

## 1. Descripción — rol y trabajo desempeñado

### 1.1 Rol asignado en el equipo

En el grupo acordamos repartir el código por **capas** para evitar conflictos en Git. Mi rol quedó definido como **motor del juego, escenario y línea completa de enemigos** — un bloque que inicialmente correspondía a otro integrante y que asumí para no duplicar trabajo en paralelo sobre el spawner y la IA.

Leonardo L. Rueda se concentró en el **jugador** (entrada, patrón Command, sistemas `system_player_*`). Miguel Angel Moreno Páez apoyó **coordinación y revisión**. Yo fui responsable de que el producto tuviera **bucle jugable**, **mundo Defender** (fondo, planeta, cámara, wrap) y **adversarios + progresión de nivel** coherentes con el enunciado.

### 1.2 Tareas concretas y archivos donde tuve influencia directa

**Motor y orquestación**

- Diseño y mantenimiento de **`GameEngine`** (`src/engine/game_engine.py`): inicialización de Pygame, fases `menu` / `play` / `game_over` / `victory`, orden de llamada a sistemas en `_update_play()` y `_draw_play()`, HUD superior (puntos, MÁX, vidas, enemigos, mutantes, fase superficie/espacio), menú inicial y overlays (pausa, smart bomb, explosión de planeta).
- Módulo **`game_state.py`**: puntaje, vidas, fase defensa arcade, cámara, flags de flash, persistencia de **high score** en `userdata/high_score.json` y funciones `record_high_score_if_best` / `high_score_best_display`.
- **`service_locator.py`**, **`resource_services.py`**, **`config.py`**, **`enemy_defs.py`**: carga de JSON desde `assets/cfg/`, construcción del spawner, reglas de juego y definiciones de tipos enemigos (Lander, Pod, Bomber, Baiter, mutante, etc.).

**Escenario y mundo**

- **`scenario_factory.py`**, **`scenario_profile.py`**, **`scenario_query.py`**: entidades de estrellas y planeta procedural, cálculo de `planet_edge_screen_y` para alinear astronautas al relieve.
- Integración de **`world.json`** y escalado de área de juego según altura de ventana.
- **`viewport.py`**: visibilidad respecto a la cámara y al ancho de mundo con wrap horizontal — base para smart bomb “solo en vista” y culling de dibujo.

**Enemigos, nivel y mecánicas Defender**

- **`system_enemy_spawner.py`**, **`build_enemy_spawner_component`** con escalado de coordenadas Y según resolución.
- IA y comportamientos: **`system_lander_ai.py`**, **`system_hunter_ai.py`**, **`system_lander_mutation.py`**, **`mutate_spawn.py`**, **`system_bomber_drop_bombs.py`**, **`system_mutant_missile.py`**, **`spawn_pod_swarm.py`**, **`system_arcade_baiter_spawn.py`**, **`system_arcade_wave_time.py`**.
- Progresión arcade: **`system_defense_arcade_transition.py`**, **`system_level_progress.py`** (repetición de oleada en superficie con humanos vivos, ciclo superficie ↔ oleadas espacio).
- Habilidades arcade integradas en el motor: **`system_arcade_smart_bomb.py`** (incluida corrección de duplicado de entidades y puntuación unificada), coordinación con hyperspace y radar (`system_draw_radar_defender.py`).
- Colisiones y puntuación del lado enemigo/proyectiles: apoyo en **`enemy_kill_score.py`**, revisión de sistemas `system_collision_*` donde afectan oleadas y marcador.
- Balance y datos: edición sustancial de **`level_01.json`**, **`game_rules.json`**, **`enemies.json`** (densidad de oleadas, Pod/Swarmer, frames de bomba bomber, escalas de dibujo).

**Documentación y cierre de producto**

- Redacción y actualización de **`docs/avance-equipo.md`**, **`docs/guia-sustentacion.md`**, **`docs/archivos-del-repositorio-sustentacion.md`**, **`docs/analisis-arquitectura-post-mortem.md`**, **`docs/entrega-publicacion-y-post-mortem.txt`**, y alineación con **`referencia-mecanicas-defender-faq.md`**.

### 1.3 Influencia en el producto final

Sin el motor estable, el juego no hubiera podido pasar de un prototipo de nave sobre fondo a una **sesión Defender reconocible**: menú, oleadas configurables, landers con rapto, mutantes, smart bomb operativa, radar, récord persistente y HUD informativo. Mi trabajo concentra la **columna vertebral técnica** que Leonardo y el resto del equipo consumen como contrato (bounds, reglas en JSON, orden de sistemas). Las iteraciones tardías de **feel** (más enemigos, HUD que actualiza mutantes, récord MÁX) fueron en gran parte cierre de bugs y reglas en la capa que yo mantenía.

---

## 2. Ajustes — qué salió bien, mal y qué cambiaría (personal)

### 2.1 Qué salió bien (a título personal)

1. **Separar motor (`engine`) de ECS (`ecs`)**  
   Me permitió asumir el bloque de enemigos sin mezclar archivos del jugador. Cuando hubo que añadir modo `arcade_defender_flight`, smart bomb o fases de defensa, el cambio entró por `game_engine` + nuevos sistemas sin reescribir el pipeline de Leonardo.

2. **Configuración en JSON**  
   Ajustar `level_01.json` y `game_rules.json` para densidad de oleadas, puntos y escalas visuales demostró que **data-driven design** compensa la complejidad del código en un clon con muchas criaturas.

3. **Documentar el orden de sistemas**  
   Aunque el pipeline es manual, tener `game_engine.py` como fuente de verdad y documentos en `docs/` ayudó a explicar en sustentación por qué un bug de smart bomb se arreglaba en un solo sistema y no en diez.

4. **Asumir un bloque grande con dueño claro**  
   Evitó que dos personas editaran el spawner a la vez; el costo fue más carga en una persona, pero menos tiempo perdido en merges conflictivos.

5. **Cierre iterativo hacia Defender real**  
   Pasar de “Hunter que rebota” a landers, rapto, oleadas superficie/espacio y récord en disco fue posible porque la arquitectura ECS ya estaba; el esfuerzo fue **contenido y reglas**, no reinicio total.

### 2.2 Qué salió mal o me costó más de lo que esperaba

1. **`game_engine.py` creció demasiado**  
   Concentré menú, HUD, recarga de mundo, orden de ~40 sistemas y overlays. Eso me hizo **cuello de botella** en revisiones y dificulta tests unitarios.

2. **Estado global en `game_state`**  
   Lo usé por pragmatismo (HUD, cámara, fase defensa), pero reconozco que **acopla** sistemas y me obligó a recordar efectos secundarios (p. ej. cuándo llamar `record_high_score_if_best`).

3. **Documentación desalineada con el código en momentos**  
   Archivos como `estado-general.md` quedaron obsoletos cuando ya existían menú y modo defensa; eso generó confusión interna hasta actualizar `avance-equipo.md`.

4. **Postergar itch.io y playtest formal**  
   Prioricé mecánicas y bugs jugables; la **entrega pública** y el registro de prueba wrap quedaron al final, con riesgo para la rúbrica de URL y para validar balance sin sesión grupal larga.

5. **Bugs por supuestos del pipeline**  
   El caso de la smart bomb con **doble tag** en bombas del bomber me enseñó que en ECS el orden y las consultas por tags no perdonan; debí haber deduplicado víctimas antes o unificado tags desde el spawner.

6. **Audio y arte**  
   Dejé muchas rutas de sonido vacías en JSON por falta de tiempo; el juego se ve bien pero **no suena** como Defender, y eso no se arregla solo con código.

### 2.3 Qué cambiaría en un nuevo proyecto (decisiones personales)

| Área | Cambio que haría |
|------|------------------|
| **Motor** | Extraer `SceneManager` o estados explícitos desde el avance 2; no acumular menú + play + HUD en un solo archivo de 800+ líneas. |
| **ECS** | Registrar sistemas por **fases** (`INPUT`, `SIMULATION`, `COLLISION`, `RENDER`) en una tabla en lugar de lista larga a mano. |
| **Estado** | Introducir un objeto `Session` inyectado en sistemas críticos en lugar de módulo global, al menos para puntaje y fase de nivel. |
| **Trabajo en equipo** | Acordar **PR pequeñas** semanales con checklist “¿rompí el orden en `game_engine`?” antes de merge. |
| **QA** | Script de humo (N frames con `SDL_VIDEODRIVER=dummy`) desde la semana 3; no esperar al avance 9. |
| **Producto** | Publicar un **build mínimo en itch** en la semana 6 aunque falten mecánicas, para detectar problemas web temprano. |
| **Yo mismo** | Reservar bloques fijos para **solo documentación y playtest**, no solo features; evita deuda invisible. |

---

## 3. Evaluación — aprendizajes y relación con la creación de videojuegos

### 3.1 Resumen de lo aprendido

Durante el curso y este proyecto integré de forma práctica varios temas que antes eran solo teoría de patrones:

- **ECS (`esper`)**: entender que el juego es composición de datos (componentes) y funciones por frame (sistemas), no un árbol de herencia `Enemy → Lander`. Eso facilitó añadir Pod, Bomber y Baiter sin tocar la clase del jugador.
- **Game Loop**: la disciplina de **input → update → render**, y de no actualizar simulación en pausa, es transversal a cualquier motor (Pygame, Unity, Godot).
- **Command**: separar “qué pidió el jugador” de “qué hace el mundo” aclara depuración y sería la base de replay o red en otro curso.
- **Service Locator y assets externos**: centralizar texturas/sonidos/fuentes y leer reglas desde JSON es cómo se trabaja en estudios pequeños antes de un editor visual.
- **Diseño de niveles como datos**: `level_01.json` me acercó al rol de **diseñador de contenido**; un cambio de `time` o `enemy_type` altera la experiencia sin tocar Python.
- **Paridad con un referente (Defender)**: aprendí a leer un FAQ de arcade y traducirlo a sistemas concretos (oleada superficie, baiter por tiempo, smart bomb en viewport), no solo a “hacer un shooter”.

### 3.2 Aprendizajes en relación con el curso

| Elemento del curso | Cómo lo viví en el proyecto |
|--------------------|-----------------------------|
| Patrones (Command, Locator, State parcial) | Los usé donde el enunciado los pedía; el State completo (escenas) quedó como deuda consciente. |
| ECS obligatorio | Fue la decisión más acertada para Defender; el costo fue **orden del pipeline**, no el paradigma en sí. |
| Trabajo en equipo / Git | La división por carpetas funcionó; fallé en actualizar siempre la doc compartida al mismo ritmo que el código. |
| Recursos cohorte (320×256) | Respetar resolución y rejilla de sprites evitó arte desproporcionado; `sprite_draw_scale` separó dibujo de colisión. |
| Entrega en portal | Entendí que un juego “terminado” para docencia incluye **URL + descripción + captura**, no solo `main.py` local. |

### 3.3 Aspectos conceptuales que debo seguir apropiando

- **Arquitectura de software en juegos**: cuándo usar ECS vs jerarquías OO vs híbridos; límites del estado global.
- **Game feel y balance**: relación entre JSON de spawn, curva de dificultad y sensación arcade; necesito más **playtest metódico**, no solo intuición.
- **Física y colisiones simplificadas**: AABB y viewport son suficientes para el curso, pero debo estudiar cómo se escalan a más entidades sin bugs de un frame.
- **Audio como parte del diseño**: no tratar SFX como “opcional al final”; en Defender el feedback sonoro es identidad.
- **Despliegue web (pygbag)**: conceptos de empaquetado Python en navegador, límites de audio y rendimiento.

### 3.4 Aspectos procedimentales que debo seguir apropiando

- **Definir contrato entre capas** antes de codificar (qué lee el jugador del `world.json`, qué expone el motor).
- **Commits y PRs pequeños** con descripción de qué sistema se tocó y qué frame del loop afecta.
- **Checklist enunciato ↔ implementado ↔ probado** en cada avance, no solo al final.
- **Profiling ligero** (FPS, conteo de entidades) cuando el nivel se densifica.
- **Comunicación con el equipo**: avisar cuando cambio el orden en `game_engine.py` porque impacta a todos.

### 3.5 Cierre personal

Este proyecto me confirmó que **disfruto y rindo mejor en la capa motor/sistemas/reglas** que en arte o audio, pero un clon fiel exige integrar las tres. Salió un Defender **jugable y defendible en sustentación** gracias a ECS y JSON; lo que me falta como desarrollador es cerrar el ciclo **publicar → jugar con extraños → medir → ajustar**. En un siguiente proyecto aplicaría las mismas bases técnicas con menos deuda en `game_engine`, más pruebas automáticas y tiempo reservado desde el inicio para el portal y el playtest documentado.

---

*Documento individual para entrega académica. Informe grupal de referencia: [`analisis-arquitectura-post-mortem.md`](analisis-arquitectura-post-mortem.md).*
