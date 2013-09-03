# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scenes import transitions
from cocos.sprite import Sprite
from cocos.scene import Scene
from cocos.text import Label
from pyglet.window import key
from gamelib.ui.menu import menu


def splash():
    return Scene(ColorLayer(128, 128, 128, 128), SplashControlLayer())


class SplashControlLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(SplashControlLayer, self).__init__()
        self.text_title = Label("Hippo Moon Monkey Revolution",
            font_size=22, x=15, y=450)

        self.text_help = Label("Hit 'Enter' to continue.",
            font_size=16, x=director.get_window_size()[0] /2, y=20,
            anchor_x='center')

        logo = Sprite('hippo-300.png')
        logo.position = (320, 250)
        self.add(logo)

    def draw(self):
        self.text_title.draw()
        self.text_help.draw()

    def on_key_press(self, k, m):
        if k == key.ENTER:
            director.replace(transitions.FadeTransition(menu()))
            return True


if __name__ == '__main__':
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    director.run(splash())
