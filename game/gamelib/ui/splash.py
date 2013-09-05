# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scenes import transitions
from cocos.sprite import Sprite
from cocos.scene import Scene
from cocos.text import Label
from pyglet.window import key
from gamelib.ui.title import title


def splash():
    return Scene(ColorLayer(128, 128, 128, 255), SplashControlLayer())


class SplashControlLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(SplashControlLayer, self).__init__()
        w, h = director.get_window_size()
        logo = Sprite('hippo-300.png')
        lh = logo.height
        logo.position = (w//2, h//2)
        self.add(logo)

        # title = Sprite('Title_Moon1.png')
        # title.position = (w//2, h//2 + (3*lh)//4)
        # self.add(title)

        self.add(Label("Presented by the Violet Hippo",
            font_size=22, x=w//2, y=h//2 + lh//2, anchor_x='center',
            anchor_y='bottom'))

        self.add(Label("Click to Continue",
            font_size=16, x=w//2, y=h//2 - lh//2 - 20, anchor_x='center',
            anchor_y='top'))

    def on_key_press(self, *args):
        director.replace(transitions.FadeTransition(title()))
        return True

    def on_mouse_press(self, *args):
        director.replace(transitions.FadeTransition(title()))
        return True


if __name__ == '__main__':
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    director.run(splash())
