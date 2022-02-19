import random

import wizards
import buildings
import persons
import pathfinding
import tools
import globe


class State:

    def __init__(self, location, map_entities, map_topology):

        self.location = location
        self.wizard = None
        self.building_list = []
        self.person_list = []
        self.stock_list = []
        self.other_states = []
        self.stat_dict = {"loyalty": 50, "fear": 50}

        self.time_last_order = globe.time.now()
        self.time_last_birth = globe.time.now()
        self.time_dur_order = 200
        self.time_dur_birth = 4000

        self.time_dur_move = 200
        self.time_dur_eat = 20000
        self.time_dur_transfer = 100#0
        self.time_dur_construct = 600#0
        self.time_dur_harvest = 400#0
        self.time_dur_attack = 400

        self.pop_limit = 0
        self.pop_current = 0

        # TODO Intelligently decide where to place tower / let player choose
        self.wizard = self.create_wizard(map_entities, map_topology, self.location)
        self.building_list.append(self.create_building("tower", map_entities, map_topology, self.location))
        
    def update(self, map_resource, map_entities, map_topology):

        # assign person actions
        if globe.time.check(self.time_last_order, self.time_dur_order):
            self.assign(self.person_list, self.building_list)
            self.time_last_order = globe.time.now()

        # decide what to construct TODO Intelligently decide what to construct next
        if tools.item_count(self.stock_list, globe.CODE_WOOD) > globe.COST_HOUSE:
            build_attempt = "house"
        elif tools.item_count(self.stock_list, globe.CODE_METAL) > globe.COST_SHRINE:
            build_attempt = "shrine"
        else:
            build_attempt = None
        
        if build_attempt:
            if temp_building := self.create_building(build_attempt, map_entities, map_topology, self.location):
                self.building_list.append(temp_building)
                for item in buildings.building_info[build_attempt][1]:
                    tools.item_remove(self.stock_list, item[0], item[1])
        
        # increase population
        if self.pop_current < self.pop_limit:
            if globe.time.check(self.time_last_birth, self.time_dur_birth):
                if temp_person := self.create_person(map_entities, map_topology, self.location):
                    self.person_list.append(temp_person)
                self.time_last_birth = globe.time.now()

        # update entities
        for building in self.building_list:
            building.update()
        for person in self.person_list:
            person.update(map_resource, map_entities, map_topology)

    def create_wizard(self, map_entities, map_topology, location_tower):
        """Create wizard at the edge of the tower. Returns new wizard object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)
        if possible_locations:
            location = random.choice(possible_locations)

            return wizards.Wizard(self, location)

    def create_building(self, kind, map_entities, map_topology, location_tower):
        """Create building site of a given kind at an appropriate location. Returns new building
        object."""

        # check for adequate resources
        for item in buildings.building_info[kind][1]:
            if not tools.item_count(self.stock_list, item[0]) > item[1]:
                return None

        # construct tower
        if kind == "tower":
            return buildings.building_info[kind][0](self, location_tower)

        # construct buildings within radius of tower
        elif kind in ["house", "shrine", "tavern"]:
            possible_locations = pathfinding.find_within_radius(location_tower, 10)
            possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)
            if possible_locations:
                location = random.choice(possible_locations)
                return buildings.building_info[kind][0](self, location)

        return None

    def create_person(self, map_entities, map_topology, location_tower):
        """Create person at the edge of the tower. Returns new person object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)
        if possible_locations:
            location = random.choice(possible_locations)
            self.pop_current += 1
            return persons.Person(self, location)

        return None

    def assign(self, person_list, building_list):
        """Assign person to harvest resource of given kind."""

        construct_weight = 10
        work_weight = 5
        harvest_weight = 5
        attack_weight = 20

        target_state = self.other_states[0]

        idle_person_list = [i for i in person_list if i.action_super == "idle"]
        construction_list = [i for i in building_list if i.under_construction]
        shrine_list = ([i for i in building_list if not i.under_construction and type(i).__name__ == "Shrine"])
        attack_list = ([i.location for i in target_state.person_list])

        if not construction_list:
            construct_weight = 0
        if not shrine_list:
            work_weight = 0
        if not attack_list:
            attack_weight = 0

        if idle_person_list:
            dice = random.randint(0, construct_weight+work_weight+harvest_weight)
            if dice < construct_weight:
                self.assign_build(person_list, idle_person_list, construction_list)
            elif dice < construct_weight+work_weight:
                self.assign_work(person_list, idle_person_list, shrine_list)
            elif dice < construct_weight+work_weight+attack_weight:
                self.assign_attack(idle_person_list, target_state)
            else:
                # TODO Give harvesting its own assign function to match construct and work
                dice = random.randint(1, 3)
                assignment = "idle"
                if dice == 1:
                    assignment = "harvest_food"
                elif dice == 2:
                    assignment = "harvest_wood"
                elif dice == 3:
                    assignment = "harvest_metal"
                idle_person_list[0].action_super_set(assignment)

    def assign_work(self, person_list, idle_person_list, building_list):
        """Assign the closest person in the provided idle person list and assign them to construct
        given building."""

        for building in building_list:

            # check if building already has construction assigned
            work_assigned = [i for i in person_list if i.action_work == building]
            if not work_assigned:

                # check for and assign appropriate person to construction
                if idle_person_list:
                    person_location = pathfinding.find_closest(building.location, [i.location for i in idle_person_list])
                    person = [i for i in idle_person_list if i.location == person_location].pop()
                    person.action_super_set("work")
                    person.action_work = building

    def assign_build(self, person_list, idle_person_list, building_list):
        """Assign the closest person in the provided idle person list and assign them to construct
        given building."""

        for building in building_list:

            # check if building already has construction assigned
            construction_assigned = [i for i in person_list if i.action_construction == building]
            if not construction_assigned:

                # check for and assign appropriate person to construction
                if idle_person_list:
                    person_location = pathfinding.find_closest(building.location, [i.location for i in idle_person_list])
                    person = [i for i in idle_person_list if i.location == person_location].pop()
                    person.action_super_set("construct")
                    person.action_construction = building

    def assign_attack(self, idle_person_list, target_state):

        # check for and assign appropriate person to construction
        if idle_person_list and target_state.person_list:
            target_location = pathfinding.find_closest(self.location, [i.location for i in target_state.person_list])
            person_location = pathfinding.find_closest(target_location, [i.location for i in idle_person_list])
            person = [i for i in idle_person_list if i.location == person_location].pop()
            person.action_super_set("attack")
            person.action_attack = [i for i in target_state.person_list if i.location == target_location].pop()

    def increase_pop_limit(self, target_state, amount):
        
        target_state.pop_limit += amount
