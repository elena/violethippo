# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scenes import transitions
from cocos.sprite import Sprite
from cocos.scene import Scene
from cocos.text import Label
from pyglet.window import key
from gamelib.ui.menu import menu


def title():
    return Scene(TitleLayer(), TitleControlLayer())


class TitleLayer(Layer):
    # is_event_handler = True
    def __init__(self):
        super(TitleLayer, self).__init__()
        w, h = director.get_window_size()
        logo = Sprite('Moon_1.jpg')
        lh = logo.height
        logo.position = (w//2, h//2)
        self.add(logo)

class TitleControlLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(TitleControlLayer, self).__init__()
        w, h = director.get_window_size()
        # logo = Sprite('Moon_1.jpg')
        # lh = logo.height
        # logo.position = (w//2, h//2)
        # self.add(logo)

        self.add(Label("Click to Continue",
            font_size=16, x=w//2, y=h//2 - 240, anchor_x='center',
            anchor_y='top', color=(200, 200, 200, 255)))

    def on_key_press(self, *args):
        director.replace(transitions.FadeTransition(menu()))
        return True

    def on_mouse_press(self, *args):
        director.replace(transitions.FadeTransition(menu()))
        return True


if __name__ == '__main__':
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    director.run(title())
