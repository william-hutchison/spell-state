import pygame as pg
import os

import globe
import tools

pg.init()

os.chdir(os.path.dirname(__file__))

image_inspector = pg.image.load('sprites/inspector.png')
image_selector = pg.image.load('sprites/selector.png')
image_food = pg.image.load('sprites/resource_food.png')
image_wood = pg.image.load('sprites/resource_wood.png')
image_metal = pg.image.load('sprites/resource_metal.png')
image_spell_hold = pg.image.load('sprites/spell_hold.png')

anim_water = [pg.image.load('sprites/water_0.png'), pg.image.load('sprites/water_1.png'), pg.image.load('sprites/water_2.png')]

colour_topology = [(40, 40, 40), (60, 60, 60), (80, 80, 80), (100, 100, 100)]
window_size = [(1200, 800), (2400, 1600)]

font_0 = pg.font.SysFont("timesnewroman", 24)


class Graphics:

    def __init__(self):

        self.window = pg.display.set_mode((1200, 800))
        self.surface_final = pg.Surface((1200, 800))
        self.surface_terrain = pg.Surface((800, 800))
        self.surface_ui_panel = pg.Surface((400, 800))
        self.surface_ui_wizard = pg.Surface((300, 200))
        self.surface_ui_spellbook = pg.Surface((300, 200))
        self.scale = 0

        pg.display.set_caption('Spell State')

    def update_window(self):

        self.surface_final.blit(self.surface_terrain, (0, 0))
        self.surface_final.blit(self.surface_ui_panel, (800, 0))
        self.surface_final.blit(self.surface_ui_wizard, (0, 400))
        self.surface_final.blit(self.surface_ui_spellbook, (0, 600))
        self.window.blit(pg.transform.scale(self.surface_final, window_size[self.scale]), (0, 0))

    def update_world(self, camera_location, topology, resources, entities):

        self.surface_terrain.fill((0, 0, 0))

        # TODO Limit loop to screen
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):

                # draw tiles
                pg.draw.rect(self.surface_terrain, (20, 8*topology[y][x], 20), ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE, globe.TILE_SIZE, globe.TILE_SIZE), 0)
                if topology[y][x] == 0:
                    self.surface_terrain.blit(anim_water[globe.time.frame()], ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE))

                # draw resources
                if resources[y][x] == "i_food":
                    self.surface_terrain.blit(image_food, ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE))
                elif resources[y][x] == "i_wood":
                    self.surface_terrain.blit(image_wood, ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE))
                elif resources[y][x] == "i_metal":
                    self.surface_terrain.blit(image_metal, ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE))

                # draw entities
                if entities[y][x]:
                    self.surface_terrain.blit(tools.colour_image(entities[y][x].sprite, entities[y][x].ruler_state.colour), ((x-camera_location[0])*globe.TILE_SIZE, (y-camera_location[1])*globe.TILE_SIZE))

        # draw contours
        # TODO Move to within tile loop.
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):
                if x + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y][x + 1]:
                        colour_index = int(min((topology[y][x], topology[y][x + 1])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x+1-camera_location[0])*globe.TILE_SIZE-1, (y-camera_location[1])*globe.TILE_SIZE, 2, globe.TILE_SIZE), 0)
                if y + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y + 1][x]:
                        colour_index = int(min((topology[y][x], topology[y + 1][x])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x-camera_location[0])*globe.TILE_SIZE-1, (y+1-camera_location[1])*globe.TILE_SIZE-1, globe.TILE_SIZE, 2), 0)

    def update_overlay(self, camera_location, inspector_location, inspector_mode, character_location, state_list):

        for state in state_list:
            for spell in state.wizard.spell_list:
                self.surface_terrain.blit(image_spell_hold, ((spell.location[0]-camera_location[0])*globe.TILE_SIZE, (spell.location[1]-camera_location[1])*globe.TILE_SIZE))

        if inspector_mode == "inspect":
            if inspector_location != character_location:
                self.surface_terrain.blit(image_inspector, ((inspector_location[0]-camera_location[0])*globe.TILE_SIZE-1, (inspector_location[1]-camera_location[1])*globe.TILE_SIZE-1))
        elif inspector_mode == "select":
            self.surface_terrain.blit(image_selector, ((inspector_location[0]-camera_location[0])*globe.TILE_SIZE-1, (inspector_location[1]-camera_location[1])*globe.TILE_SIZE-1))

    def update_ui_panel(self, state, inspector_dict, interface):

        self.surface_ui_panel.fill((30, 30, 40))

        for i in range(3):
            text = font_0.render(str(i+1), True, (255, 255, 255))
            self.surface_ui_panel.blit(text, (10+30*i, 10))
            self.surface_ui_panel.blit(image_inspector, (10+30*(interface.panel_current-1), 10))

        if interface.panel_current == 1:
            text = font_0.render("State info", True, (255, 255, 255))
            self.surface_ui_panel.blit(text, (10, 40))
            draw_time(self.surface_ui_panel)
            draw_state_info(self.surface_ui_panel, state)
            draw_inspector_info(self.surface_ui_panel, inspector_dict)

        elif interface.panel_current == 2:
            text = font_0.render("Person info", True, (255, 255, 255))
            self.surface_ui_panel.blit(text, (10, 40))

        elif interface.panel_current == 3:
            text = font_0.render("Building info", True, (255, 255, 255))
            self.surface_ui_panel.blit(text, (10, 40))

    def update_ui_wizard(self, camera, character):

        self.surface_ui_wizard.fill((30, 30, 40))
        self.surface_ui_spellbook.fill((30, 30, 40))

        draw_player_info(self.surface_ui_wizard, camera, character)
        draw_player_spells(self.surface_ui_spellbook, character)

    def set_window_scale(self, scale):

        self.scale = scale
        self.window = pg.display.set_mode(window_size[self.scale])

    def draw_menu(self, options, current_option):

        self.window.fill((0, 0, 0))
        for i in range(len(options)):
            text = font_0.render(options[i], True, (255, 255, 255))
            self.window.blit(text, (10, 10+30*i))

        pg.draw.rect(self.window, (255, 255, 255), (100, 15+30*current_option, 10, 10), 0)


