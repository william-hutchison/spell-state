import random

import wizards
import buildings
import persons
import pathfinding
import globe
import audio


class State:

    def __init__(self, location, map_entities, map_topology, map_traffic):

        self.location = location
        self.building_list = []
        self.person_list = []
        self.other_states = []
        self.colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.action_dict = {None: {"weight": 10, "function": None},
                            "a_harvest_food": {"weight": 10, "function": persons.Person.harvest},
                            "a_harvest_wood": {"weight": 10, "function": persons.Person.harvest},
                            "a_harvest_metal": {"weight": 10, "function": persons.Person.harvest},
                            "a_haul": {"weight": 100, "function": persons.Person.haul},
                            "a_construct": {"weight": 100, "function": persons.Person.construct},
                            "a_work": {"weight": 10, "function": persons.Person.work},
                            "a_attack": {"weight": 10, "function": persons.Person.attack}}

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

        self.person_list_limit = 0

        # TODO Intelligently decide where to place tower / let player choose
        # TODO Prevent placement in water
        self.wizard = self.create_wizard(map_entities, map_topology, self.location)
        self.building_list.append(self.create_building("b_tower", map_entities, map_topology, map_traffic, self.location))
        self.temp = True

    def update(self, map_resource, map_entities, map_topology, map_item, map_traffic):

        self.tune_action_wight()

        # assign person actions
        if globe.time.check(self.time_last_order, self.time_dur_order):
            self.assign(self.person_list, self.building_list)
            self.time_last_order = globe.time.now()

        # decide what to construct 
        # TODO Intelligently decide what to construct next
        if self.temp:
            build_attempt = random.choice(["b_house", "b_lab_offence"])
            self.building_list.append(self.create_building(build_attempt, map_entities, map_topology, map_traffic, self.location))
            self.temp = False

        # increase population
        if len(self.person_list) < self.person_list_limit:
            if globe.time.check(self.time_last_birth, self.time_dur_birth):
                if temp_person := self.create_person(map_entities, map_topology, self.location):
                    self.person_list.append(temp_person)
                self.time_last_birth = globe.time.now()

        # update entities
        for building in self.building_list:
            building.update(map_topology, map_item)
        for person in self.person_list:
            person.update(map_resource, map_entities, map_topology, map_item, map_traffic)

    def create_wizard(self, map_entities, map_topology, location_tower):
        """Create wizard at the edge of the tower. Returns new wizard object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)
        if possible_locations:
            location = random.choice(possible_locations)

            return wizards.Wizard(self, location)

    def create_building(self, kind, map_entities, map_topology, map_traffic, location_tower):
        """Create building site of a given kind at an appropriate location. Returns new building
        object."""

        # construct tower
        if kind == "b_tower":
            return buildings.building_info[kind]["obj"](self, location_tower)

        # construct buildings within radius of tower
        # TODO Ensure building access (maybe astar check each building with tower)
        else:
            build_radius = 4 + round(len(self.building_list) * 0.25)
            possible_locations = pathfinding.find_within_radius(location_tower, build_radius)
            possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)

            if possible_locations:

                # place buildings in low traffic areas
                possible_locations_chance = []
                for i in possible_locations:
                    possible_locations_chance.append(2 / (map_traffic[i[1]][i[0]]+1))
                location = random.choices(possible_locations, weights=possible_locations_chance, k=1)[0]

                # construct building
                audio.audio.play_relative_sound("n_construction", location)
                return buildings.building_info[kind]["obj"](self, location)

        return None

    def create_person(self, map_entities, map_topology, location_tower):
        """Create person at the edge of the tower. Returns new person object."""

        possible_locations = pathfinding.find_edges(location_tower)
        possible_locations = pathfinding.find_free(possible_locations, map_entities, map_topology)
        if possible_locations:
            location = random.choice(possible_locations)
            audio.audio.play_relative_sound("n_birth", location)
            return persons.Person(self, location)

        return None

    def assign(self, person_list, building_list):
        """Assign an idle person to a random action, based on action dictionary weights and available tasks."""
        
        #TODO Replace with diplomacy system
        target_state = self.other_states[0]

        # Prepare lists of possible actions
        possible_actions = [None, "a_harvest_food", "a_harvest_wood", "a_harvest_metal"]
        idle_person_list = [i for i in person_list if not i.action_super]

        if construction_list := [i for i in building_list if i.under_construction and not i.stock_list_needed]:
            possible_actions.append("a_construct")

        if work_list := [i for i in building_list if not i.under_construction and i.under_work]:
            possible_actions.append("a_work")

        if attack_list := ([i.location for i in target_state.person_list]):
            possible_actions.append("a_attack")

        # Create list of tuples where 0 - entity to haul to, 1 - entity to haul from, 2 - item to haul
        haul_links = []

        # Find buildings in need of items
        for building_to in [i for i in building_list if i.stock_list_needed]:
            for item in building_to.stock_list_needed:

                # Find buildings with needed items
                for building_from in [i for i in building_list if i.stock_list]:
                    # TODO Improve logic to account for multiple of the same item
                    if item in building_from.stock_list:
                        haul_links.append((building_to, building_from, item))
        if haul_links:
            possible_actions.append("a_haul")

        # TODO Intelligently decide which building to construct next ect somewhere. Currently assign_build ect attempts to build everything until no idle workers / unbuilt buildings remain
        if idle_person_list:
            chosen_action = random.choices([i for i in possible_actions], weights=[self.action_dict[i]["weight"] for i in possible_actions])[0]
            if chosen_action == "a_haul":
                self.assign_haul(person_list, idle_person_list, haul_links)
            elif chosen_action == "a_construct":
                self.assign_build(person_list, idle_person_list, construction_list)
            elif chosen_action == "a_work":
                self.assign_work(person_list, idle_person_list, work_list)
            elif chosen_action == "a_attack":
                self.assign_attack(idle_person_list, target_state)

            # TODO Give assigning harvest its own function to match assign work, chose target resource within and set as action_target, then use generic harvest function
            elif chosen_action in ["a_harvest_food", "a_harvest_wood", "a_harvest_metal"]:
                idle_person_list[0].action_super = chosen_action

                # PLACEHOLDER CODE UNTIL ABOVE IS IMPLEMENTED
                if chosen_action == "a_harvest_food":
                    idle_person_list[0].action_set("a_harvest_food", "i_food")
                if chosen_action == "a_harvest_wood":
                    idle_person_list[0].action_set("a_harvest_wood", "i_wood")
                if chosen_action == "a_harvest_metal":
                    idle_person_list[0].action_set("a_harvest_metal", "i_metal")

    def assign_haul(self, person_list, idle_person_list, haul_links):

        for haul_link in haul_links:

            # check if entity already has haul assigned
            haul_assigned = [i for i in person_list if i.action_target == haul_link[0]]
            if not haul_assigned:

                # Find the closest idle person with inventory space and assign to haul
                if possible_person_list := [i for i in idle_person_list if len(i.stock_list) < i.stock_list_limit]:
                    person_location = pathfinding.find_closest(haul_link[1].location, [i.location for i in possible_person_list])
                    person = [i for i in possible_person_list if i.location == person_location].pop()
                    # TODO Add support for hauling multiple items
                    person.action_set("a_haul", haul_link)


    def assign_work(self, person_list, idle_person_list, work_list):
        """Assign the closest person in the provided idle person list and assign them to construct
        given building."""

        for building in work_list:

            # TODO Remove useless variables work_assigned ect when able to test again
            # check if building already has construction assigned
            work_assigned = [i for i in person_list if i.action_target == building]
            if not work_assigned:

                # check for and assign appropriate person to construction
                if idle_person_list:
                    person_location = pathfinding.find_closest(building.location, [i.location for i in idle_person_list])
                    person = [i for i in idle_person_list if i.location == person_location].pop()
                    person.action_set("a_work", building)

    def assign_build(self, person_list, idle_person_list, construction_list):
        """Assign the closest person in the provided idle person list and assign them to construct
        given building."""

        for building in construction_list:

            # check if building already has construction assigned
            construction_assigned = [i for i in person_list if i.action_target == building]
            if not construction_assigned:

                # check for and assign appropriate person to construction
                if idle_person_list:
                    person_location = pathfinding.find_closest(building.location, [i.location for i in idle_person_list])
                    person = [i for i in idle_person_list if i.location == person_location].pop()
                    person.action_set("a_construct", building)

    def assign_attack(self, idle_person_list, target_state):

        # check for and assign appropriate person to construction
        if idle_person_list and target_state.person_list:
            target_location = pathfinding.find_closest(self.location, [i.location for i in target_state.person_list])
            person_location = pathfinding.find_closest(target_location, [i.location for i in idle_person_list])
            person = [i for i in idle_person_list if i.location == person_location].pop()
            person.action_set("a_attack", [i for i in target_state.person_list if i.location == target_location].pop())

    def tune_action_wight(self):
        """Restrict action weight to between 0 and 100, slowly move value towards 50."""

        #TODO Do not call every step, should have global update every half second or so for this type of thing
        for action in self.action_dict.keys():
            self.action_dict[action]["weight"] = max(min(100, self.action_dict[action]["weight"]), 0)
            self.action_dict[action]["weight"] += (self.action_dict[action]["weight"] - 50) * -0.01
