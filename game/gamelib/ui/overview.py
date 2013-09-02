import os
import pyglet

from cocos.scene import Scene
from cocos.layer import Layer
from cocos.sprite import Sprite


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__()
        self.add(Display())


class Display(Layer):
    def __init__(self):
        super(Display, self).__init__()
        self.moon = Sprite('moon.png', position=(512, 500))
        self.add(self.moon)
        self.planet = Sprite('planet.png', anchor=(0, 0))
        self.add(self.planet)
