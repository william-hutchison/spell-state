# Spell State
## About
An in-development wizard role-playing game / real-time strategy. Guide your autonomous subjects towards victory.

## Instructions
Move your wizard around the world with the WASD keys. Move the camera and inspector with the arrow keys. To refocus the camera onto your wizard, press F.

To see what your citizens and buildings are up to, move the inspector onto them and press enter.

Have a look at the spell book at the bottom left of your screen. You can cast these spells by holding down space and typing the required arrow key combination, then releasing space. You are now holding the spell. If it is a directional spell, cast it in the desired direction with the arrow keys. If it is a selection spell, move the selector to the desired location with the arrow keys and then press enter.

If you like what one of your subjects is doing, bestow a blessing on them (researched at the Well of Blessings) and they will be more likely to perfrom that action in the future. If you don't like what one of your subjects is doing, bestow a curse on them (researched at the Well of Curses) and they will be less likely to perfrom that action in the future.

## Control list
- Wizard movement - WASD
- Camera movement - Arrows
- Inspect tile - Enter
- Refocus camera on wizard - F
- Detect spell combo - Hold space
- Input spell combo - Arrows
- Cast spell - Arrows
- Menu navigation - Arrows
- Menu selection - Enter
- Access in-game menu - Escape

## Setup
A macOS executable is available in the bin folder. Apologies for the current absence of Linux and Windows executables! Alternatively, the game can be run using Python 3.9 with the required libraries at main.py. The executable is a bundle of the project at git commit 10c894c.

## Required libraries
- os
- sys
- numpy
- math
- random
- noise
- pygame
- pickle

