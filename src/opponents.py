import pathfinding
import timer


class Opponent:
    """Class to control opponent wizards."""

    def __init__(self, subject_wizard):

        self.subject_wizard = subject_wizard
        self.ruler_state = subject_wizard.ruler_state

    def update(self, map_topology, map_resource, map_item, map_entities):

        # TODO This is messy
        move_character_attempt = None
        cast_attempt = None
        move_spell_attempt = None
        target = None 

        for state in list(self.ruler_state.relation_dict.keys()):
            if self.ruler_state.relation_dict[state] < 50:
                cast_attempt, move_spell_attempt = self.attempt_attack(map_entities)
                target_cross = pathfinding.find_within_cross(state.wizard.location, 4) 
                if self.subject_wizard.location not in target_cross:
                    # TODO Replace with dedicated pathfinding function. Use combo of astar and find_closest to check options one by one, also require line of sight
                    target = pathfinding.find_closest(self.subject_wizard.location, target_cross)

        if target:
            move_character_attempt = self.move_attempt(map_entities, map_topology, target)

        self.subject_wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)

    def attempt_attack(self, map_entities):
        """Attempt to attack any nearby wizard."""

        cast_attempt = None
        move_spell_attempt = None

        # Detect nearby entities
        aware_tiles = pathfinding.find_within_radius(self.subject_wizard.location, 6)
        aware_entities = [map_entities[tile[1]][tile[0]] for tile in aware_tiles if map_entities[tile[1]][tile[0]]]

        # Attack nearby entities
        for entity in aware_entities:
            if type(entity).__name__ == 'Wizard' and entity.ruler_state != self.ruler_state:
                cast_attempt = "fireball"

                if entity.location in pathfinding.find_within_cross(self.subject_wizard.location, 4):
                    move_spell_attempt = pathfinding.find_direction(self.subject_wizard.location, entity.location)

        return cast_attempt, move_spell_attempt

    def move_attempt(self, map_entities, map_topology, target, adjacent=False):
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
