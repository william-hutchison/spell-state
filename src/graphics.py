import pygame as pg
import os

import globe
import tools

# TODO Move these somewhere else
os.chdir(os.path.dirname(__file__))
window_size = [(1200, 800), (2400, 1600)]


class GraphicsManager:

    def __init__(self):

        pg.display.set_caption('Spell State')
        self.window = pg.display.set_mode((1200, 800))
        self.surface = pg.Surface((1200, 800))
        self.scale = 0

        self.menu = Menu()
        self.terrain = Terrain()
        self.world_info = WorldInfo()
        self.state_info = StateInfo()
        self.player_info = PlayerInfo()
        self.spell_book = SpellBook()

        self.inspector_info = InspectorInfo()
        self.item_transfer = None

        self.image_ui = pg.image.load('../sprites/ui.png')
        #self.set_window_scale(1) # For testing

    def update_interface(self, state, character, camera, inspector_dict):

        self.surface.blit(self.image_ui, (0, 0))
        self.world_info.update(self.surface)
        self.state_info.update(self.surface, state)
        self.player_info.update(self.surface, character, camera)
        self.spell_book.update(self.surface, character)

        # TODO selectively create and destroy these objects
        self.inspector_info.update(self.surface, inspector_dict)
        if self.item_transfer:
            self.item_transfer.update(self.surface)

        self.window.blit(pg.transform.scale(self.surface, window_size[self.scale]), (0, 0))

    def update_terrain(self, camera_location, topology, resources, items, entities, inspector_location, inspector_mode, character_location, state_list):

        self.terrain.draw_terrain(self.surface, camera_location, topology, resources, items, entities)
        self.terrain.draw_overlay(self.surface, camera_location, inspector_location, inspector_mode, character_location, state_list)
        self.window.blit(pg.transform.scale(self.surface, window_size[self.scale]), (0, 0))

    def update_menu(self, options, current_option):

        self.menu.draw_menu(self.surface, options, current_option)
        self.window.blit(pg.transform.scale(self.surface, window_size[self.scale]), (0, 0))

    def set_window_scale(self, scale):

        self.scale = scale
        self.window = pg.display.set_mode(window_size[self.scale])

    def create_transfer_interface(self, options, current_option):

        self.item_transfer = ItemTransfer(self, options, current_option)
        return self.item_transfer


class Menu:

    def __init__(self):

        self.position = (0, 0)
        self.size = (1200, 800)
        self.surface = pg.Surface(self.size)
        self.font = pg.font.SysFont("timesnewroman", 24)

    def draw_menu(self, final_surface, options, current_option):

        self.surface.fill((0, 0, 0))
        for i in range(len(options)):
            text = self.font.render(options[i], True, (255, 255, 255))
            self.surface.blit(text, (10, 10 + 30 * i))

        pg.draw.rect(self.surface, (255, 255, 255), (100, 15 + 30 * current_option, 10, 10), 0)
        final_surface.blit(self.surface, self.position)


