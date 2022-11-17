import pathfinding
import timer


class Opponent:
    """Class to control opponent wizards."""

    def __init__(self, subject_wizard):

        self.subject_wizard = subject_wizard
        self.ruler_state = subject_wizard.ruler_state

    def update(self, map_topology, map_resource, map_item, map_entities):

        target = (1, 1) # FOR TESTING
        move_character_attempt = self.move_attempt(map_entities, map_topology, target)
        cast_attempt, move_spell_attempt = self.attempt_attack(map_entities)

        self.subject_wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)

    def attempt_attack(self, map_entities):
        """Attempt to attack any nearby wizard."""

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
                    move_spell_attempt = pathfinding.find_direction(self.subject_wizard.location, entity.location)

        return cast_attempt, move_spell_attempt

    def move_attempt(self, map_entities, map_topology, target, adjacent=True):
        """Finds the shortest path to target and returns a tuple vector of next step. Returns None if no path is
        found."""

        # TODO Avoid checking timer twice (here and within the wizard)
        if timer.timer.check(self.subject_wizard.time_last, self.subject_wizard.stat_dict["move_duration"]):

            # Find the shortest path to target
            path = pathfinding.astar(map_entities, map_topology, self.subject_wizard.location, target, adjacent)

            # Return a direction vector for the next move towards the target
            if len(path) > 1:
                return pathfinding.find_direction(self.subject_wizard.location, path[1])
            else:
                return None
