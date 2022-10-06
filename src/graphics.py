import pygame as pg
import os

import globe
import tools


os.chdir(os.path.dirname(__file__))

image_inspector = pg.image.load('../sprites/inspector.png')
image_selector = pg.image.load('../sprites/selector.png')
image_food = pg.image.load('../sprites/resource_food.png')
image_wood = pg.image.load('../sprites/resource_wood.png')
image_metal = pg.image.load('../sprites/resource_metal.png')
image_spell_hold = pg.image.load('../sprites/spell_hold.png')
image_item = pg.image.load('../sprites/item.png')

anim_water = [pg.image.load('../sprites/water_0.png'), pg.image.load('../sprites/water_1.png'), pg.image.load(
    '../sprites/water_2.png')]

colour_topology = [(40, 40, 40), (60, 60, 60), (80, 80, 80), (100, 100, 100)]
window_size = [(1200, 800), (2400, 1600)]


class Graphics:

    def __init__(self):

        self.window = pg.display.set_mode((1200, 800))
        self.scale = 0
        self.surface_final = pg.Surface((1200, 800))
        self.surface_terrain = pg.Surface((1200, 800))

        self.world_info = WorldInfo()
        self.state_info = StateInfo()
        self.inspector_info = InspectorInfo()
        self.player_info = PlayerInfo()
        self.spell_book = SpellBook()

        pg.display.set_caption('Spell State')

        self.font = pg.font.SysFont("timesnewroman", 24)

    def update_interface(self, state, character, camera, inspector_dict):

        self.surface_final.blit(self.surface_terrain, (0, 0))

        self.world_info.update(self.surface_final)
        self.state_info.update(self.surface_final, state)
        self.inspector_info.update(self.surface_final, inspector_dict)
        self.player_info.update(self.surface_final, character, camera)
        self.spell_book.update(self.surface_final, character)
        self.window.blit(pg.transform.scale(self.surface_final, window_size[self.scale]), (0, 0))

    def set_window_scale(self, scale):

        self.scale = scale
        self.window = pg.display.set_mode(window_size[self.scale])

    # TODO Replace with separate object managed by Graphics
    def update_world(self, camera_location, topology, resources, items, entities):

        self.surface_terrain.fill((0, 0, 0))

        # TODO Limit loop to screen
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):

                # draw tiles
                pg.draw.rect(self.surface_terrain, (20, 8*topology[y][x], 20), ((x-camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE, globe.TILE_SIZE, globe.TILE_SIZE), 0)
                if topology[y][x] == 0:
                    self.surface_terrain.blit(anim_water[globe.time.frame()], ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw resources
                if resources[y][x] == "i_food":
                    self.surface_terrain.blit(image_food, ((x-camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))
                elif resources[y][x] == "i_wood":
                    self.surface_terrain.blit(image_wood, ((x-camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))
                elif resources[y][x] == "i_metal":
                    self.surface_terrain.blit(image_metal, ((x-camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw items
                if items[y][x]:
                    self.surface_terrain.blit(image_item, ((x-camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw entities
                if entities[y][x]:
                    self.surface_terrain.blit(
                        tools.colour_image(entities[y][x].sprite, entities[y][x].ruler_state.colour), ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

        # draw contours
        # TODO Move to within tile loop and eliminate glitch at contour corners.
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):
                if x + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y][x + 1]:
                        colour_index = int(min((topology[y][x], topology[y][x + 1])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x+1-camera_location[0]) * globe.TILE_SIZE - 1, (y - camera_location[1]) * globe.TILE_SIZE, 2, globe.TILE_SIZE), 0)
                if y + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y + 1][x]:
                        colour_index = int(min((topology[y][x], topology[y + 1][x])))
                        pg.draw.rect(self.surface_terrain, colour_topology[colour_index], ((x-camera_location[0]) * globe.TILE_SIZE - 1, (y + 1 - camera_location[1]) * globe.TILE_SIZE - 1, globe.TILE_SIZE, 2), 0)

    def update_overlay(self, camera_location, inspector_location, inspector_mode, character_location, state_list):

        for state in state_list:
            for spell in state.wizard.spell_list:
                self.surface_terrain.blit(image_spell_hold, ((spell.location[0]-camera_location[0]) * globe.TILE_SIZE, (spell.location[1] - camera_location[1]) * globe.TILE_SIZE))

        if inspector_mode == "inspect":
            if inspector_location != character_location:
                self.surface_terrain.blit(image_inspector, ((inspector_location[0]-camera_location[0]) * globe.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * globe.TILE_SIZE - 1))
        elif inspector_mode == "select":
            self.surface_terrain.blit(image_selector, ((inspector_location[0]-camera_location[0]) * globe.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * globe.TILE_SIZE - 1))


    # TODO Replace with separate object managed by Graphics
    def draw_menu(self, options, current_option):

        self.window.fill((0, 0, 0))
        for i in range(len(options)):
            text = self.font.render(options[i], True, (255, 255, 255))
            self.window.blit(text, (10, 10 + 30 * i))

        pg.draw.rect(self.window, (255, 255, 255), (100, 15 + 30 * current_option, 10, 10), 0)


class Interface:

    def __init__(self):

        self.text_spacing = 30
        self.margin_spacing = 10
        self.font = pg.font.SysFont("timesnewroman", 24)

    def draw_text_lines(self, text_list, position):

        for i, item in enumerate(text_list):
            line = self.font.render(item, True, (255, 255, 255))
            self.surface.blit(line, (position[0]+self.margin_spacing, position[1]+self.text_spacing*i))


class WorldInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (900, 0)
        self.size = (300, 100)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface):

        self.surface.fill((30, 30, 40))
        text = ["World time: " + str(globe.time.now())]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class StateInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (900, 100)
        self.size = (300, 200)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, state):

        self.surface.fill((30, 30, 40))
        text = ["Building list: " + str([type(i).__name__ for i in state.building_list]),
                "Person list: " + str([type(i).__name__ for i in state.person_list]),
                "Action dict: " + str(state.action_dict)]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class InspectorInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (900, 500)
        self.size = (300, 400)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, inspector_dict):

        self.surface.fill((30, 30, 40))
        text = []
        for i, item in enumerate(inspector_dict.items()):
            if item[1]:
                text.append(str(item[0]) + ": " + str(item[1]))
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class PlayerInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (0, 0)
        self.size = (400, 200)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, character, camera):

        self.surface.fill((30, 30, 40))
        text = ["Inspector location: " + str(camera.inspector_location),
                "Character location: " + str(character.wizard.location),
                "Casting string: " + str(character.casting_string),
                "Health: " + str(character.wizard.stat_dict['u_health_current']) + "/" + str(character.wizard.stat_dict['u_health_max']),
                "Mana: " + str(character.wizard.stat_dict['u_mana_current']) + "/" + str(character.wizard.stat_dict['u_mana_max']),
                "Items: " + str(character.wizard.stock_list)]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class SpellBook(Interface):

    def __init__(self):

        super().__init__()
        self.position = (0, 500)
        self.size = (400, 300)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, character):

        self.surface.fill((30, 30, 40))
        text = []
        i = 0
        for key, value in character.wizard.spell_dict.items():
            if value["unlocked"]:
                text.append(key + ": " + str(value["combo"]))
                i += 1
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)
