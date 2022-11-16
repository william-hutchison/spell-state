import pathfinding


class Opponent:

    def __init__(self, subject_wizard):

        self.subject_wizard = subject_wizard
        self.ruler_state = subject_wizard.ruler_state

    def update(self, map_topology, map_resource, map_item, map_entities):

        move_character_attempt = None
        cast_attempt, move_spell_attempt = self.attempt_attack(map_entities)


        self.subject_wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)

    def attempt_attack(self, map_entities):

        cast_attempt = None
        move_spell_attempt = None

        # Detect nearby entities
        aware_tiles = pathfinding.find_within_radius(self.subject_wizard.location, 2)
        aware_entities = [map_entities[tile[1]][tile[0]] for tile in aware_tiles if map_entities[tile[1]][tile[0]]]

        # Attack nearby entities
        for entity in aware_entities:
            if type(entity).__name__ == 'Wizard' and entity.ruler_state != self.ruler_state:
                cast_attempt = "fireball"

                if entity.location in pathfinding.find_within_cross(self.subject_wizard.location, 2):
                    diff = (entity.location[0] - self.subject_wizard.location[0], entity.location[1] - self.subject_wizard.location[1])
                    if diff[0] > 0:
                        move_spell_attempt = (1, 0)
                    elif diff[0] < 0:
                        move_spell_attempt = (-1, 0)
                    elif diff[1] > 0:
                        move_spell_attempt = (0, 1)
                    elif diff[1] < 0:
                        move_spell_attempt = (0, -1)

        return cast_attempt, move_spell_attempt
