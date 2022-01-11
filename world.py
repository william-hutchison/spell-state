from noise import pnoise2
import numpy as np
import random

import state
import glob


class World:
    
    def __init__(self):

        self.seed = random.randint(0,20)

        self.state_list = []
        self.map_topology = self.gen_topology(self.gen_noise(self.seed))
        self.map_resource = self.gen_wood()
        self.map_resource = self.gen_food(self.map_resource)
        self.map_resource = self.gen_metal(self.map_resource)
        self.map_entities = np.empty(glob.WORLD_SIZE, dtype=object)

        for i in range(glob.STATE_NUMBER):
            self.state_list.append(self.create_state(self.map_entities))

    def update(self):

        for state in self.state_list:
            state.update(self.map_resource, self.map_entities)

        self.map_entities = self.update_entity_map(self.state_list)

    def update_entity_map(self, state_list):

        map_entities = np.empty(glob.WORLD_SIZE, dtype=object)
        for state in state_list:
            map_entities[state.wizard.location[1]][state.wizard.location[0]] = state.wizard
            for building in state.building_list:
                map_entities[building.location[1]][building.location[0]] = building
            for person in state.person_list:
                map_entities[person.location[1]][person.location[0]] = person
                
        return map_entities

    def create_state(self, map_entities):

        location = (random.randint(0, glob.WORLD_SIZE[0]-1), random.randint(0, glob.WORLD_SIZE[1]-1))
        
        return state.State(location, map_entities)

    def gen_topology(self, map_noise):
      
        map_new = np.zeros(glob.WORLD_SIZE)
        for y in range(len(map_new[0])):
            for x in range(len(map_new[1])):
                if map_noise[y][x] > 0.8:
                    map_new[y][x] = 4
                elif map_noise[y][x] > 0.6:
                    map_new[y][x] = 3
                elif map_noise[y][x] > 0.4:
                    map_new[y][x] = 2
                elif map_noise[y][x] > 0.2:
                    map_new[y][x] = 1
                else:
                    map_new[y][x] = 0

        return map_new

    def gen_food(self, map_resource):

        for y in range(len(map_resource[1])):
            for x in range(len(map_resource[0])):
                if random.randint(0, 30) == 0:
                    map_resource[y][x] = glob.FOOD

        return map_resource

    def gen_wood(self):
     
        map_new = np.zeros(glob.WORLD_SIZE)
        for y in range(len(map_new[1])):
            for x in range(len(map_new[0])):
                if random.randint(0, 30) == 0:
                    map_new[y][x] = glob.WOOD

        return map_new

    def gen_metal(self, map_resource):

        for y in range(len(map_resource[1])):
            for x in range(len(map_resource[0])):
                if random.randint(0, 30) == 0:
                    map_resource[y][x] = glob.METAL

        return map_resource

    def gen_noise(self, seed, scale=20, octaves=6, persistence=0.5, lacunarity=2.0):
    
        map_new = np.zeros(glob.WORLD_SIZE)
        for y in range(len(map_new[0])):
            for x in range(len(map_new[1])):
                map_new[y][x] = pnoise2(y / scale, x / scale, octaves=octaves, persistence=persistence,
                                    lacunarity=lacunarity, repeatx=1024, repeaty=1024, base=seed)
        max_arr = np.max(map_new)
        min_arr = np.min(map_new)
        norm_me = lambda x: (x - min_arr) / (max_arr - min_arr)
        norm_me = np.vectorize(norm_me)
        map_new = norm_me(map_new)

        return map_new