class Terrain:

    def __init__(self):

        self.position = (0, 0)
        self.size = (1200, 800)
        self.surface = pg.Surface(self.size)

        os.chdir(os.path.dirname(__file__))

        self.image_inspector = pg.image.load('../sprites/inspector.png')
        self.image_selector = pg.image.load('../sprites/selector.png')
        self.image_food = pg.image.load('../sprites/resource_food.png')
        self.image_wood = pg.image.load('../sprites/resource_wood.png')
        self.image_metal = pg.image.load('../sprites/resource_metal.png')
        self.image_spell_hold = pg.image.load('../sprites/spell_hold.png')
        self.image_item = pg.image.load('../sprites/item.png')

        self.anim_water = [pg.image.load('../sprites/water_0.png'),
                           pg.image.load('../sprites/water_1.png'),
                           pg.image.load('../sprites/water_2.png')]

        self.colour_topology = [(40, 40, 40), (60, 60, 60), (80, 80, 80), (100, 100, 100)]

    def draw_terrain(self, final_surface, camera_location, topology, resources, items, entities):

        self.surface.fill((0, 0, 0))

        # TODO Limit loop to screen
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):

                # draw tiles
                pg.draw.rect(self.surface, (20, 8 * topology[y][x], 20), ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE, globe.TILE_SIZE, globe.TILE_SIZE), 0)
                if topology[y][x] == 0:
                    self.surface.blit(self.anim_water[globe.time.frame()], ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw resources
                if resources[y][x] == "i_food":
                    self.surface.blit(self.image_food, ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))
                elif resources[y][x] == "i_wood":
                    self.surface.blit(self.image_wood, ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))
                elif resources[y][x] == "i_metal":
                    self.surface.blit(self.image_metal, ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw items
                if items[y][x]:
                    self.surface.blit(self.image_item, ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

                # draw entities
                if entities[y][x]:
                    self.surface.blit(
                        tools.colour_image(entities[y][x].sprite, entities[y][x].ruler_state.colour), ((x - camera_location[0]) * globe.TILE_SIZE, (y - camera_location[1]) * globe.TILE_SIZE))

        # TODO Move to within tile loop and eliminate glitch at contour corners
        for y in range(globe.WORLD_SIZE[1]):
            for x in range(globe.WORLD_SIZE[0]):
                if x + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y][x + 1]:
                        colour_index = int(min((topology[y][x], topology[y][x + 1])))
                        pg.draw.rect(self.surface, self.colour_topology[colour_index], ((x+1-camera_location[0]) * globe.TILE_SIZE - 1, (y - camera_location[1]) * globe.TILE_SIZE, 2, globe.TILE_SIZE), 0)
                if y + 1 < globe.WORLD_SIZE[0]:
                    if topology[y][x] != topology[y + 1][x]:
                        colour_index = int(min((topology[y][x], topology[y + 1][x])))
                        pg.draw.rect(self.surface, self.colour_topology[colour_index], ((x-camera_location[0]) * globe.TILE_SIZE - 1, (y + 1 - camera_location[1]) * globe.TILE_SIZE - 1, globe.TILE_SIZE, 2), 0)

        final_surface.blit(self.surface, self.position)

    def draw_overlay(self, final_surface, camera_location, inspector_location, inspector_mode, character_location, state_list):

        for state in state_list:
            for spell in state.wizard.spell_list:
                final_surface.blit(self.image_spell_hold, ((spell.location[0] - camera_location[0]) * globe.TILE_SIZE, (spell.location[1] - camera_location[1]) * globe.TILE_SIZE))

        if inspector_mode == "inspect":
            if inspector_location != character_location:
                final_surface.blit(self.image_inspector, ((inspector_location[0] - camera_location[0]) * globe.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * globe.TILE_SIZE - 1))
        elif inspector_mode == "select":
            final_surface.blit(self.image_selector, ((inspector_location[0] - camera_location[0]) * globe.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * globe.TILE_SIZE - 1))


class Interface:

    def __init__(self):

        self.text_spacing = 30
        self.margin_spacing = 10
        self.font = pg.font.SysFont("timesnewroman", 18)

    def draw_text_lines(self, text_list, position):

        for i, item in enumerate(text_list):
            line = self.font.render(item, True, (255, 255, 255))
            self.surface.blit(line, (position[0]+self.margin_spacing, position[1]+self.text_spacing*i))


class WorldInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (558, 0)
        self.size = (120, 20)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface):

        self.surface.fill((0, 0, 0))
        text = ["Time: " + str(globe.time.now())]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class StateInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (950, 0)
        self.size = (250, 300)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, state):

        self.surface.fill((0, 0, 0))
        text = ["Building list: " + str([type(i).__name__ for i in state.building_list]),
                "Person list: " + str([type(i).__name__ for i in state.person_list]),
                "Action dict: " + str(state.action_dict)]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class InspectorInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (950, 430)
        self.size = (300, 350)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, inspector_dict):

        self.surface.fill((0, 0, 0))
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
        self.size = (250, 300)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, character, camera):

        self.surface.fill((0, 0, 0))
        text = ["Inspector location: " + str(camera.inspector_location),
                "Character location: " + str(character.wizard.location),
                "Casting string: " + str(character.casting_string),
                "Health: " + str(character.wizard.stat_dict['health_current']) + "/" + str(character.wizard.stat_dict['health_max']),
                "Mana: " + str(character.wizard.stat_dict['mana_current']) + "/" + str(character.wizard.stat_dict['mana_max']),
                "Items: " + str(character.wizard.stock_list)]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class SpellBook(Interface):

    def __init__(self):

        super().__init__()
        self.position = (0, 600)
        self.size = (330, 300)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, character):

        self.surface.fill((0, 0, 0))
        text = []
        i = 0
        for key, value in character.wizard.spell_dict.items():
            if value["unlocked"]:
                text.append(key + ": " + str(value["combo"]))
                i += 1
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)

class ItemTransfer(Interface):

    def __init__(self, graphics_manager, options, current_option):

        super().__init__()

        self.graphics_manager = graphics_manager
        self.options = options
        self.current_option = current_option

        self.position = (950, 430)
        self.size = (300, 350)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface):

        self.surface.fill((0, 200, 0))
        self.draw_text_lines(self.options[0], (0, 0))
        self.draw_text_lines(self.options[1], (150, 0))
        pg.draw.rect(self.surface, (255, 255, 255), (self.current_option[0]*150+80, self.current_option[1]*self.text_spacing, 10, 10), 0)
        final_surface.blit(self.surface, self.position)

    def close(self):

        self.graphics_manager.item_transfer = None
