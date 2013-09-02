# -*- coding: utf-8 -*-
'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data
from cocos.director import director
from ui.main import main_scene
from ui.overview import Overview

def main():
    director.init(width=1024, height=768)
    director.run(Overview())
