# Enunciato del proyecto — MISW-4407

*Introducción al desarrollo de videojuegos — proyecto final (clon *Defender*).*

Este documento reúne el **enunciato** consolidado utilizado por el equipo: objetivos pedagógicos, producto esperado, requisitos, recursos cohorte y entregas. La **evaluación pormenorizada** (tablas por criterio) sigue documentada en el [**README** del repositorio](../README.md#rúbricas-del-proyecto-final) *(sección Rúbricas)*.

---

## Enunciato

Aplicar en un solo producto lo aprendido en las cuatro primeras semanas del curso, encaminándose a reproducir lo más cercano posible a un **juego clásico** con comportamiento, proporciones y sensación cercanos al original (**no** basta algo solo “similar” o “inspirado en”).

## Objetivos de aprendizaje

| Área | Objetivo |
|------|----------|
| Estructura | Aplicar la **base del patrón Game Loop**. |
| Arquitectura | Aplicar **ECS** (entidad-componente-sistema). |
| Motor | Modelar situaciones típicas con **matemáticas aplicadas**. |
| Físicas | Implementar **colisión básica**. |
| Entrada | Aplicar el patrón **Command simplificado** a input y acciones. |
| Experiencia | Reconocer **game feel** y aplicarlo. |
| Arte 2D | Texturas, **sprites**, animación 2D cuadro a cuadro en práctica real. |
| Estado / IA | Patrón **State** sobre varias entidades. |
| Recursos | **Administración de assets** usando **Service Locator**. |
| Despliegue | **Despliegue** específico en **Python** (escritorio y web cuando aplique). |
| Escenas | Patrón de **Escena(s)** en un proyecto real. |

**Bonus opcionales** (contenidos de semanas posteriores si se implementan): diferencias entre **motores** y **APIs/Frameworks**, clasificación de **herramientas**, y/o **IA con steering behaviours** y **emergencia**.

## Producto: clon tipo *Defender* (Williams, 1981)

Réplica cercana al arcade con **énfasis en exactitud** (dimensiones, sonidos, comportamientos). Se permite **extender** la base si funciona como continuidad natural o secuela. No es obligatorio un **100 % literal**, pero debe acercarse todo lo que sea **razonable**.

## Referencias

- **[Williams Arcade's Greatest Hits (USA)](https://online-emulators.com/snes/Williams_Arcade's_Greatest_Hits_(USA))** — emulación SNES; *settings*: velocidad, *save states*, etc.
- **[GameFAQs — Defender arcade](https://gamefaqs.gamespot.com/arcade/584162-defender/faqs/25139)** — guía de mecánicas.
- **Vídeo de gameplay** recomendado como referencia principal.

> ***Defender* original** usa **luces parpadeantes** (bomba, muerte, fase 2…). El curso **no exige** parpadeo a pantalla completa *(riesgo de epilepsia)*; pueden sustituirlo por efectos locales o por **énfasis en sonido**.

## Requisitos obligatorios (resumen)

- **ECS** en la mayor parte del código (**obligatorio** para aceptación del proyecto).
- **Menú** con título e instrucciones para jugar.
- **Fondo:** estrellas animadas; planeta procedural por líneas (distinto cada partida); **parallax**. Ni jugador ni enemigos chocan con la línea del planeta; **astronautas** aparecen debajo (**suelo**) y puntos al transportarlos al suelo.
- **Nave:** ratón o flechas, **inercia** cercana al original; **disparo** por teclado — láser **atraviesa enemigos** y **no afecta** a quien esté **fuera de pantalla**.
- **Cámara dinámica** según donde mira = **bonificación**. Sin ella: jugador **centrado**.
- **Enemigos** según nivel; al menos tipos **Lander** y **Mutant**. **Astronautas** en el suelo con ligero movimiento.
- **Lander:** movimiento; dispara si el jugador está en pantalla; **captura** astronautas; al subir, en la zona superior aparece como **Mutant**; astronauta caído con gravedad si matas al Lander; rescate/dejar en el suelo y puntos.
- **Alerta de rapto:** sonido + **minimapa** (bonus) **o** **flecha** + **contador de enemigos** (sin minimapa).
- **Wraparound** horizontal mundo y entidades; enemigos **wrap vertical**; **jugador no**.
- Enemigos disparan en movimiento; a veces **misil pequeño**.
- **Colisiones:** balas enemigas↔jugador; láser jugador↔enemigos, astronautas y otras balas enemigas.
- **Pausa** — tecla dedicada; texto **PAUSED** parpadeante centrado *(alinear texto del enunciato con lo que marque la rúbrica vigente)*.
- **Fanfare** al empezar a jugar la primera vez.
- **Explosiones** tipo partícula con colores por tipo (jugador: blanco que funde a color).
- **HUD** superior: **puntaje** y **vidas** (extras suelen enlazarse con bonificación).
- **Game over / reinicios** cuando corresponda; con **vidas por bonus**, al gastarlas vuelta al menú si aplica.
- **Victoria / olas:** pantalla de victoria conforme nivel/olas (**olas múltiples** = típicamente bonificación).
- **Sonidos** y **animaciones** donde el original las use.
- **Distribución** preferible **[itch.io](https://itch.io)** web o Windows; ejecutables macOS **no recomendados** para entrega habitual.

## Bonificación *(opcional, según rúbrica)*

Entre otros: cámara según disparo; vidas + recuperación por puntos (**config**); **smart bomb** (+recarga por puntaje); HIGH-SCORE persistente en config (**ej. 21 270** inicial); tabla de nombres; **texto multicolor dinámico** (no sprites); **≥ 5 oleadas** en configuración **o** modo infinito con dificultad creciente; **minimapa**; todos los enemigos; **fase 2** sin astronautas; **modo atracción**; vistas **debug**; **editor de niveles**; efectos extra; **dos jugadores**; **gamepad**.

Los **detalles de calificación por ítem** se documentaron en [**Rúbricas**](../README.md#rúbricas-del-proyecto-final).

## Recursos oficiales (cohorte MISW-4407)

- **[Sitio cohorte — recursos proyecto](https://misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-12/)** — sprites, algo de audio, **`window.json`** referencia (**320 × 256**); respetar **rejilla tamaño** al editar.
- Completar sonidos (**[sfxr](https://sfxr.me/)**); exportación **`.ogg`** para web (**Audacity** u otra herramienta).

> **Assets propios:** permitidos cumpliendo **copyright** de terceros y la **resolución de diseño** (p. ej. 320 × 256).

## Entregas formativas *(no califican — mentoría)*

1. Nombre/descripción del grupo + integrantes/correos + GitHub + documentación disponible.  
2. **Propuesta técnica.**  
3. **Avances:** ECS propuesto, refactor acumulado, bitácora por persona, alcance hacia la entrega final, **repositorio** actual.

Las **tres primeras entregas** no puntúan; habilitan revisión opcional por docentes/tutores.

## Entrega sumativa *(impacta la nota)*

| Entregable | Contenido breve esperado |
|------------|-------------------------|
| **Build público** (itch.io / Game Jolt / Newgrounds…) | Ejecutable; descripción en la página del portal + pantallazo (+ bonifs. si aplican). |
| **Código fuente** | URL Git; tag/commit final alineado con lo publicado; historial por semanas visible. |
| **Post-mortem + arquitectura grupal** | Evolución semanal; ECS y decisiones *(diagramas opcionales)*; patrones; reflexión. |
| **Post-mortem individual** | Rol propio + aprendizajes. |
| **Vídeo** | Juego, equipo, ECS (componentes/sistemas/config), paradigma extra, papel de cada integrante *(trailer opcional)*. |

## Recomendaciones

- Videos/tutoriales semanales (base de muchas bonificaciones).
- Reutilizar trabajo de ejercicios y demos del curso.
- **Debug / trucos** documentados (README itch o proyecto).
- Comunicación temprana con tutores/monitores/profesores ante bloqueos.

## Ponderación *(proyecto final ~50 % curso típico)*

Como orientación habitual del curso: **juego publicado 20 %**, código 10 %, post-mortem grupal 10 %, individual 10 %, vídeo presentación 10 % — más **≈10 %** posible bonificación global. Confirmar valores en el **silabus** / docencia vigente.

---

*Última edición contenido — alinear con comunicados oficiales curso año/cohorte en curso.*
