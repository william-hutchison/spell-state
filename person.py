import glob
import pathfinding
import tools


class Person:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.stock_list_limit = 2

        self.time_last = glob.time.now()
        self.time_last_eat = glob.time.now()
        self.action_super = "idle"
        self.action_construction = None

        self.stat_dict = {"health max": 100, "health current": 100}


    def update(self, map_resource, map_entities):

        if glob.time.check(self.time_last_eat, self.ruler_state.time_dur_eat):
            self.eat()
            self.time_last_eat = glob.time.now()

        if self.action_super == "harvest_food":
            self.harvest(map_resource, map_entities, glob.FOOD)
        elif self.action_super == "harvest_wood":
            self.harvest(map_resource, map_entities, glob.WOOD)
        elif self.action_super == "harvest_metal":
            self.harvest(map_resource, map_entities, glob.METAL)
        elif self.action_super == "build":
            self.build(map_entities, self.action_construction)

        if self.stat_dict["health current"] <= 0:
            self.ruler_state.person_list.remove(self)

    def harvest(self, map_resource, map_entities, target_resource):

        # deposit stock_list
        if self.location in pathfinding.find_edges(self.ruler_state.location) and target_resource in self.stock_list:
            if glob.time.check(self.time_last, self.ruler_state.time_dur_transfer):
                tools.item_transfer(self.stock_list, self.ruler_state.stock_list, target_resource, 1)
                self.time_last = glob.time.now()

                if target_resource not in self.stock_list:
                    self.action_super_set("idle")

        # move to base
        elif len(self.stock_list) == self.stock_list_limit:
            self.move(map_entities, self.ruler_state.location, adjacent=True)

        # harvest target resource
        elif map_resource[self.location[1]][self.location[0]] == target_resource:
            if glob.time.check(self.time_last, self.ruler_state.time_dur_harvest):            
                tools.item_add(self.stock_list, target_resource, 1)
                self.time_last = glob.time.now()

        # move to the closest target resource
        else:
            targets_all = pathfinding.find_targets(map_resource, target_resource)
            targets_free = pathfinding.find_free(targets_all, map_entities)
            if targets_free:
                target_location = pathfinding.find_closest(self.location, targets_free)
                self.move(map_entities, target_location)
            else:
                self.action_super_set("idle")

    def build(self, map_entities, build_object):
        """Send person to build object location."""

        # construct build_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(build_object.location):            
            if not build_object.constructing(glob.time.now() - self.time_last):
                self.action_super_set("idle")
            self.time_last = glob.time.now()

        # move to build object
        else:
            self.move(map_entities, build_object.location, adjacent=True)

    def move(self, map_entities, target, adjacent=False):
        
        if glob.time.check(self.time_last, self.ruler_state.time_dur_move):
            path = pathfinding.astar(map_entities, self.location, target, adjacent)
            if path:
                self.location = path[1]
            else:
                self.action_super_set("idle")
            self.time_last = glob.time.now()

    def action_super_set(self, action_new):
        
        self.action_super = action_new

    def eat(self):

        if glob.FOOD in self.stock_list:
            tools.item_remove(self.stock_list, glob.FOOD, 1)
        elif glob.FOOD in self.ruler_state.stock_list:
            tools.item_remove(self.ruler_state.stock_list, glob.FOOD, 1)
        else:
            pass


