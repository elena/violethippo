import os
import pyglet

from cocos.scene import Scene
from cocos.layer import Layer
from cocos.sprite import Sprite

import squirtle


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__()
        path = os.path.join(pyglet.resource.location('overview.svg').path,
            'overview.svg')
        layers = squirtle.load_layers(path, circle_points=100)
        self.add(SVG(layers['display']))
        self.hit = layers['hitbox']

class SVG(Layer):
    def __init__(self, svg):
        super(SVG, self).__init__()
        self.svg = svg

    def draw(self):
        # pyglet.gl.glPushMatrix()
        # self.transform()
        self.svg.draw(0, 768)
        # pyglet.gl.glPopMatrix()

