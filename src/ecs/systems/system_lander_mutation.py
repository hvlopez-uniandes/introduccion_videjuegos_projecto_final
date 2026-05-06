"""Al alcanzar parte superior, Lander consume astronauta y se convierte en Mutant ECS."""

import esper

from src.ecs.components.c_lander_ai import CLanderAI
from src.ecs.components.c_position import CPosition
from src.ecs.components.c_size import CSize
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagEnemy, CTagLander
from src.ecs.systems.mutate_spawn import spawn_mutant_at
from src.engine.audio_util import play_sound
import src.engine.game_state as game_state


def system_lander_mutate_to_alien():
    to_replace = []
    for ent, (pos, ai, _te, _tl) in esper.get_components(
        CPosition,
        CLanderAI,
        CTagEnemy,
        CTagLander,
    ):
        if ai.capture_phase != "ascend":
            continue
        if pos.y > ai.mutate_screen_y_px + 0.5:
            continue
        if esper.try_component(ent, CSize) is None and esper.try_component(ent, CSurface) is None:
            continue
        carried = ai.carried_astronaut_entity
        to_replace.append((ent, pos.x, pos.y, carried))

    for ent, px, py, carried in to_replace:
        play_sound(str(game_state.get_rule("sound_lander_mutate", "")), 0.58)
        spawn_mutant_at(px, py)
        if carried >= 0 and esper.entity_exists(carried):
            esper.delete_entity(carried, immediate=True)
        esper.delete_entity(ent, immediate=True)
