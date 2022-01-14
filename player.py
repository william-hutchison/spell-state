import pygame as pg
import sys

import glob

spell_dict = {"consume": ["down", "down"], "fireball": ["up", "left"]}


class Player:

    def __init__(self, player_wizard):

        self.camera = Camera()
        self.character = Character(player_wizard)

    def update(self, map_topology, map_resource, map_entities):
        
        key_press, keys = self.event_loop()
        self.character.update(map_entities, key_press, keys)
        self.camera.update(self.character, map_topology, map_resource, map_entities, keys)

    def event_loop(self):

        key_press = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                key_press = True

        return key_press, pg.key.get_pressed()


class Camera:
    
    def __init__(self):

        self.location = (0, 0)
        self.time_last = 0
        self.inspector_location = (0, 0)
        self.inspector_dict = {"Topology": "", "Resource": "", "Entity type": "", "Location": "", "Action": "", "Stock": "",
                               "Health": "", "Construction remaining": ""}

    def update(self, player_character, map_topology, map_resource, map_entities, keys):

        self.move_camera(player_character, keys)
        self.move_inspector(self.location, map_topology, map_resource, map_entities, keys)

    def move_camera(self, player_character, keys):
        """Check for keyboard input and set new camera tile location if move detected."""

        # move the camera to follow the player_character
        if player_character.camera_follow:
            self.location = (player_character.wizard.location[0] - 20, player_character.wizard.location[1] - 20)

        # prevent camera movement immediately after casting
        if spell_list := player_character.wizard.spell_list:
            if spell_list[0].status == "hold":
                self.time_last = glob.time.now() + 300

        # move the camera independently of the player_character
        if 1 in (keys[pg.K_UP], keys[pg.K_LEFT], keys[pg.K_DOWN], keys[pg.K_RIGHT]):
            if not keys[pg.K_SPACE]:
                if glob.time.check(self.time_last, glob.TIME_CAMERA):
                    move_x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
                    move_y = keys[pg.K_DOWN] - keys[pg.K_UP]
                    self.location = (self.location[0]+move_x, self.location[1]+move_y)
                    player_character.camera_follow = False
                    self.time_last = glob.time.now()

    def move_inspector(self, location_camera, map_topology, map_resource, map_entities, keys):
        """Set new inspector tile location based on camera location. Check for keyboard input and 
        activate inspector if request detected."""

        self.inspector_location = (location_camera[0]+20, location_camera[1]+20) 
        
        if keys[pg.K_RETURN]:

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

                if type(inspect_object).__name__ in ['Tower', 'House']:
                    self.inspector_dict["Construction remaining"] = str(inspect_object.under_construction)


class Character:

    def __init__(self, wizard):

        self.wizard = wizard

        self.camera_follow = True
        self.casting_string = []

    def update(self, map_entities, key_press, keys):

        move_character_attempt = self.move_character(keys)
        move_spell_attempt = None
        cast_attempt = None

        # move spell if holding otherwise cast new spell
        if [i for i in self.wizard.spell_list if i.status == "hold"]:
            move_spell_attempt = self.move_spell(keys)
        else:
            cast_attempt = self.select_spell(key_press, keys)

        self.wizard.update(map_entities, cast_attempt, move_character_attempt, move_spell_attempt)

    def move_character(self, keys):
        """Detect keyboard input and call wizard.move with appropriate direction tuple."""

        if pg.key.get_pressed()[pg.K_f]:
            self.camera_follow = True

        if 1 in (keys[pg.K_w], keys[pg.K_a], keys[pg.K_s], keys[pg.K_d]):
            move_x = keys[pg.K_d] - keys[pg.K_a]
            move_y = keys[pg.K_s] - keys[pg.K_w]

            return move_x, move_y
        return None

    def move_spell(self, keys):

        if 1 in (keys[pg.K_UP], keys[pg.K_LEFT], keys[pg.K_DOWN], keys[pg.K_RIGHT]):
            move_x = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
            move_y = keys[pg.K_DOWN] - keys[pg.K_UP]

            return move_x, move_y
        return None

    def select_spell(self, key_press, keys):

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
                for key, value in spell_dict.items():
                    if self.casting_string == value:

                        self.casting_string = []
                        return key

            self.casting_string = []
        return None

