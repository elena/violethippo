# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import MultiplexLayer
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, CENTER
from cocos.scene import Scene

from overview import Overview

class MainMenu(Menu):

    def __init__(self):

        super(MainMenu, self).__init__("Moon Game")
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.font_title['font_size'] = 42
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20

        items = []
        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_new_game(self):
        director.push(Overview())

    def on_options(self):
        self.parent.switch_to(1)

    def on_quit(self):
        director.pop()


class OptionMenu(Menu):

    def __init__(self):

        super(OptionMenu, self).__init__("Moon Game Options")

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.font_title['font_size'] = 42
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20

        items = []
        items.append(MenuItem('Fullscreen', self.on_fullscreen))
        items.append(MenuItem('OK', self.on_quit))
        self.create_menu(items, zoom_in(), zoom_out())

    def on_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)


director.init(resizable=True)
menu_layer = MultiplexLayer(MainMenu(), OptionMenu())
menu_scene = Scene(menu_layer)
