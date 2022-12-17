import pygame as pg

import timer
import tools


class GraphicsManager:
    """Class to control the display and manage the terrain and interface objects."""

    def __init__(self):

        pg.display.set_caption('Spell State')

        self.WINDOW_SIZES = [(1200, 800), (2400, 1600)]
        self.scale = 0
        self.window = pg.display.set_mode(self.WINDOW_SIZES[self.scale])
        self.surface = pg.Surface(self.WINDOW_SIZES[0])

        self.start_menu = StartMenu()
        self.menu = Menu()

        self.terrain = Terrain()
        self.world_info = WorldInfo()
        self.state_info = StateInfo()
        self.player_info = PlayerInfo()
        self.spell_book = SpellBook()

        self.inspector_info = InspectorInfo()
        self.item_transfer = ItemTransfer()

        self.image_ui = pg.image.load('../sprites/interface/ui.png')
        # self.set_window_scale(1) # For testing

    def update_interface(self, state, character, camera, inspector_dict, transfer_object, map_item):
        """Update interface objects and draw to the window."""

        self.surface.blit(self.image_ui, (0, 0))
        self.world_info.update(self.surface)
        self.state_info.update(self.surface, state)
        self.player_info.update(self.surface, character, camera)
        self.spell_book.update(self.surface, character)

        # TODO Selectively create and destroy these objects
        self.inspector_info.update(self.surface, inspector_dict)
        self.item_transfer.update(self.surface, character, transfer_object, map_item)

        # TODO Prevent window being drawn twice
        self.window.blit(pg.transform.scale(self.surface, self.WINDOW_SIZES[self.scale]), (0, 0))

    def update_terrain(self, camera_location, topology, resources, items, entities, inspector_location, inspector_mode, character_location, state_list):
        """Update terrain objects and draw to the window."""

        self.terrain.draw_terrain(self.surface, camera_location, topology, resources, items, entities)
        self.terrain.draw_overlay(self.surface, camera_location, inspector_location, inspector_mode, character_location, state_list)
        self.window.blit(pg.transform.scale(self.surface, self.WINDOW_SIZES[self.scale]), (0, 0))

    def update_menu(self, current_menu, options, current_option):
        """Update the menu object and draw to the window."""

        if type(current_menu).__name__ == "Start":
            self.start_menu.draw_menu(self.surface, options, current_option)
        else:
            self.menu.draw_menu(self.surface, options, current_option)

        self.window.blit(pg.transform.scale(self.surface, self.WINDOW_SIZES[self.scale]), (0, 0))

    def set_window_scale(self, scale):
        """Control window scaling."""

        self.scale = scale
        self.window = pg.display.set_mode(self.WINDOW_SIZES[self.scale])


class StartMenu:
    """Class to draw a whole screen menu to a surface."""

    def __init__(self):

        self.position = (0, 0)
        self.size = (1200, 800)
        self.surface = pg.Surface(self.size)
        self.background = pg.image.load('../sprites/menus/start_background_v3.png')
        self.select = pg.image.load('../sprites/menus/start_select.png')
        self.anim_select = [pg.image.load('../sprites/menus/start_select_0.png'),
                            pg.image.load('../sprites/menus/start_select_1.png'),
                            pg.image.load('../sprites/menus/start_select_2.png'),
                            pg.image.load('../sprites/menus/start_select_3.png')]


    def draw_menu(self, final_surface, options, current_option):

        self.surface.blit(self.background, self.position)
        self.surface.blit(self.anim_select[timer.timer.frame()], (450, 440 + 80 * current_option))

        final_surface.blit(self.surface, self.position)


class Menu:
    """Class to draw a whole screen menu to a surface."""

    def __init__(self):

        self.position = (0, 0)
        self.size = (1200, 800)
        self.surface = pg.Surface(self.size)
        self.font = pg.font.Font("../fonts/linden_hill.otf", 24)
        self.image_inspector = pg.image.load('../sprites/interface/inspector.png')


    def draw_menu(self, final_surface, options, current_option):
        """Draw menu comprised of options and current_option indicator onto the input final_surface."""

        self.surface.fill((0, 0, 0))
        for i in range(len(options)):
            text = self.font.render(options[i], True, (255, 255, 255))
            self.surface.blit(text, (10, 10 + 30 * i))

        pg.draw.rect(self.surface, (255, 255, 255), (100, 15 + 30 * current_option, 10, 10), 0)
        final_surface.blit(self.surface, self.position)


