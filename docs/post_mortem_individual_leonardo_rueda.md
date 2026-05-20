# Post-mortem individual — Proyecto final Defender

**Estudiante:** Leonardo Rueda\
**Curso:** MISW-4407 — Introducción al desarrollo de videojuegos\
**Proyecto:** Clon arcade Defender\
**Fecha:** mayo 2026

---

# 1. Descripción — rol y trabajo desempeñado

## 1.1 Rol desempeñado dentro del equipo

Durante el desarrollo del proyecto mi principal responsabilidad estuvo enfocada en la lógica del jugador, las mecánicas principales de control y parte importante de la experiencia arcade relacionada con movimiento, combate y habilidades especiales. Además del desarrollo de sistemas específicos, participé en pruebas de integración, revisión de bugs y ajustes de balance durante las etapas finales del proyecto. También trabajé en ramas experimentales para implementar bonos adicionales y prototipos avanzados.

## 1.2 Tareas concretas desarrolladas

### Jugador y control

Trabajé principalmente sobre los sistemas relacionados con la nave del jugador y su interacción con el mundo: Implementación de entrada y movimiento del jugador, integración del patrón Command para desacoplar entrada y acciones, desarrollo de sistemas relacionados con aceleración, disparo y control de dirección, ajustes de velocidad, sensibilidad y “game feel”, e integración de mecánicas especiales como hyperspace y habilidades del jugador. Gran parte de este trabajo estuvo relacionado con los módulos y sistemas `system_player_*`, además de lógica conectada al loop principal del juego.

### Mecánicas de combate

Participé en la construcción y ajuste de mecánicas ofensivas: Disparos principales del jugador, ajustes de colisiones relacionadas con proyectiles, balance entre velocidad de enemigos y capacidad ofensiva, y revisión del comportamiento de impactos y retroalimentación visual. También apoyé integración y pruebas de sistemas ECS relacionados con entidades de proyectiles y destrucción de enemigos.

### Bonos desarrollados

A título personal trabajé en tres bonos adicionales para el proyecto:

1. **Nueva arma tipo misil de rastreo**: desarrollé un prototipo funcional de misil con seguimiento automático de enemigos.
2. **Efectos visuales adicionales**: implementé efectos para hyperspace, missile trail y shockwave para mejorar la retroalimentación visual del juego.
3. **Prototipo de boss**: inicié el desarrollo de un jefe enemigo en una rama experimental (`leonardo`), pero no alcancé a terminarlo correctamente ni adaptarlo completamente a una arquitectura ECS limpia. Debido a eso, el boss quedó únicamente como prototipo y no fue incluido en el release final.

Estos bonos me permitieron explorar problemas adicionales relacionados con arquitectura ECS, efectos visuales y diseño de mecánicas más complejas.

### Integración y pruebas

Además de implementar sistemas, participé en pruebas de jugabilidad, revisión de bugs relacionados con movimiento y combate, ajustes de balance, y apoyo durante etapas de cierre y estabilización del proyecto.

## 1.3 Influencia en el producto final

Mi trabajo tuvo impacto directo en cómo se siente jugar Defender. Las mecánicas del jugador son el punto principal de interacción del usuario con el juego, por lo que el control, el movimiento y el combate eran fundamentales para que el proyecto fuera jugable.

Los ajustes realizados sobre movimiento y disparo ayudaron a que la experiencia se sintiera más cercana a un arcade clásico y menos rígida. Además, los efectos visuales implementados mejoraron la percepción de acciones importantes como hyperspace y ciertos ataques.

Aunque algunos bonos no llegaron al producto final, el proceso de prototipado permitió explorar límites de la arquitectura ECS y dejó trabajo avanzado que podría reutilizarse en futuras versiones.

---

# 2. Ajustes — qué salió bien, mal y qué cambiaría

## 2.1 Qué salió bien

### Arquitectura ECS

El uso de ECS con `esper` facilitó mucho agregar nuevas entidades y sistemas sin depender de jerarquías complejas. Para mecánicas arcade con múltiples enemigos y proyectiles, este enfoque permitió iterar rápidamente.

### Separación de responsabilidades

La división del trabajo entre sistemas del jugador, enemigos y motor ayudó al flujo de trabajo y la prevención de conflictos. Tener responsabilidades relativamente claras hizo más fácil trabajar en paralelo.

### Sensación de movimiento y combate

Considero que uno de los aspectos que mejor funcionó fue el movimiento del jugador. Con varios ajustes de velocidad, aceleración y control se logró una sensación arcade mucho más fluida que en las primeras versiones.

### Experimentación con bonos

Aunque algunos bonos quedaron incompletos, trabajar en ellos me ayudó a aprender sobre seguimiento de objetivos, efectos visuales y problemas de integración dentro de ECS. También permitió experimentar más allá de los requisitos mínimos.

### Integración progresiva

El proyecto evolucionó desde un prototipo básico hasta un juego mucho más cercano a Defender gracias a una integración gradual de sistemas y mecánicas.

