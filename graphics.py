import pygame as pg
import os

import glob
import tools


os.chdir(os.path.dirname(__file__))

image_wizard = pg.image.load('sprites/wizard.png')
image_person = pg.image.load('sprites/person.png')
image_inspector = pg.image.load('sprites/inspector.png')
image_food = pg.image.load('sprites/resource_food.png')
image_wood = pg.image.load('sprites/resource_wood.png')
image_metal = pg.image.load('sprites/resource_metal.png')
image_spell_hold = pg.image.load('sprites/spell_hold.png')

colour_topology = [(40, 40, 40), (60, 60, 60), (80, 80, 80), (100, 100, 100)]
colour_states = [(255, 50, 50), (50, 50, 255)]
window_size = [(1200, 800), (2400, 1600)]

class Graphics:

    def __init__(self):

        self.window = pg.display.set_mode((1200, 800))
        self.surface_final = pg.Surface((1200, 800))
        self.surface_terrain = pg.Surface((800, 800))
        self.surface_ui_panel = pg.Surface((400, 800))
        self.surface_ui_spellbook = pg.Surface((300, 200))
        self.scale = 0

        self.font = pg.font.SysFont("timesnewroman", 24)

        pg.display.set_caption('NewSpellState')

    def update_window(self):

        self.surface_final.blit(self.surface_terrain, (0, 0))
        self.surface_final.blit(self.surface_ui_panel, (800, 0))
        self.surface_final.blit(self.surface_ui_spellbook, (20, 580))
        self.window.blit(pg.transform.scale(self.surface_final, window_size[self.scale]), (0, 0))

    def update_terrain(self, camera_location, inspector_location, character_location, topology, resources, state_list):

        self.surface_terrain.fill((0, 0, 0))
        self.draw_terrain(camera_location, topology, resources)
        self.draw_entities(camera_location, state_list)
        self.draw_overlay(camera_location, inspector_location, character_location, state_list)

    def update_ui_panel(self, state, camera, character, inspector_dict):

        self.surface_ui_panel.fill((30, 40, 40))
        self.draw_time()
        self.draw_state_info(state)
        self.draw_player_info(camera, character)
        self.draw_inspector_info(inspector_dict)

    def update_ui_wizard(self, spell_combo_dict):

        self.surface_ui_spellbook.fill((30, 40, 40))
        i = 0
        for key, value in spell_combo_dict.items():
            text = self.font.render(key + ": " + str(value), True, (255, 255, 255))
            self.surface_ui_spellbook.blit(text, (10, 10+i*30))
            i += 1

    def set_window_scale(self, scale):

        self.scale = scale
        self.window = pg.display.set_mode(window_size[self.scale])

    def draw_terrain(self, camera_location, topology, resources):
        
        # draw tiles
        for y in range(glob.WORLD_SIZE[1]):
            for x in range(glob.WORLD_SIZE[0]):
                pg.draw.rect(self.surface_terrain, (0, 12*topology[y][x], 0), ((x-camera_location[0])*glob.TILE_SIZE, (y-camera_location[1])*glob.TILE_SIZE, glob.TILE_SIZE, glob.TILE_SIZE), 0)

                if resources[y][x] == glob.FOOD:
                    self.surface_terrain.blit(image_food, ((x-camera_location[0])*glob.TILE_SIZE, (y-camera_location[1])*glob.TILE_SIZE))
                elif resources[y][x] == glob.WOOD:
                    self.surface_terrain.blit(image_wood, ((x-camera_location[0])*glob.TILE_SIZE, (y-camera_location[1])*glob.TILE_SIZE))
                elif resources[y][x] == glob.METAL:
                    self.surface_terrain.blit(image_metal, ((x-camera_location[0])*glob.TILE_SIZE, (y-camera_location[1])*glob.TILE_SIZE))

        # draw contours MOVE TO WITHIN TILE LOOP
        for y in range(glob.WORLD_SIZE[1]):
            for x in range(glob.WORLD_SIZE[0]):
                if x+1 < glob.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y][x+1]:
                        colour_index = int(min((topology[y][x], topology[y][x+1])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x+1-camera_location[0])*glob.TILE_SIZE-1, (y-camera_location[1])*glob.TILE_SIZE, 2, glob.TILE_SIZE), 0)
                if y+1 < glob.WORLD_SIZE[0]:  
                    if topology[y][x] != topology[y+1][x]:
                        colour_index = int(min((topology[y][x], topology[y+1][x])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x-camera_location[0])*glob.TILE_SIZE-1, (y+1-camera_location[1])*glob.TILE_SIZE-1, glob.TILE_SIZE, 2), 0)                    

    def draw_entities(self, camera_location, state_list):
    
        for i, state in enumerate(state_list):

            for building in state.building_list:
                if building.under_construction:
                    pg.draw.rect(self.surface_terrain, (100, 10, 100), ((building.location[0]-camera_location[0])*glob.TILE_SIZE, (building.location[1]-camera_location[1])*glob.TILE_SIZE, glob.TILE_SIZE, glob.TILE_SIZE), 0)
                else:
                    pg.draw.rect(self.surface_terrain, (255, 100, 255), ((building.location[0]-camera_location[0])*glob.TILE_SIZE, (building.location[1]-camera_location[1])*glob.TILE_SIZE, glob.TILE_SIZE, glob.TILE_SIZE), 0)
            for person in state.person_list:
                self.surface_terrain.blit(tools.colour_image(image_person, colour_states[i]), ((person.location[0]-camera_location[0])*glob.TILE_SIZE-1, (person.location[1]-camera_location[1])*glob.TILE_SIZE-1))

            self.surface_terrain.blit(tools.colour_image(image_wizard, colour_states[i]), ((state.wizard.location[0]-camera_location[0])*glob.TILE_SIZE, (state.wizard.location[1]-camera_location[1])*glob.TILE_SIZE))

    def draw_overlay(self, camera_location, inspector_location, character_location, state_list):

        for state in state_list:
            for spell in state.wizard.spell_list:
                self.surface_terrain.blit(image_spell_hold, ((spell.location[0] - camera_location[0]) * glob.TILE_SIZE, (spell.location[1] - camera_location[1]) * glob.TILE_SIZE))

        if inspector_location != character_location:
            self.surface_terrain.blit(image_inspector, ((inspector_location[0]-camera_location[0])*glob.TILE_SIZE, (inspector_location[1]-camera_location[1])*glob.TILE_SIZE))

    def draw_time(self):

        text0 = self.font.render("World time: " + str(glob.time.now()), True, (255, 255, 255))
        self.surface_ui_panel.blit(text0, (10, 10))

    def draw_state_info(self, state):

        text0 = self.font.render("Stock list: " + str(tools.item_summary(state.stock_list)), True, (255, 255, 255))
        text1 = self.font.render("Building list: " + str([type(i).__name__ for i in state.building_list]), True, (255, 255, 255))
        text2 = self.font.render("Person list: " + str([type(i).__name__ for i in state.person_list]), True, (255, 255, 255))
        self.surface_ui_panel.blit(text0, (10, 100))
        self.surface_ui_panel.blit(text1, (10, 130))
        self.surface_ui_panel.blit(text2, (10, 160))
    
    def draw_player_info(self, camera, character):

        text0 = self.font.render("Inspector location: " + str(camera.inspector_location), True, (255, 255, 255))
        text1 = self.font.render("Character location: " + str(character.wizard.location), True, (255, 255, 255))
        text2 = self.font.render("Casting string: " + str(character.casting_string), True, (255, 255, 255))
        self.surface_ui_panel.blit(text0, (10, 300))
        self.surface_ui_panel.blit(text1, (10, 330))
        self.surface_ui_panel.blit(text2, (10, 360))

    def draw_inspector_info(self, inspector_dict):

        i = 0
        for item in inspector_dict.items():
            if item[1]:
                text = self.font.render(str(item[0])+": "+str(item[1]), True, (255, 255, 255))
                self.surface_ui_panel.blit(text, (10, 500+30*i))
                i += 1

    def draw_start(self):

        self.window.fill((0, 0, 0))
        text0 = self.font.render("Select resolution. (1) 1200x800. (2) 2400x1600.", True, (255, 255, 255))
        self.window.blit(text0, (10, 10))

