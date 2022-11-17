from noise import pnoise2
import numpy as np
import random

import states
import timer


class World:
    """Class to store world information and update states each step."""
    
    def __init__(self):

        self.SEED = random.randint(0, 20)
        self.WORLD_SIZE = (60, 60)
        self.STATE_NUMBER = 3
        self.STATE_COLOURS = [(85, 220, 121), (174, 84, 220), (14, 44, 120)]

        # Variables to capture information outside the world object when saving game
        self.save_time = 0
        self.save_player = None

        # Create empty maps
        self.map_topology = np.zeros(self.WORLD_SIZE)
        self.map_resource = np.empty(self.WORLD_SIZE, dtype="<U10")
        self.map_item = np.empty(self.WORLD_SIZE, dtype="<U10")
        self.map_traffic = np.zeros(self.WORLD_SIZE)
        self.map_entities = np.empty(self.WORLD_SIZE, dtype=object)

        # Create terrain
        self.map_topology = gen_topology(self.map_topology, gen_noise(self.WORLD_SIZE, self.SEED))
        self.map_resource = gen_resource(self.map_resource, self.map_topology, gen_noise(self.WORLD_SIZE, self.SEED+1), [(1, 0.2), (2, 0.1)],  0.4, "i_food")
        self.map_resource = gen_resource(self.map_resource, self.map_topology, gen_noise(self.WORLD_SIZE, self.SEED+2), [(1, 0.2), (2, 0.4), (3, 0.2)],  0.5, "i_wood")
        self.map_resource = gen_resource(self.map_resource, self.map_topology, gen_noise(self.WORLD_SIZE, self.SEED+3), [(4, 0.4)], 0.2, "i_metal")

        # Create states
        self.state_list = []
        for i in range(self.STATE_NUMBER):
            self.state_list.append(create_state(self.map_entities, self.map_topology, self.map_traffic, self.STATE_COLOURS[i]))
        for state in self.state_list:
            for other_state in self.state_list:
                if state != other_state:
                    state.relation_dict[other_state] = 50

    def update(self):

        for state in self.state_list:
            state.update(self.map_resource, self.map_entities, self.map_topology, self.map_item, self.map_traffic)
        self.map_entities = self.update_entity_map(self.state_list)

    def update_entity_map(self, state_list):
        """Updates and returns map_entities, providing easy entity information access to other 
        parts of the program."""

        map_entities = np.empty(self.WORLD_SIZE, dtype=object)
        for state in state_list:
            for building in state.building_list:
                map_entities[building.location[1]][building.location[0]] = building
            for person in state.person_list:
                map_entities[person.location[1]][person.location[0]] = person
            map_entities[state.wizard.location[1]][state.wizard.location[0]] = state.wizard

        return map_entities


def gen_topology(map_topology, map_noise):
    """Generates and returns topology map of 5 levels based on map_noise."""

    for y in range(len(map_topology[0])):
        for x in range(len(map_topology[1])):
            if map_noise[y][x] > 0.8:
                map_topology[y][x] = 4
            elif map_noise[y][x] > 0.6:
                map_topology[y][x] = 3
            elif map_noise[y][x] > 0.4:
                map_topology[y][x] = 2
            elif map_noise[y][x] > 0.2:
                map_topology[y][x] = 1
            else:
                map_topology[y][x] = 0

    return map_topology


def gen_resource(map_resource, map_topology, map_noise, topology_target, chance, resource):
    """Generates and returns map of input resource based on map_noise. The chance of resource 
    occuring at a given tile is modified by the topology_target, map_topology and chance."""

    for y in range(len(map_resource[1])):
        for x in range(len(map_resource[0])):
            for topology in topology_target:
                if topology[0] == map_topology[y][x]:
                    if topology[1] > map_noise[y][x]:
                        if random.randint(0, random.randint(0, chance * 10)):
                            map_resource[y][x] = resource

    return map_resource


def create_state(map_entities, map_topology, map_traffic, colour):
    """Returns state object of input colour at a suitable location."""

    possible_locations = []
    for y in range(len(map_topology[0])):
        for x in range(len(map_topology[1])):
            if map_topology[y][x] in [1, 2, 3]:
                possible_locations.append((x, y))

    return states.State(random.choice(possible_locations), map_entities, map_topology, map_traffic, colour)


def gen_noise(map_size, seed, scale=20, octaves=6, persistence=0.5, lacunarity=2.0):
    """Returns a numpy array of perlin noise scaled between 0 and 1."""

    map_new = np.zeros(map_size)
    for y in range(len(map_new[0])):
        for x in range(len(map_new[1])):
            map_new[y][x] = pnoise2(y / scale, x / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=1024, repeaty=1024, base=seed)
    max_arr = np.max(map_new)
    min_arr = np.min(map_new)
    norm_me = lambda x: (x - min_arr) / (max_arr - min_arr)
    norm_me = np.vectorize(norm_me)
    map_new = norm_me(map_new)
    
    return map_new

