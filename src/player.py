import pygame as pg

import globe


class Player:  # TODO Should this object even exist? Probably not

    def __init__(self, player_wizard):

        self.character = Character(self, player_wizard)
        self.camera = Camera(self)
        self.interface = Interface(self, player_wizard)

    def update(self, map_topology, map_resource, map_item, map_entities, events):
        
        self.character.update(map_entities, map_topology, map_resource, map_item, events[0], events[1])
        self.camera.update(self.character, map_topology, map_resource, map_item, map_entities, events[0], events[1])
        self.interface.update(map_entities, map_item, events[0], events[1])


class Camera:
    
    def __init__(self, ruler_player):

        self.ruler_player = ruler_player

        self.location = (0, 0)
        self.time_last = 0
        self.camera_follow = True
        self.inspector_location = (0, 0)
        self.inspector_mode = "inspect"
        self.inspector_dict = {"Topology": "", "Resource": "", "Entity type": "", "Location": "", "Action": "", "Stock": "", "Health": "", "Construction remaining": ""}

    def update(self, player_character, map_topology, map_resource, map_item, map_entities, key_press, keys):

        # prevent camera actions when interface object is in use
        if self.ruler_player.interface.transfer_target:
            return None

        # check for a spell requiring target selection
        if spell_list := player_character.wizard.spell_list:
            if type(spell_list[0]).__name__ in ['SpellHeal']:
                self.inspector_mode = "select"

        self.location, self.inspector_location = self.move_camera(player_character, keys)

        if self.inspector_mode == "inspect":
            if key_press and keys[pg.K_RETURN]:
                self.inspect(map_topology, map_resource, map_item, map_entities, keys)

        elif self.inspector_mode == "select":
            player_character.wizard.spell_list[0].location_select = self.inspector_location
            if key_press and keys[pg.K_RETURN]:
                player_character.wizard.spell_list[0].select(map_entities)
                self.inspector_mode = "inspect"

    def move_camera(self, player_character, keys):
        """Check for keyboard input and set new camera tile location if move detected."""

        camera_location = self.location

        # set camera to follow the player
        if pg.key.get_pressed()[pg.K_f]:
            self.camera_follow = True

        # move the camera to follow the player_character
        if self.camera_follow:
            camera_location = (player_character.wizard.location[0] - 30, player_character.wizard.location[1] - 20)

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
                    self.camera_follow = False
                    self.time_last = globe.time.now()
        # TODO This will brake if world scale changes
        inspector_location = (camera_location[0]+30, camera_location[1]+20)

        return camera_location, inspector_location

    def inspect(self, map_topology, map_resource, map_item, map_entities, keys):
        """Set new inspector tile location based on camera location. Check for keyboard input and 
        activate inspector if request detected."""

        self.inspector_dict = dict.fromkeys(self.inspector_dict, "")
        self.inspector_dict["Topology"] = str(map_topology[self.inspector_location[1]][self.inspector_location[0]])
        self.inspector_dict["Resource"] = str(map_resource[self.inspector_location[1]][self.inspector_location[0]])
        self.inspector_dict["Item"] = str(map_item[self.inspector_location[1]][self.inspector_location[0]])

        inspect_object = map_entities[self.inspector_location[1]][self.inspector_location[0]]

        if inspect_object:
            self.inspector_dict["Entity type"] = str(type(inspect_object).__name__)
            self.inspector_dict["Location"] = str(inspect_object.location)
            self.inspector_dict["Stock"] = str(inspect_object.stock_list)
            self.inspector_dict.update(inspect_object.stat_dict)

            if type(inspect_object).__name__ == 'Person':
                self.inspector_dict["Action"] = str(inspect_object.action_super)

            if type(inspect_object).__name__ in ['Tower', 'House', 'Shrine', 'WellOfCurses', 'WellOfBlessings']:
                self.inspector_dict["Stock list needed"] = str(inspect_object.stock_list_needed)
                self.inspector_dict["Construction remaining"] = str(inspect_object.under_construction)
                self.inspector_dict["Work remaining"] = str(inspect_object.under_work)


class Character:

    def __init__(self, ruler_player, wizard):

        self.ruler_player = ruler_player
        self.wizard = wizard

        self.casting_string = []

    def update(self, map_entities, map_topology, map_resource, map_item, key_press, keys):

        # TODO This is messy
        move_character_attempt = None
        move_spell_attempt = None
        cast_attempt = None

        move_character_attempt = self.move_character(keys)

        # perform all non-interface actions
        if not self.ruler_player.interface.transfer_target:
            # move spell if holding otherwise cast new spell
            if [i for i in self.wizard.spell_list if i.status == "hold"]:
                move_spell_attempt = self.move_spell(key_press, keys)
            else:
                cast_attempt = self.select_spell(key_press, keys)

        self.wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)

    def move_character(self, keys):
        """Detect keyboard input and return appropriate direction tuple for wizard move."""

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
                    if self.casting_string == value["combo"] and value["unlocked"]:

                        self.casting_string = []
                        return key

            self.casting_string = []
        return None


