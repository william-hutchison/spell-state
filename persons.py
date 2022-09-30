import pygame as pg

import globe
import pathfinding
import tools
import audio


class Person:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.sprite = pg.image.load('sprites/person.png')
        self.stock_list = []
        self.stock_list_limit = 2

        self.time_last = globe.time.now()
        self.time_last_eat = globe.time.now()
        self.action_super = "a_idle"
        self.action_construction = None
        self.action_work = None
        self.action_attack = None

        self.stat_dict = {"u_health_max": 100,
                          "u_health_current": 100,
                          "u_attack_damage": 20}

    def update(self, map_resource, map_entities, map_topology, map_traffic):

        if globe.time.check(self.time_last_eat, self.ruler_state.time_dur_eat):
            self.eat()
            self.time_last_eat = globe.time.now()

        if self.action_super == "a_harvest_food":
            self.harvest(map_resource, map_entities, map_topology, map_traffic, "i_food")
        elif self.action_super == "a_harvest_wood":
            self.harvest(map_resource, map_entities, map_topology, map_traffic, "i_wood")
        elif self.action_super == "a_harvest_metal":
            self.harvest(map_resource, map_entities, map_topology, map_traffic, "i_metal")
        elif self.action_super == "a_construct":
            self.construct(map_entities, map_topology, map_traffic, self.action_construction)
        elif self.action_super == "a_work":
            self.work(map_entities, map_topology, map_traffic, self.action_work)
        elif self.action_super == "a_attack":
            self.attack(map_entities, map_topology, map_traffic, self.action_attack)

        if self.stat_dict["u_health_current"] <= 0:
            self.ruler_state.person_list.remove(self)
            # TODO Drop items upon destruction

    def work(self, map_entities, map_topology, map_traffic, work_object):
        """Send person to work object location and work when adjacent."""

        # construct construct_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(work_object.location):
            if not work_object.working(globe.time.now() - self.time_last):
                self.action_super_set("a_idle")
                self.action_work = None
            self.time_last = globe.time.now()

        # move to construct object
        else:
            self.move(map_entities, map_topology, map_traffic, work_object.location, adjacent=True)

    def construct(self, map_entities, map_topology, map_traffic, construct_object):
        """Send person to construct object location and construct construct object when adjacent."""

        # construct construct_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(construct_object.location):
            if not construct_object.constructing(globe.time.now() - self.time_last):
                self.action_super_set("a_idle")
                self.action_construction = None
            self.time_last = globe.time.now()

        # move to construct object
        else:
            self.move(map_entities, map_topology, map_traffic, construct_object.location, adjacent=True)

    def attack(self, map_entities, map_topology, map_traffic, attack_object):

        # attack attack_object
        if self.location in pathfinding.find_edges(attack_object.location):
            if globe.time.check(self.time_last, self.ruler_state.time_dur_attack):

                attack_object.stat_dict["u_health_current"] -= self.stat_dict["u_attack_damage"]
                if attack_object.stat_dict["u_health_current"] <= 0:
                    self.action_attack = None
                    self.action_super_set("a_idle")
                self.time_last = globe.time.now()

        # move to attack object
        else:
            self.move(map_entities, map_topology, map_traffic, attack_object.location, adjacent=True)

    def harvest(self, map_resource, map_entities, map_topology, map_traffic, target_resource):

        # TODO Replace with generic deposit item function
        # deposit stock_list
        if self.location in pathfinding.find_edges(self.ruler_state.building_list[0].location) and target_resource in self.stock_list:
            if globe.time.check(self.time_last, self.ruler_state.time_dur_transfer):
                tools.item_transfer(self.stock_list, self.ruler_state.building_list[0].stock_list, target_resource, 1)
                self.time_last = globe.time.now()

                if target_resource not in self.stock_list:
                    self.action_super_set("a_idle")

        # move to base
        elif len(self.stock_list) == self.stock_list_limit:
            self.move(map_entities, map_topology, map_traffic, self.ruler_state.location, adjacent=True)

        # harvest target resource
        elif map_resource[self.location[1]][self.location[0]] == target_resource:
            if globe.time.check(self.time_last, self.ruler_state.time_dur_harvest):            
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
                self.action_super_set("a_idle")

    def move(self, map_entities, map_topology, map_traffic, target, adjacent=False):
        
        if globe.time.check(self.time_last, self.ruler_state.time_dur_move):
            path = pathfinding.astar(map_entities, map_topology, self.location, target, adjacent)
            if len(path) > 1:
                self.location = path[1]
            else:
                self.action_super_set("a_idle")
            self.time_last = globe.time.now()

            # add location to traffic map
            audio.audio.play_relative_sound("n_move", self.location)
            map_traffic[self.location[1]][self.location[0]] += 1

    def action_super_set(self, action_new):
        
        self.action_super = action_new

    def eat(self):

        if "i_food" in self.stock_list:
            tools.item_remove(self.stock_list, "i_food", 1)
        elif "i_food" in self.ruler_state.stock_list:
            tools.item_remove(self.ruler_state.stock_list, "i_food", 1)
        else:
            pass