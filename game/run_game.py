#! /usr/bin/env python
from cocos.director import director
director.init(width=1024, height=768)


import pyglet
pyglet.resource.path.append('data')
pyglet.resource.reindex()
pyglet.resource.add_font('Prototype.ttf')

from cocos.scene import Scene
from gamelib.ui.splash import splash

director.run(splash())
