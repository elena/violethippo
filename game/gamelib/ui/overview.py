import os
import pyglet

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite


from gamelib import model


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(ColorLayer(245, 244, 240, 255),
            Display())


class Display(Layer):
    def __init__(self):
        super(Display, self).__init__()
        w, h = director.get_window_size()

        self.turn_label = Label('', color=(0, 0, 0, 255), x=0, y=h, anchor_y='top')
        self.add(self.turn_label)
        self.threat_label = Label('', color=(0, 0, 0, 255), x=0, y=h-20, anchor_y='top')
        self.add(self.threat_label)
        self.visible_label = Label('', color=(0, 0, 0, 255), x=0, y=h-40, anchor_y='top')
        self.add(self.visible_label)
        self.update()

        self.industry = pyglet.resource.image('industry.png')
        self.logistics = pyglet.resource.image('logistics.png')
        self.military = pyglet.resource.image('military.png')

        self.add(Sprite(self.industry, position=(w//2, h//2)))

    def update(self):
        self.turn_label.element.text = 'Turn: %d' % model.game.turn
        self.threat_label.element.text = 'Threat: %d' % model.game.threat
        self.visible_label.element.text = 'Visibility: %d' % model.game.player.visibility



if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()

    director.run(Overview())
