import globe
import pathfinding
import tools


class Person:

    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.stock_list = []
        self.stock_list_limit = 2

        self.time_last = globe.time.now()
        self.time_last_eat = globe.time.now()
        self.action_super = "idle"
        self.action_construction = None
        self.action_work = None

        self.stat_dict = {"health max": 100, "health current": 100}

    def update(self, map_resource, map_entities, map_topology):

        if globe.time.check(self.time_last_eat, self.ruler_state.time_dur_eat):
            self.eat()
            self.time_last_eat = globe.time.now()

        if self.action_super == "harvest_food":
            self.harvest(map_resource, map_entities, map_topology, globe.CODE_FOOD)
        elif self.action_super == "harvest_wood":
            self.harvest(map_resource, map_entities, map_topology, globe.CODE_WOOD)
        elif self.action_super == "harvest_metal":
            self.harvest(map_resource, map_entities, map_topology, globe.CODE_METAL)
        elif self.action_super == "construct":
            self.construct(map_entities, map_topology, self.action_construction)
        elif self.action_super == "work":
            self.work(map_entities, map_topology, self.action_work)

        if self.stat_dict["health current"] <= 0:
            self.ruler_state.person_list.remove(self)

    def work(self,  map_entities, map_topology, work_object):
        """Send person to work object location and work when adjacent."""

        # construct construct_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(work_object.location):
            if not work_object.working(globe.time.now() - self.time_last):
                self.action_super_set("idle")
                self.action_work = None
            self.time_last = globe.time.now()

        # move to construct object
        else:
            self.move(map_entities, map_topology, work_object.location, adjacent=True)

    def construct(self, map_entities, map_topology, construct_object):
        """Send person to construct object location and construct construct object when adjacent."""

        # construct construct_object in milliseconds until it returns 0
        if self.location in pathfinding.find_edges(construct_object.location):
            if not construct_object.constructing(globe.time.now() - self.time_last):
                self.action_super_set("idle")
                self.action_construction = None
            self.time_last = globe.time.now()

        # move to construct object
        else:
            self.move(map_entities, map_topology, construct_object.location, adjacent=True)

    def harvest(self, map_resource, map_entities, map_topology,  target_resource):

        # deposit stock_list
        if self.location in pathfinding.find_edges(self.ruler_state.location) and target_resource in self.stock_list:
            if globe.time.check(self.time_last, self.ruler_state.time_dur_transfer):
                tools.item_transfer(self.stock_list, self.ruler_state.stock_list, target_resource, 1)
                self.time_last = globe.time.now()

                if target_resource not in self.stock_list:
                    self.action_super_set("idle")

        # move to base
        elif len(self.stock_list) == self.stock_list_limit:
            self.move(map_entities, map_topology, self.ruler_state.location, adjacent=True)

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
                self.move(map_entities, map_topology, target_location)
            else:
                self.action_super_set("idle")

    def move(self, map_entities, map_topology, target, adjacent=False):
        
        if globe.time.check(self.time_last, self.ruler_state.time_dur_move):
            path = pathfinding.astar(map_entities, map_topology, self.location, target, adjacent)
            if len(path) > 1:
                self.location = path[1]
            else:
                self.action_super_set("idle")
            self.time_last = globe.time.now()

    def action_super_set(self, action_new):
        
        self.action_super = action_new

    def eat(self):

        if globe.CODE_FOOD in self.stock_list:
            tools.item_remove(self.stock_list, globe.CODE_FOOD, 1)
        elif globe.CODE_FOOD in self.ruler_state.stock_list:
            tools.item_remove(self.ruler_state.stock_list, globe.CODE_FOOD, 1)
        else:
            pass