def draw_time(surface_ui_panel):

    text0 = font_0.render("World time: " + str(globe.time.now()), True, (255, 255, 255))
    surface_ui_panel.blit(text0, (10, 70))


def draw_state_info(surface_ui_panel, state):

    text0 = font_0.render("Stock list: " + str(tools.item_summary(state.stock_list)), True, (255, 255, 255))
    text1 = font_0.render("Building list: " + str([type(i).__name__ for i in state.building_list]), True, (255, 255, 255))
    text2 = font_0.render("Person list: " + str([type(i).__name__ for i in state.person_list]), True, (255, 255, 255))
    surface_ui_panel.blit(text0, (10, 100))
    surface_ui_panel.blit(text1, (10, 130))
    surface_ui_panel.blit(text2, (10, 160))

    for i, item in enumerate(state.stat_dict.items()):
        if item[1]:
            text = font_0.render(str(item[0]) + ": " + str(item[1]), True, (255, 255, 255))
            surface_ui_panel.blit(text, (10, 190 + 30 * i))


def draw_inspector_info(surface_ui_panel, inspector_dict):

    for i, item in enumerate(inspector_dict.items()):
        if item[1]:
            text = font_0.render(str(item[0]) + ": " + str(item[1]), True, (255, 255, 255))
            surface_ui_panel.blit(text, (10, 500 + 30 * i))


def draw_player_info(surface_ui_wizard, camera, character):

    text0 = font_0.render("Inspector location: " + str(camera.inspector_location), True, (255, 255, 255))
    text1 = font_0.render("Character location: " + str(character.wizard.location), True, (255, 255, 255))
    text2 = font_0.render("Casting string: " + str(character.casting_string), True, (255, 255, 255))
    text3 = font_0.render("Health: " + str(character.wizard.stat_dict['health current']) + "/" + str(character.wizard.stat_dict['health max']), True, (255, 255, 255))
    text4 = font_0.render("Mana: " + str(character.wizard.stat_dict['mana current']) + "/" + str(character.wizard.stat_dict['mana max']), True, (255, 255, 255))
    surface_ui_wizard.blit(text0, (10, 10))
    surface_ui_wizard.blit(text1, (10, 40))
    surface_ui_wizard.blit(text2, (10, 70))
    surface_ui_wizard.blit(text3, (10, 100))
    surface_ui_wizard.blit(text4, (10, 130))


def draw_player_spells(surface_ui_spellbook, character):

    i = 0
    for key, value in character.wizard.spell_dict.items():
        if value["unlocked"]:
            text = font_0.render(key + ": " + str(value["combo"]), True, (255, 255, 255))
            surface_ui_spellbook.blit(text, (10, 10+i*30))
            i += 1