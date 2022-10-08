import pygame as pg

import globe
import pathfinding
import tools
import audio


class Person:

    def __init__(self, ruler_state, location):

        self.stat_dict = {"stock_max": 2,
                          "health_max": 100,
                          "health_current": 100,
                          "attack_damage": 20,
                          "move_duration": 600,
                          "transfer_duration": 600,
                          "eat_duration": 20000,
                          "harvest_duration": 800,
                          "attack_duration": 400}

        self.sprite = pg.image.load('../sprites/person.png')
        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []

        self.action_super = None
        self.action_target = None

        self.time_last = globe.time.now()
        self.time_last_eat = globe.time.now()

    def update(self, map_resource, map_entities, map_topology, map_item, map_traffic):

        if globe.time.check(self.time_last_eat, self.stat_dict["eat_duration"]):
            self.eat()
            self.time_last_eat = globe.time.now()

        if self.action_super:
            self.ruler_state.action_dict[self.action_super]["function"](self, map_entities, map_topology, map_resource, map_traffic, self.action_target)

        if self.stat_dict["health_current"] <= 0:
            pathfinding.drop_items(self.location, self.stock_list, map_topology, map_item)
            self.ruler_state.person_list.remove(self)

    def haul(self, map_entities, map_topology, map_resource, map_traffic, haul_link):

        if haul_link[2] in self.stock_list:

            # Deposit item
            if self.location in pathfinding.find_edges(haul_link[0].location):
                if haul_link[2] in haul_link[0].stock_list_needed:
                    if globe.time.check(self.time_last, self.stat_dict["transfer_duration"]):
                        tools.item_transfer(self.stock_list, haul_link[0].stock_list, haul_link[2], 1)
                        self.time_last = globe.time.now()
                        self.action_set(None, None)
                else:
                    self.action_set(None, None)
            # Move to haul to location
            else:
                self.move(map_entities, map_topology, map_traffic, haul_link[0].location, adjacent=True)

        else:
            # Collect item
            if self.location in pathfinding.find_edges(haul_link[1].location):
                if globe.time.check(self.time_last, self.stat_dict["transfer_duration"]):
                    if haul_link[2] in haul_link[1].stock_list:
                        tools.item_transfer(haul_link[1].stock_list, self.stock_list, haul_link[2], 1)
                    else:
                        self.action_set(None, None)
                    self.time_last = globe.time.now()
            # Move to haul from location
            else:
                self.move(map_entities, map_topology, map_traffic, haul_link[1].location, adjacent=True)

    def work(self, map_entities, map_topology, map_resource, map_traffic, work_object):
        """Send person to work object location and work when adjacent."""

        # work at work_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(work_object.location):
            if not work_object.working(globe.time.now() - self.time_last):
                self.action_set(None, None)
            self.time_last = globe.time.now()

        # move to work object
        else:
            self.move(map_entities, map_topology, map_traffic, work_object.location, adjacent=True)

    def construct(self, map_entities, map_topology, map_resource, map_traffic, construct_object):
        """Send person to construct object location and construct construct object when adjacent."""

        # construct construct_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(construct_object.location):
            if not construct_object.constructing(globe.time.now() - self.time_last):
                self.action_set(None, None)
            self.time_last = globe.time.now()

        # move to construct object
        else:
            self.move(map_entities, map_topology, map_traffic, construct_object.location, adjacent=True)

    def attack(self, map_entities, map_topology, map_resource, map_traffic, attack_object):

        # attack attack_object
        if self.location in pathfinding.find_edges(attack_object.location):
            if globe.time.check(self.time_last, self.stat_dict["attack_duration"]):

                attack_object.stat_dict["health_current"] -= self.stat_dict["attack_damage"]
                if attack_object.stat_dict["health_current"] <= 0:
                    self.action_set(None, None)
                self.time_last = globe.time.now()

        # move to attack object
        else:
            self.move(map_entities, map_topology, map_traffic, attack_object.location, adjacent=True)

    def harvest(self, map_entities, map_topology, map_resource, map_traffic, target_resource):

        # TODO Replace with generic deposit item function
        # deposit stock_list
        if self.location in pathfinding.find_edges(self.ruler_state.building_list[0].location) and target_resource in self.stock_list:
            if globe.time.check(self.time_last, self.stat_dict["transfer_duration"]):
                tools.item_transfer(self.stock_list, self.ruler_state.building_list[0].stock_list, target_resource, 1)
                self.time_last = globe.time.now()

                if target_resource not in self.stock_list:
                    self.action_set(None, None)

        # move to base
        elif len(self.stock_list) == self.stat_dict["stock_max"]:
            self.move(map_entities, map_topology, map_traffic, self.ruler_state.location, adjacent=True)

        # harvest target resource
        elif map_resource[self.location[1]][self.location[0]] == target_resource:
            if globe.time.check(self.time_last, self.stat_dict["harvest_duration"]):
                tools.item_add(self.stock_list, target_resource, 1)
                self.time_last = globe.time.now()

        # move to the closest target resource
        else:
            targets_all = pathfinding.find_targets(map_resource, target_resource)
            targets_free = pathfinding.find_free(targets_all, map_entities, map_topology)
            if targets_free:
                target_location = pathfinding.find_closest(self.location, targets_free)
                self.move(map_entities, map_topology, map_traffic, target_location)
            else:
                self.action_set(None, None)

    def move(self, map_entities, map_topology, map_traffic, target, adjacent=False):
        
        if globe.time.check(self.time_last, self.stat_dict["move_duration"]):
            path = pathfinding.astar(map_entities, map_topology, self.location, target, adjacent)
            if len(path) > 1:
                self.location = path[1]
            else:
                self.action_set(None, None)
            self.time_last = globe.time.now()

            # add move location to traffic map
            audio.audio.play_relative_sound("n_move", self.location)
            map_traffic[self.location[1]][self.location[0]] += 1

    def action_set(self, action_super, action_target):

        self.action_super = action_super
        self.action_target = action_target

    def eat(self):

        if "i_food" in self.stock_list:
            tools.item_remove(self.stock_list, "i_food", 1)
        else:
            # TODO Make person pickup food if possible, need a general purpose item pickup function
            self.stat_dict["health_current"] -= 5
            pass
