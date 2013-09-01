# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scenes import transitions
from cocos.sprite import Sprite
from pyglet import font
from pyglet import text
from pyglet.window import key
from gamelib.ui.menu import menu_scene


class SplashControlLayer(Layer):

    is_event_handler = True

    def __init__(self, next_scene):

        super(SplashControlLayer, self).__init__()

        self.text_title = text.Label(
            "Hippo Moon Monkey Revolution",
            font_size=22, x=15, y=450)

        self.text_help = text.Label(
            "Hit 'Enter' to continue.",
            font_size=16, x=director.get_window_size()[0] /2, y=20,
            anchor_x=font.Text.CENTER)

        self.next_scene = next_scene

        logo = Sprite('assets/hippo-300.png')
        logo.position = (320, 250)
        self.add(logo)

    def draw(self):
        self.text_title.draw()
        self.text_help.draw()

    def on_key_press(self, k, m):

        if k == key.ENTER:
            director.replace(transitions.FlipX3DTransition(
                self.next_scene, 1.25))
            return True


splash_color = ColorLayer(128,128,128,128)
splash_control = SplashControlLayer(next_scene=menu_scene)
