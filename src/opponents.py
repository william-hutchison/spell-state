import random

import pathfinding
import timer


class Opponent:
    """Class to control opponent wizards."""

    def __init__(self, subject_wizard):

        self.subject_wizard = subject_wizard

        self.ruler_state = subject_wizard.ruler_state

        self.action_super = None
        self.action_target = None

    def update(self, map_topology, map_resource, map_item, map_entities):

        # Prevent wizard control if the wizard has been destroyed
        if not self.subject_wizard:
            return None

        # Check for wizard destruction
        if self.subject_wizard.stat_dict["health_current"] <= 0:
            pathfinding.drop_items(self.subject_wizard.location, self.subject_wizard.stock_list, map_topology, map_item)
            self.subject_wizard.spell_list = []
            self.ruler_state.wizard = None
            self.subject_wizard = None
            return None

        # Prevent wizard control if the state has been defeated
        if self.ruler_state.defeated:
            return None

        # TODO This is messy
        move_character_attempt = None
        move_spell_attempt = None
        cast_attempt = None

        # TODO Replace with intelligent decision making function
        # Assign action_super
        self.action_super = "wander"
        for state in list(self.ruler_state.relation_dict.keys()):
            if self.ruler_state.relation_dict[state] < 50:
                self.action_super = "attack"
                self.action_target = state.wizard

        # Wander aimlessly around the map
        if self.action_super == "wander":
            self.action_target = self.wander()
            if self.action_target:
                move_character_attempt = self.attempt_move(map_entities, map_topology, self.action_target)

        # Move to and attack the action_target entity
        elif self.action_super == "attack":
            if self.action_target:
                cast_attempt, move_spell_attempt = self.attempt_fireball(map_entities, self.action_target)
                target_cross = pathfinding.find_within_cross(self.action_target.location, 4)
                if self.subject_wizard.location not in target_cross:
                    # TODO Replace with dedicated pathfinding function. Use combo of astar and find_closest to check options one by one, also require line of sight
                    move_character_attempt = self.attempt_move(map_entities, map_topology, pathfinding.find_closest(self.subject_wizard.location, target_cross))

        self.subject_wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)

    def wander(self):

        if not self.action_target or self.action_target == self.subject_wizard.location:
            target = random.choice(pathfinding.find_within_radius(self.subject_wizard.location, 12))
        else:
            target = self.action_target

        return target

    def attempt_fireball(self, map_entities, target):
        """Attempt to cast a fireball at the target wizard."""

        cast_attempt = None
        move_spell_attempt = None

        # Detect nearby entities
        aware_tiles = pathfinding.find_within_radius(self.subject_wizard.location, 6)
        aware_entities = [map_entities[tile[1]][tile[0]] for tile in aware_tiles if map_entities[tile[1]][tile[0]]]

        # Attack nearby entities
        for entity in aware_entities:
            if entity == target:
                cast_attempt = "fireball"
                if entity.location in pathfinding.find_within_cross(self.subject_wizard.location, 4):
                    move_spell_attempt = pathfinding.find_direction(self.subject_wizard.location, entity.location)

        return cast_attempt, move_spell_attempt

    def attempt_move(self, map_entities, map_topology, target, adjacent=False):
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
