import pygame as pg

import globe
import spells


class Player:  # TODO Should this object even exist? Probably not

    def __init__(self, player_wizard):

        self.interface = Interface()
        self.camera = Camera()
        self.character = Character(player_wizard)

    def update(self, map_topology, map_resource, map_entities, events):
        
        self.interface.update(events[0], events[1])
        self.character.update(map_entities, map_topology, events[0], events[1])
        self.camera.update(self.character, map_topology, map_resource, map_entities, events[0], events[1])


class Interface:

    def __init__(self):

        self.panel_current = 1

    def update(self, key_press, keys):

        self.change_panel(key_press, keys)

    def change_panel(self, key_press, keys):

        if key_press:
            if keys[pg.K_1]:
                self.panel_current = 1
            elif keys[pg.K_2]:
                self.panel_current = 2
            elif keys[pg.K_3]:
                self.panel_current = 3

class Camera:
    
    def __init__(self):

        self.location = (0, 0)
        self.time_last = 0
        self.inspector_location = (0, 0)
        self.inspector_mode = "inspect"
        self.inspector_dict = {"Topology": "", "Resource": "", "Entity type": "", "Location": "", "Action": "", "Stock": "", "Health": "", "Construction remaining": ""}

    def update(self, player_character, map_topology, map_resource, map_entities, key_press, keys):

        # check for a spell requiring target selection
        if spell_list := player_character.wizard.spell_list:
            if type(spell_list[0]).__name__ in ['SpellHeal']:
                self.inspector_mode = "select"

        self.location, self.inspector_location = self.move_camera(player_character, keys)

        if self.inspector_mode == "inspect":
            if key_press and keys[pg.K_RETURN]:
                self.inspect(map_topology, map_resource, map_entities, keys)

        elif self.inspector_mode == "select":
            player_character.wizard.spell_list[0].location_select = self.inspector_location
            if key_press and keys[pg.K_RETURN]:
                player_character.wizard.spell_list[0].select(map_entities)
                self.inspector_mode = "inspect"

    def move_camera(self, player_character, keys):
        """Check for keyboard input and set new camera tile location if move detected."""

        camera_location = self.location

        # move the camera to follow the player_character
        if player_character.camera_follow:
            camera_location = (player_character.wizard.location[0] - 20, player_character.wizard.location[1] - 20)

        # prevent camera movement immediately after casting
        if spell_list := player_character.wizard.spell_list:
            if spell_list[0].status == "hold":
                self.time_last = globe.time.now() + 300

        # move the camera independently of the player_character
        if 1 in (keys[pg.K_UP], keys[pg.K_LEFT], keys[pg.K_DOWN], keys[pg.K_RIGHT]):
            if not keys[pg.K_SPACE]:
                if globe.time.check(self.time_last, globe.TIME_CAMERA):
                    move_x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
                    move_y = keys[pg.K_DOWN] - keys[pg.K_UP]
                    camera_location = (self.location[0]+move_x, self.location[1]+move_y)
                    player_character.camera_follow = False
                    self.time_last = globe.time.now()

        inspector_location = (camera_location[0]+20, camera_location[1]+20)  # TODO This will brake if world scale changes.

        return camera_location, inspector_location

    def inspect(self, map_topology, map_resource, map_entities, keys):
        """Set new inspector tile location based on camera location. Check for keyboard input and 
        activate inspector if request detected."""

        self.inspector_dict = dict.fromkeys(self.inspector_dict, "")
        self.inspector_dict["Topology"] = str(map_topology[self.inspector_location[1]][self.inspector_location[0]])
        self.inspector_dict["Resource"] = str(map_resource[self.inspector_location[1]][self.inspector_location[0]])

        inspect_object = map_entities[self.inspector_location[1]][self.inspector_location[0]]

        if inspect_object:
            self.inspector_dict["Entity type"] = str(type(inspect_object).__name__)
            self.inspector_dict["Location"] = str(inspect_object.location)
            self.inspector_dict.update(inspect_object.stat_dict)

            if type(inspect_object).__name__ == 'Person':
                self.inspector_dict["Action"] = str(inspect_object.action_super)
                self.inspector_dict["Stock"] = str(inspect_object.stock_list)

            if type(inspect_object).__name__ in ['Tower', 'House', 'Shrine']:
                self.inspector_dict["Construction remaining"] = str(inspect_object.under_construction)


class Character:

    def __init__(self, wizard):

        self.wizard = wizard

        self.camera_follow = True
        self.casting_string = []

    def update(self, map_entities, map_topology, key_press, keys):

        move_character_attempt = self.move_character(keys)
        move_spell_attempt = None
        cast_attempt = None

        # move spell if holding otherwise cast new spell
        if [i for i in self.wizard.spell_list if i.status == "hold"]:
            move_spell_attempt = self.move_spell(key_press, keys)
        else:
            cast_attempt = self.select_spell(key_press, keys)

        self.wizard.update(map_entities, map_topology, cast_attempt, move_character_attempt, move_spell_attempt)

    def move_character(self, keys):
        """Detect keyboard input and return appropriate direction tuple for wizard move."""

        if pg.key.get_pressed()[pg.K_f]:
            self.camera_follow = True

        if 1 in (keys[pg.K_w], keys[pg.K_a], keys[pg.K_s], keys[pg.K_d]):
            move_x = keys[pg.K_d] - keys[pg.K_a]
            move_y = keys[pg.K_s] - keys[pg.K_w]

            return move_x, move_y
        return None

    def move_spell(self, key_press, keys):
        """Detect keyboard input and return appropriate direction tuple for spell cast."""

        if key_press:
            if 1 in (keys[pg.K_UP], keys[pg.K_LEFT], keys[pg.K_DOWN], keys[pg.K_RIGHT]):
                move_x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
                move_y = keys[pg.K_DOWN] - keys[pg.K_UP]
                return move_x, move_y

            elif keys[pg.K_RETURN]:
                return "cast"

        return None

    def select_spell(self, key_press, keys):
        """Detect keyboard input and build casting string when space is held. Return selected spell if a match to the
        casting string is found, otherwise return None."""

        # create casting string while holding space
        if keys[pg.K_SPACE]:
            if key_press:
                if keys[pg.K_UP]:
                    self.casting_string.append("up")
                elif keys[pg.K_LEFT]:
                    self.casting_string.append("left")
                elif keys[pg.K_DOWN]:
                    self.casting_string.append("down")
                elif keys[pg.K_RIGHT]:
                    self.casting_string.append("right")

        # attempt to select spell when space is released
        else:
            if self.casting_string:
                for key, value in self.wizard.spell_dict.items():
                    if self.casting_string == value[2] and value[3]:

                        self.casting_string = []
                        return key

            self.casting_string = []
        return None