class Terrain:
    """Class to draw terrain, entities and overlays to a surface."""

    def __init__(self):

        self.TILE_SIZE = 20
        self.SURFACE_SIZE = (1200, 800)
        self.SURFACE_POSITION = (0, 0)

        self.BACKGROUND_COLOUR = (0, 0, 0)
        self.CONTOUR_COLOURS = [(39, 53, 60), (49, 53, 70), (59, 63, 80), (69, 73, 90)]

        self.surface = pg.Surface(self.SURFACE_SIZE)
        self.image_inspector = pg.image.load('../sprites/interface/inspector.png')
        self.image_selector = pg.image.load('../sprites/interface/selector.png')
        self.image_food = pg.image.load('../sprites/terrain/resource_food.png')
        self.image_wood = pg.image.load('../sprites/terrain/resource_wood.png')
        self.image_metal = pg.image.load('../sprites/terrain/resource_metal.png')
        self.image_item = pg.image.load('../sprites/misc/item.png')
        self.image_topology_0 = pg.image.load('../sprites/terrain/topology_0.png')
        self.image_topology_1 = pg.image.load('../sprites/terrain/topology_1.png')
        self.image_topology_2 = pg.image.load('../sprites/terrain/topology_2.png')
        self.image_topology_3 = pg.image.load('../sprites/terrain/topology_3.png')
        self.anim_water = [pg.image.load('../sprites/terrain/water_0.png'),
                           pg.image.load('../sprites/terrain/water_1.png'),
                           pg.image.load('../sprites/terrain/water_2.png'),
                           pg.image.load('../sprites/terrain/water_3.png')]

    def draw_terrain(self, final_surface, camera_location, topology, resources, items, entities):
        """Draw terrain tiles, items and entities onto the input final_surface."""

        self.surface.fill(self.BACKGROUND_COLOUR)

        # TODO Limit loop to tiles present on screen, remove reliance on temp_world_size
        temp_world_size = (60, 60)
        for y in range(temp_world_size[1]):
            for x in range(temp_world_size[0]):

                # Draw tiles
                if topology[y][x] == 0:
                    self.surface.blit(self.anim_water[timer.timer.frame()], ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif topology[y][x] == 1:
                    self.surface.blit(self.image_topology_0, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif topology[y][x] == 2:
                    self.surface.blit(self.image_topology_1, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif topology[y][x] == 3:
                    self.surface.blit(self.image_topology_2, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif topology[y][x] == 4:
                    self.surface.blit(self.image_topology_3, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))

                # Draw resources
                if resources[y][x] == "i_food":
                    self.surface.blit(self.image_food, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif resources[y][x] == "i_wood":
                    self.surface.blit(self.image_wood, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))
                elif resources[y][x] == "i_metal":
                    self.surface.blit(self.image_metal, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))

                # Draw items
                if items[y][x]:
                    self.surface.blit(self.image_item, ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))

                # Draw entities
                if entities[y][x]:
                    self.surface.blit(
                        tools.colour_image(entities[y][x].sprite, entities[y][x].ruler_state.colour), ((x - camera_location[0]) * self.TILE_SIZE, (y - camera_location[1]) * self.TILE_SIZE))

        # TODO Move to within tile loop and eliminate glitch at contour corners
        for y in range(temp_world_size[1]):
            for x in range(temp_world_size[0]):
                if x + 1 < temp_world_size[0]:
                    if topology[y][x] != topology[y][x + 1]:
                        colour_index = int(min((topology[y][x], topology[y][x + 1])))
                        pg.draw.rect(self.surface, self.CONTOUR_COLOURS[colour_index], ((x+1-camera_location[0]) * self.TILE_SIZE - 1, (y - camera_location[1]) * self.TILE_SIZE, 2, self.TILE_SIZE), 0)
                if y + 1 < temp_world_size[0]:
                    if topology[y][x] != topology[y + 1][x]:
                        colour_index = int(min((topology[y][x], topology[y + 1][x])))
                        pg.draw.rect(self.surface, self.CONTOUR_COLOURS[colour_index], ((x-camera_location[0]) * self.TILE_SIZE - 1, (y + 1 - camera_location[1]) * self.TILE_SIZE - 1, self.TILE_SIZE, 2), 0)

        final_surface.blit(self.surface, self.SURFACE_POSITION)

    def draw_overlay(self, final_surface, camera_location, inspector_location, inspector_mode, character_location, state_list):
        """Draw spells and the inspector or selector onto the input final_surface."""

        # Draw spells
        for state in state_list:
            for spell in state.wizard.spell_list:
                final_surface.blit(spell.sprite, ((spell.location[0] - camera_location[0]) * self.TILE_SIZE, (spell.location[1] - camera_location[1]) * self.TILE_SIZE))

        # Draw inspector or selector if necessary
        if inspector_mode == "inspect":
            if inspector_location != character_location:
                final_surface.blit(self.image_inspector, ((inspector_location[0] - camera_location[0]) * self.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * self.TILE_SIZE - 1))
        elif inspector_mode == "select":
            final_surface.blit(self.image_selector, ((inspector_location[0] - camera_location[0]) * self.TILE_SIZE - 1, (inspector_location[1] - camera_location[1]) * self.TILE_SIZE - 1))


class Interface:
    """Parent class for the various on-screen interface objects."""

    def __init__(self):

        self.BACKGROUND_COLOUR = (4, 9, 29)
        self.TEXT_COLOUR = (206, 205, 233)
        self.TEXT_SPACING = 24
        self.MARGIN_SPACING = 10

        self.font = pg.font.Font("../fonts/linden_hill.otf", 16)

    def draw_text_lines(self, text_list, position):
        """Draw text_list of strings at position as lines of text."""

        for i, item in enumerate(text_list):
            line = self.font.render(str(item), True, self.TEXT_COLOUR)
            self.surface.blit(line, (position[0]+self.MARGIN_SPACING, position[1]+self.TEXT_SPACING*i))


class WorldInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (558, 0)
        self.size = (120, 20)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface):

        self.surface.fill(self.BACKGROUND_COLOUR)
        text = ["Time: " + str(timer.timer.now())]
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class StateInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (950, 0)
        self.size = (250, 325)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, state):

        # TODO Also show other states' opinion of the player, or maybe merge these counts into one? 

        # Prepare lists of text
        action_text = list(zip(list(state.action_dict.keys()), [round(state.action_dict[i]["weight"], 1) for i in list(state.action_dict)]))
        relation_text = list(zip(list(state.relation_dict.keys()), list(state.relation_dict.values())))
        building_text = ["BUILDINGS: " + str([type(i).__name__ for i in state.building_list])]
        person_text = ["PEOPLE: " + str([type(i).__name__ for i in state.person_list])]

        # Draw to the surface
        self.surface.fill(self.BACKGROUND_COLOUR)
        self.draw_text_lines(["ACTION WEIGHTS..."], (0, 0))
        self.draw_text_lines(action_text, (0, 24))
        self.draw_text_lines(["RELATION WEIGHTS..."], (0, 216))
        self.draw_text_lines(relation_text, (0, 240))
        self.draw_text_lines(building_text, (0, 288))
        self.draw_text_lines(person_text, (0, 312))
        final_surface.blit(self.surface, self.position)


