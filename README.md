# Proyecto final — Introducción al desarrollo de videojuegos (MISW-4407)

Aplicar lo aprendido en las **cuatro primeras semanas** en la **réplica más fiel posible** de un arcade conocido: no vale un juego apenas “similar” ni “inspirado en”; el resultado debe acercarse al original en proporciones, sonido y comportamiento.

## Información del proyecto

**Enunciato** del curso (objetivos, *Defender*, requisitos, referencias y entregas): [`docs/enunciado.md`](docs/enunciado.md)

Rúbricas y desglose por puntos: [más abajo](#rúbricas-del-proyecto-final).


## Equipo

| Miembro | Correo Uniandes |
|--------|------------------|
| Leonardo L. Rueda | [leonardo.l.ruedar@uniandes.edu.co](mailto:leonardo.l.ruedar@uniandes.edu.co) |
| Miguel Angel Moreno Páez | [ma.moreno2@uniandes.edu.co](mailto:ma.moreno2@uniandes.edu.co) |
| Héctor López | [hv.lopez@uniandes.edu.co](mailto:hv.lopez@uniandes.edu.co) |

## Documentación

### Avance y código fuente

| Archivo | Contenido |
|---------|-----------|
| [`docs/avance-equipo.md`](docs/avance-equipo.md) | Miembros, roles y trabajo. |
| [`docs/analisis-arquitectura-post-mortem.md`](docs/analisis-arquitectura-post-mortem.md) | **Informe grupal:** resumen, arquitectura, patrones (ECS), post-mortem. |
| [`docs/presentacion-video.md`](docs/presentacion-video.md) | **Guion / guía** para el vídeo de presentación (rúbrica MISW). |
| [`docs/entrega-publicacion-y-post-mortem.txt`](docs/entrega-publicacion-y-post-mortem.txt) | **Entrega .txt:** URL de publicación + post-mortem en texto plano. |
| [`docs/enlace-codigo-fuente.md`](docs/enlace-codigo-fuente.md) | Repositorio Git y, si aplica, entrega en `.zip`. |

### Arquitectura

Carpeta [`docs/arquitectura/`](docs/arquitectura/):

| Archivo | Contenido |
|---------|-----------|
| [`docs/arquitectura/estado-general.md`](docs/arquitectura/estado-general.md) | Requisitos *Defender* / curso **vs** lo implementado hoy. |
| [`docs/arquitectura/arquitectura-ecs.md`](docs/arquitectura/arquitectura-ecs.md) | Introducción ECS, Command, pausa, Service Locator, decisiones y deuda. |
| [`docs/arquitectura/componentes.md`](docs/arquitectura/componentes.md) | Inventario de **componentes** y combinaciones típicas. |
| [`docs/arquitectura/sistemas.md`](docs/arquitectura/sistemas.md) | Orden de **sistemas** en el game loop y dependencias. |
| [`docs/arquitectura/recursos-y-config.md`](docs/arquitectura/recursos-y-config.md) | JSON en `assets/cfg/`, Locator, resolución **320 × 256**. |
| [`docs/arquitectura/flujo-de-juego.md`](docs/arquitectura/flujo-de-juego.md) | Bucle principal, pausa y flujo entre estados del juego. |

## Rúbricas del proyecto final

### Evaluaciones en grupo — visión general

Los entregables de grupo aplican conocimientos de las primeras cuatro semanas para la reproducción de un juego conocido. Aspectos generales:

- El juego se publica en un portal (itch.io, Game Jolt, Newgrounds u otro similar), en el estado en que esté el ejecutable/compilación.
- Debe haber descripción del juego y captura/pantallazo en el portal.
- Las bonificaciones del juego pueden sumarse si están implementadas.

---

### Proyecto final — juego publicado (**20 % · 20 puntos**)

Evalúa reproducir el juego con los requisitos técnicos y de contenido siguientes.

| Pts | Criterio | Deficiente | Regular | Excelente |
|-----|----------|------------|---------|-----------|
| **5** | **URL del proyecto terminado** (web o descarga en portal tipo itch.io, Game Jolt, Newgrounds, etc.) | No publicado o sin URL enviado | URL muestra el juego pero el sitio **no** tiene descripción ni pantalla | Juego publicado en el URL, con **descripción** y **pantalla/captura** |
| **1** | Pantalla de **menú principal** con instrucciones y logo | No | — | Sí |
| **1** | **Fondo** de estrellas animado y **planeta** aleatorio, con movimiento como en el original | No | Deficiente, sin animación/movimiento, o solo uno de los elementos | Sí |
| **1** | **Movimiento y disparo** de la nave (si no hay bono de cámara: jugador en el centro) | No | — | Sí |
| **1** | **Spawn** de Landers y astronautas y **comportamiento** (movimiento/persecución según personaje) | No | Falta algún elemento del enemigo o del astronauta | Sí |
| **1** | **Wraparound** de todas las entidades, mundo y personajes | No | — | Sí |
| **1** | Mecánica de **rapto** de astronautas + **enemigo mutante** | No | — | Sí |
| **1** | Enemigos **disparan** ocasionalmente en su movimiento básico | No | — | Sí |
| **1** | **Colisión** láser jugador ↔ balas y enemigos (incl. astronautas); balas enemigas ↔ jugador | No | — | Sí |
| **1** | **Pausa**: jugador, enemigos y proyectiles invisibles; texto **PAUSED** (o similar) **parpadeando** | No | — | Sí |
| **1** | **Sonido de introducción** al comenzar el primer nivel | No | — | Sí |
| **1** | **Puntaje** visible arriba | No | — | Sí |
| **1** | **Contador de enemigos** y flecha de **rapto** (sin minimapa cumple lo pedido; con minimapa se cumple + bono posible) | No | — | Sí |
| **1** | **Explosiones de partículas** en todas las entidades que correspondan | No | — | Sí |
| **1** | **GAME OVER** / reinicio: al morir por bala (considerar vidas si existen); o cuando todos los astronautas mueran o desaparezcan | No | Errores en la secuencia | Sí |
| **1** | **Sonidos** y **animación de imágenes** acordes al original | No | Pocas o irregulares | Sí |

---

### Proyecto final — enlace al código fuente (**10 % · 10 puntos**)

Cada fila vale **Si** / **No** (excelente ↔ deficiente).

| Pts | Dimensión | Excelente | Deficiente |
|-----|-----------|-----------|------------|
| **1** | URL al código en **Git** | Sí | No |
| **2** | Patrón **ECS** (**obligatorio**) | Sí | No |
| **1** | Patrón **Game Loop** | Sí | No |
| **1** | Patrón **Command simplificado** | Sí | No |
| **1** | Patrón **State** | Sí | No |
| **1** | Patrón **Service Locator** | Sí | No |
| **1** | Patrón **Escena** | Sí | No |
| **1** | Uso de **archivos de configuración** | Sí | No |
| **1** | El código corresponde al **juego publicado** | Sí | No |

---

### Documento — análisis de arquitectura y post-mortem grupal (**10 % · 10 puntos**)

Incluir: **Resumen**, **Análisis arquitectónico**, **Patrones usados** y **Reflexión**.

**Contenido esperado**

- **Resumen:** proceso de desarrollo y evolución **semana a semana**.
- **Análisis arquitectónico:** organización de clases, componentes y sistemas y **por qué** esas decisiones; diagramas si es posible.
- **Patrones:** análisis, en particular **ECS** en juegos y otras aplicaciones.
- **Reflexión:** ¿Qué salió bien? ¿Qué salió mal? ¿Qué cambiar en el futuro?

| Pts | Dimensión | Deficiente | Regular | Muy bien | Excelente |
|-----|-----------|------------|---------|----------|------------|
| **2,5** | **Resumen** | No entrega | Inconsistencias o procesos hechos pero sin enunciar o sin claridad | Principales acciones sintetizadas con imprecisiones que no afectan del todo la comprensión | Sintetiza con claridad el proceso **semana a semana** |
| **2,5** | **Análisis arquitectónico** | No entrega, incompleto, incorrecto o poco claro | Incompleto o sin todos los elementos (clases, componentes, sistemas, razones de decisiones) | Incluye **todos** esos elementos con claridad | Lo anterior **y** diagrama que mejora la comprensión |
| **2,5** | **Patrones usados** | No entrega o análisis sin argumentos/ejemplos sólidos | Falta suficientemente ECS y relevancia en juegos u otras apps | Análisis de patrones con huecos en ECS | Claro sobre **ECS** empleado y relevancia en juegos/apps |
| **2,5** | **Reflexión** | No entrega / no evalúa / poco argumentada | Respuestas incompletas o imprecisas, sin mejoras claras desde el proyecto | Reflexión argumentada con mejoras algo visibles desde el proyecto real | Respuestas bien argumentadas (**bien/mal/futuro**) con mejoras desde el proyecto |

---

### Presentación del proyecto (**10 % · 10 puntos**)

**Vídeo** con arquitectura, **roles** y desempeño de integrantes:

- Buen uso de lenguaje audiovisual; presentar **juego** e **integrantes**.
- Precisión sobre la **labor de cada uno**.
- **Arquitectura ECS:** qué componentes y sistemas y por qué; qué archivos de configuración; qué otros paradigmas aparte de ECS.

| Pts | Dimensión | Deficiente | Regular | Muy bien | Excelente |
|-----|-----------|------------|---------|----------|------------|
| **3,5** | **Vídeo** | No entrega | Confuso / uso audiovisual inadecuado | Comunica ideas; muestra bien el **juego** pero **no** enuncian integrantes | Comunicación clara; **juego** e **integrantes** presentados con precisión |
| **3,5** | **Arquitectura** | No entrega | No responde a **todas** las preguntas | Todas contestadas pero con imprecisiones o poca claridad/profundidad | Todas contestadas **con precisión, pertinencia y suficiencia** |
| **3** | **Trabajo por integrante** | No entrega | Quién hizo qué **no** es claro | Imprecisiones pero se logra comprender las tareas de cada uno | **Claro** quién realizó cada actividad |

---

### Evaluación individual (**10 % · 10 puntos**)

Cada estudiante entrega **post-mortem individual** con:

- **Descripción** de rol y trabajo **específico**.
- **Ajustes:** qué salió bien, mal y qué cambiaría para un **proyecto futuro propio**.
- **Evaluación:** aprendizajes y vínculo con la **creación de videojuegos**.

| Pts | Dimensión | Deficiente | Regular | Muy bien | Excelente |
|-----|-----------|------------|---------|----------|------------|
| **3,5** | **Descripción** | Roles/actividades poco claros | Descripción con **algunas imprecisiones** | Roles y trabajo bastante claros; tareas coherentes | Descripción **clara** del rol y trabajo real; **tareas e influencia** en el resultado final muy legibles |
| **3,5** | **Ajustes** | No cubre qué fue bien/mal/qué cambiaría en futuro proyecto propio | Los tres están pero con lagunas tolerables | **Clara** en bien/mal y ajustes personales futuros | Misma cobertura con argumentación **sólida** y mejoras muy concretas |
| **3** | **Evaluación** | No permite entender los aprendizajes | Principales hallazgos del curso; **falta** precisión vínculo con creación de juegos | Aprendizajes articulados con el curso y la práctica propia | **Sintetiza** aprendizajes y establece qué aspectos debe **apropiar en profundidad** sobre creación de videojuegos (conceptual y procedimental) |

---

### Bonificación del proyecto final (**hasta 10 % adicional sobre la nota final**)

Opcional: suman a ítems con nota deficiente (grupo o individual); combinadas pueden superar **100 %**.

**Bonos de juego publicado — Excelente = Bonificación cuando aplica**

- Cámara del jugador (desplazamiento según hacia dónde mira).
- Sistema de **vidas** (dos vidas y game over).
- **Puntaje máximo** y **HIGH-SCORE** conservado en la misma sesión.
- Pantalla de **HIGH SCORE** al terminar, con posibilidad de escribir nombre.
- **Todos** los enemigos del juego, sin excepción.
- Texto a **colores dinámico**.
- **Varios niveles** con config en **olas** (o infinito con dificultad dinámica — vale **por dos**).
- **Minimapa**.
- Mecánica **smart bomb**.
- **Fase dos** (al perder todos los astronautas).
- **Vistas de depuración** para evaluar aspectos pertinentes del juego.
- **Editor de niveles** con carga/guardado.
- **Efecto visual** extra sobre el juego.
- Modo **atracción**.
- Juego **a dos jugadores**.
- Inputs de **gamepad**.