class Interface:

    def __init__(self, ruler_player, wizard):

        self.ruler_player = ruler_player
        self.wizard = wizard

        self.transfer_target = None
        self.options = [[], []]
        self.current_option = [0, 0]

    def update(self, map_entities, map_item, key_press, keys):

        if self.transfer_target:
            self.options[0] = self.wizard.stock_list

            if type(self.transfer_target) == tuple:
                self.options[1] = [map_item[self.transfer_target[1]][self.transfer_target[0]]]
            else:
                self.options[1] = self.transfer_target.stock_list

            self.navigate_transfer_interface(map_item, key_press, keys)

        else:
            self.check_transfer_interface(map_entities, key_press, keys)

    def navigate_transfer_interface(self, map_item, key_press, keys):
        """Navigate through the transfer interface and attempt to transfer the desired item."""

        if key_press:

            # close interface
            if 1 in (keys[pg.K_e], keys[pg.K_f], keys[pg.K_w], keys[pg.K_a], keys[pg.K_s], keys[pg.K_d]):
                self.ruler_player.camera.camera_follow = True
                self.transfer_target = None

            # change selection
            elif keys[pg.K_DOWN]:
                if self.current_option[1] < len(self.options[self.current_option[0]]) - 1:
                    self.current_option[1] += 1
            elif keys[pg.K_UP]:
                if self.current_option[1] > 0:
                    self.current_option[1] -= 1
            elif keys[pg.K_RIGHT]:
                if self.current_option[0] == 0:
                    self.current_option[0] = 1
            elif keys[pg.K_LEFT]:
                if self.current_option[0] == 1:
                    self.current_option[0] = 0

            # attempt item transfer
            elif keys[pg.K_RETURN]:
                if self.options[self.current_option[0]]:
                    self.transfer(map_item)

        # prevent selection of invalid option
        self.current_option[1] = min(self.current_option[1], len(self.options[self.current_option[0]])-1)
        self.current_option[1] = max(self.current_option[1], 0)

    def check_transfer_interface(self, map_entities, key_press, keys):
        """Check for the creation of a new transfer interface and assignment of a new transfer target, either a tuple
        location on the item map or another entity."""

        if key_press:
            if keys[pg.K_e] and keys[pg.K_UP]:
                if map_entities[self.wizard.location[1]-1][self.wizard.location[0]]:
                    self.transfer_target = map_entities[self.wizard.location[1]-1][self.wizard.location[0]]
                else:
                    self.transfer_target = (self.wizard.location[0], self.wizard.location[1]-1)

            elif keys[pg.K_e] and keys[pg.K_LEFT]:
                if map_entities[self.wizard.location[1]][self.wizard.location[0]-1]:
                    self.transfer_target = map_entities[self.wizard.location[1]][self.wizard.location[0]-1]
                else:
                    self.transfer_target = (self.wizard.location[0]-1, self.wizard.location[1])

            elif keys[pg.K_e] and keys[pg.K_DOWN]:
                if map_entities[self.wizard.location[1]+1][self.wizard.location[0]]:
                    self.transfer_target = map_entities[self.wizard.location[1]+1][self.wizard.location[0]]
                else:
                    self.transfer_target = (self.wizard.location[0], self.wizard.location[1]+1)

            elif keys[pg.K_e] and keys[pg.K_RIGHT]:
                if map_entities[self.wizard.location[1]][self.wizard.location[0]+1]:
                    self.transfer_target = map_entities[self.wizard.location[1]][self.wizard.location[0]+1]
                else:
                    self.transfer_target = (self.wizard.location[0]+1, self.wizard.location[1])

    def transfer(self, map_item):
        """Transfer the desired item between the player character and the transfer target."""

        # transfer between player character and a location in the item map
        if type(self.transfer_target) == tuple:
            if self.current_option[0] == 0:
                if not map_item[self.transfer_target[1]][self.transfer_target[0]]:
                    map_item[self.transfer_target[1]][self.transfer_target[0]] = self.options[0][self.current_option[1]]
                    self.wizard.stock_list.remove(self.options[0][self.current_option[1]])
            elif self.current_option[0] == 1:
                if len(self.wizard.stock_list) < self.wizard.stat_dict["stock_max"]:
                    self.wizard.stock_list.append(map_item[self.transfer_target[1]][self.transfer_target[0]])
                    map_item[self.transfer_target[1]][self.transfer_target[0]] = ""

        # transfer between player character and another entity
        else:
            if self.current_option[0] == 0:
                if len(self.transfer_target.stock_list) < self.transfer_target.stat_dict["stock_max"]:
                    self.transfer_target.stock_list.append(self.options[0][self.current_option[1]])
                    self.wizard.stock_list.remove(self.options[0][self.current_option[1]])
            elif self.current_option[0] == 1:
                if len(self.wizard.stock_list) < self.wizard.stat_dict["stock_max"]:
                    self.wizard.stock_list.append(self.options[1][self.current_option[1]])
                    self.transfer_target.stock_list.remove(self.options[1][self.current_option[1]])
