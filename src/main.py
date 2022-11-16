import pygame as pg
import sys
import pickle

import player
import world
import graphics
import menus
import globe
import audio


class Game:
    """Class to store, update and coordinate the objects required for gameplay, menus, user input and graphics."""

    def __init__(self):

        pg.init()
        globe.time = globe.Time()
        self.world = world.World()
        self.player = player.Player(self.world.state_list[0].wizard)
        self.graphics_manager = graphics.GraphicsManager()
        self.menu_manager = menus.MenuManager()
        audio.audio = audio.Audio(self.world.state_list[0].wizard)

    def update(self):
        """Control the game state, update the display and detect any keyboard input for each step of the main game
        loop."""

        events = event_loop()

        # Run the game
        if not self.menu_manager.current_menu:
            self.play(events)
            audio.audio.stop_music()
            globe.time.update()

        # TODO Stop time from increasing while the game is paused
        # Run the menu
        else:
            self.graphics_manager.update_menu(self.menu_manager.current_menu.options, self.menu_manager.current_menu.current_option)
            self.menu_manager.update(events, self.graphics_manager.set_window_scale, self.save_file, self.load_file, self.exit_game)

        pg.display.update()

    def play(self, events):
        """Update all objects necessary to run the game."""

        self.player.update(self.world.map_topology, self.world.map_resource, self.world.map_item, self.world.map_entities, events)
        self.world.update()
        self.graphics_manager.update_terrain(self.player.camera.location, self.world.map_topology, self.world.map_resource, self.world.map_item, self.world.map_entities, self.player.camera.inspector_location, self.player.camera.inspector_mode, self.player.character.wizard.location, self.world.state_list)
        self.graphics_manager.update_interface(self.world.state_list[0], self.player.character, self.player.camera, self.player.camera.inspector_dict, self.player.interface, self.world.map_item)

        # Check for menu launch
        if events[0] and events[1][pg.K_ESCAPE]:
            self.menu_manager.current_menu = self.menu_manager.menu_dict["Pause"]()

    def save_file(self, file_name):
        """Store any necessary information outside the world object within the world object, then create a save file
        from the world object."""

        self.world.save_time = globe.time.now()
        self.world.save_player = player.Player(self.world.state_list[0].wizard)
        
        with open('saves/'+file_name, 'wb') as f:
            pickle.dump(self.world, f)

    def load_file(self, file_name):
        """Restore the world object from the save file, then restore any necessary information outside the world
        object."""

        with open('saves/'+file_name, 'rb') as f:
            self.world = pickle.load(f)

        globe.time.set_time(self.world.save_time)
        self.player = self.world.save_player

    def exit_game(self):
        """Safely close the game."""
        
        pg.quit()
        sys.exit()


def event_loop():
    """Checks for keyboard input. Returns True if any key is pressed this step, and returns all keys held this step."""

    key_press = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            key_press = True

    return key_press, pg.key.get_pressed()


# Create the game object
game = Game()

# Run the main game loop
while True:
    game.update()