## 2.2 Qué salió mal o fue más difícil de lo esperado

### Complejidad de ECS al crecer el proyecto

Aunque ECS ayudó mucho, también generó dificultades cuando comenzaron a existir demasiados sistemas interactuando al mismo tiempo. A veces era difícil rastrear qué sistema estaba modificando una entidad o en qué orden ocurrían ciertos eventos.

### Integración tardía de algunas mecánicas

Algunos sistemas avanzados se integraron demasiado tarde, especialmente bonos y prototipos experimentales. Eso dificultó hacer pruebas suficientes antes del cierre.

### Boss incompleto

El prototipo del boss terminó siendo más complejo de lo esperado. El principal problema fue intentar hacerlo rápidamente sin definir desde el inicio una arquitectura ECS suficientemente limpia. Aunque el comportamiento base funciona, no alcanzó un estado estable ni un código lo suficientemente estructurado, modularizado y limpio como para incluirlo en main. Sin embargo, se puede probar su funcionamiento en la rama "leonardo".

### Tiempo para playtesting

Hubiera sido útil realizar sesiones de prueba más rigurosas para probar cada sistema con el objetivo de pulir mecánicas, solucionar bugs y mejorar la sensación general del juego.

### Audio y pulido general

Aunque el proyecto terminó funcional, quedaron aspectos de sonido y retroalimentación audiovisual menos desarrollados de lo que hubiera querido.

## 2.3 Qué cambiaría en un nuevo proyecto

| Área               | Cambio que realizaría                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Arquitectura ECS   | Definir desde el inicio convenciones más estrictas para sistemas, eventos y flujo de actualización. |
| Bonos y prototipos | Empezar los bonos más temprano para evitar que queden únicamente como experimentos de última hora.  |
| Playtesting        | Programar sesiones periódicas de pruebas desde etapas tempranas del proyecto.                       |
| Integración        | Integrar nuevas mecánicas en ramas pequeñas y hacer merges frecuentes.                              |
| Organización       | Documentar mejor qué sistemas afectan cada entidad y qué dependencias existen.                      |
| Audio y feedback   | Reservar tiempo específico para efectos de sonido y pulido visual desde antes del cierre.           |
| Trabajo personal   | Dividir mejor el tiempo entre implementar features nuevas y estabilizar las ya existentes.          |

---

# 3. Evaluación — aprendizajes y relación con la creación de videojuegos

## 3.1 Resumen de lo aprendido

Este proyecto me permitió entender de forma práctica muchos conceptos vistos durante el curso. Pude entender realmente los retos de coordinar sistemas, mantener arquitectura y construir una experiencia jugable.

El aprendizaje más importante fue comprender el patrón ECS. A diferencia de OOP, en donde se construyen jerarquías de objetos complejos, en ECS se desarrollan componentes y sistemas independientes, lo que facilita extender el juego, pero también exige mayor organización.

Otro aprendizaje importante fue el concepto de “game feel” y cómo pequeños cambios en aceleración, velocidad, efectos visuales o tiempo de respuesta modifican muchísimo la percepción del jugador.

## 3.2 Relación con los temas del curso

| Elemento del curso   | Cómo se aplicó en el proyecto                                          |
| -------------------- | ---------------------------------------------------------------------- |
| ECS                  | Se utilizó como base principal para entidades, componentes y sistemas. |
| Patrones de diseño   | Especialmente Command y separación por sistemas.                       |
| Loop de juego        | Organización del ciclo input → update → render.                        |
| Trabajo colaborativo | Uso de Git, ramas y división de responsabilidades.                     |
| Diseño arcade        | Implementación de mecánicas inspiradas en Defender clásico.            |
| Manejo de assets     | Integración de configuraciones y recursos externos.                    |

## 3.3 Aspectos conceptuales que debo seguir fortaleciendo

- Diseño de arquitectura escalable para videojuegos.
- Mejor manejo de dependencias entre sistemas ECS.
- Balance de dificultad y diseño de progresión.
- Diseño de enemigos y comportamientos más complejos.
- Optimización y organización de proyectos grandes.

## 3.4 Aspectos procedimentales que debo mejorar

- Hacer commits más pequeños y frecuentes.
- Documentar cambios importantes desde etapas tempranas.
- Planear mejor prototipos experimentales.
- Realizar más pruebas automatizadas y playtesting.
- Separar mejor tiempo de desarrollo y tiempo de estabilización.
- Diseñar mecánicas complejas antes de implementarlas directamente.

## 3.5 Cierre personal

Este proyecto, aunque retador, me pareció un ejercicio muy interesante. Desarrollar mecánicas jugables, movimiento y sistemas interactivos , así como la iteración constante y coordinación entre múltiples partes del proyecto, me permitió aprender sobre el desarrollo de videojuegos, un campo que siempre me ha llamado la atención pero que jamás había sabido como adentrarme a el. Considero que el resultado final del proyecto logró capturar gran parte de la esencia arcade de Defenders, y me permitió entender el patrón ECS.
