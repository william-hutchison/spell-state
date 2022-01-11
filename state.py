import random

import wizard
import building
import person
import pathfinding
import tools
import glob


class State:

    def __init__(self, location, map_entities):

        self.location = location
        self.wizard = None
        self.building_list = []
        self.person_list = []
        self.stock_list = []

        self.time_last_order = glob.time.now()
        self.time_last_birth = glob.time.now()
        self.time_dur_order = 200
        self.time_dur_birth = 4000

        self.time_dur_move = 200#0
        self.time_dur_eat = 2000
        self.time_dur_transfer = 100#0
        self.time_dur_construct = 600#0
        self.time_dur_harvest = 400#0

        self.pop_limit = 0
        self.pop_current = 0

        # IMPROVE TO ROBUST STARTING LOCATION
        self.wizard = self.create_wizard(map_entities, self.location)
        self.building_list.append(self.create_building("tower", map_entities, self.location)) 
        
    def update(self, map_resource, map_entities):

        # assign person actions
        if glob.time.check(self.time_last_order, self.time_dur_order):
            self.assign(self.person_list, self.building_list)
            self.time_last_order = glob.time.now()

        # construct buildings
        if tools.item_count(self.stock_list, glob.WOOD) > glob.HOUSE_COST:
            if temp_building := self.create_building("house", map_entities, self.location):
                self.building_list.append(temp_building)

        # increase population
        if self.pop_current < self.pop_limit:
            if glob.time.check(self.time_last_birth, self.time_dur_birth):
                if temp_person := self.create_person(map_entities, self.location):
                    self.person_list.append(temp_person)
                self.time_last_birth = glob.time.now()

        # update entities
        for building in self.building_list:
            building.update()
        for person in self.person_list:
            person.update(map_resource, map_entities)

    def create_wizard(self, map_entities, location_tower):
        """Create wizard at the edge of the tower. Returns new wizard object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities)
        if possible_locations:
            location = random.choice(possible_locations)

            return wizard.Wizard(self, location)

    def create_building(self, kind, map_entities, location_tower):
        """Create building site of a given kind at an appropriate location. Returns new building
        object."""

        if kind == "tower":
            return building.Tower(self, location_tower)

        elif kind == "house":
            possible_locations = pathfinding.find_within_radius(location_tower, 10)
            possible_locations = pathfinding.find_free(possible_locations, map_entities)
            if possible_locations:
                location = random.choice(possible_locations)
                tools.item_remove(self.stock_list, glob.WOOD, glob.HOUSE_COST)
                return building.House(self, location)

        return None

    def create_person(self, map_entities, location_tower):
        """Create person at the edge of the tower. Returns new person object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities)
        if possible_locations:
            location = random.choice(possible_locations)

            self.pop_current += 1
            return person.Person(self, location)
        return None

    def assign(self, person_list, building_list):
        """Assign person to harvest resource of given kind."""

        idle_person_list = [i for i in person_list if i.action_super == "idle"]
        construction_list = [i for i in building_list if i.under_construction]

        if construction_list:
            self.assign_build(person_list, idle_person_list, construction_list)

        # MOVE TO OWN  FUNCTION AND IMPROVE TO INTELLIGENTLY DECIDE WHAT TO HARVEST
        idle_person_list = [i for i in person_list if i.action_super == "idle"]
        assignment = "idle"
        for person in idle_person_list:
            dice = random.randint(1, 3)
            if dice == 1:
                assignment = "harvest_food"
            elif dice == 2:
                assignment = "harvest_wood"
            elif dice == 3:
                assignment = "harvest_metal"

            person.action_super_set(assignment)

    def assign_build(self, person_list, idle_person_list, building_list):
        """Assign appropriate person from person_list to build given building."""

        for building in building_list:

            # check if building already has construction assigned
            construction_assigned = [i for i in person_list if i.action_construction == building]
            if not construction_assigned:

                # check for and assign appropriate person to construction
                if idle_person_list:
                    person_location = pathfinding.find_closest(building.location, [i.location for i in idle_person_list])
                    person = [i for i in idle_person_list if i.location == person_location].pop()
                    person.action_super_set("build")
                    person.action_construction = building

    def increase_pop_limit(self, target_state, amount):
        
        target_state.pop_limit += amount
