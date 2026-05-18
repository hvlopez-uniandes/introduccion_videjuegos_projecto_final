"""Utilidades compartidas para colisiones y resolución de dimensiones de entidades."""

import esper

from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface


def get_entity_dims(entity: int, fallback: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    """Devuelve el ancho y alto de una entidad, priorizando CSurface sobre CSize.

    Args:
        entity: ID de la entidad en el mundo ECS.
        fallback: Tupla (w, h) a retornar si la entidad no tiene ni CSurface ni CSize.

    Returns:
        Tupla (width, height) como floats.
    """
    surf = esper.try_component(entity, CSurface)
    if surf is not None:
        return float(surf.area_w), float(surf.area_h)
    size = esper.try_component(entity, CSize)
    if size is not None:
        return float(size.w), float(size.h)
    return float(fallback[0]), float(fallback[1])


def aabb_overlap(
    ax: float, ay: float, aw: float, ah: float,
    bx: float, by: float, bw: float, bh: float,
) -> bool:
    """Comprueba si dos rectángulos AABB se solapan.

    Args:
        ax, ay: Posición superior-izquierda del rectángulo A.
        aw, ah: Dimensiones del rectángulo A.
        bx, by: Posición superior-izquierda del rectángulo B.
        bw, bh: Dimensiones del rectángulo B.

    Returns:
        True si los rectángulos se intersectan.
    """
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