class InspectorInfo(Interface):

    def __init__(self):

        super().__init__()
        self.position = (950, 430)
        self.size = (300, 350)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, inspector_dict):

        self.surface.fill(self.BACKGROUND_COLOUR)
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

        self.surface.fill(self.BACKGROUND_COLOUR)
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

        self.surface.fill(self.BACKGROUND_COLOUR)
        text = []
        i = 0
        for key, value in character.wizard.spell_dict.items():
            if value["unlocked"]:
                text.append(key + ": " + str(value["combo"]))
                i += 1
        self.draw_text_lines(text, (0, 0))
        final_surface.blit(self.surface, self.position)


class ItemTransfer(Interface):

    def __init__(self):

        super().__init__()
        self.position = (950, 430)
        self.size = (300, 350)
        self.surface = pg.Surface(self.size)

    def update(self, final_surface, character, transfer_object, map_item):

        if transfer_object.transfer_target:

            # Determine item transfer headings
            player_text = self.font.render("Player ({}/{})".format(len(character.wizard.stock_list), character.wizard.stat_dict["stock_max"]), True, (255, 255, 255))
            if type(transfer_object.transfer_target) == tuple:
                if map_item[transfer_object.transfer_target[1]][transfer_object.transfer_target[0]]:
                    target_text = self.font.render("Tile (1/1)", True, (255, 255, 255))
                else:
                    target_text = self.font.render("Tile (0/1)", True, (255, 255, 255))
            else:
                target_text = self.font.render("{} ({}/{})".format(type(transfer_object.transfer_target).__name__, len(transfer_object.transfer_target.stock_list), transfer_object.transfer_target.stat_dict["stock_max"]), True, (255, 255, 255))

            # Draw item transfer information
            self.surface.fill(self.BACKGROUND_COLOUR)
            self.surface.blit(player_text, (0, 0))
            self.surface.blit(target_text, (150, 0))
            self.draw_text_lines(transfer_object.options[0], (0, self.TEXT_SPACING))
            self.draw_text_lines(transfer_object.options[1], (150, self.TEXT_SPACING))
            pg.draw.rect(self.surface, (255, 255, 255), (transfer_object.current_option[0]*150+80, transfer_object.current_option[1]*self.TEXT_SPACING+self.TEXT_SPACING, 10, 10), 0)
            final_surface.blit(self.surface, self.position)
