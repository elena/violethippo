# -*- coding: utf-8 -*-
'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data
from cocos.director import director
from ui.main import main_scene


def main():

    print "Hello from your game's main()"
    print data.load('sample.txt').read()

    # director.init run in menu.py lest spews AttributeError
    director.run(main_scene)