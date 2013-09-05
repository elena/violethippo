# -*- coding: utf-8 -*-
import os
from cocos.director import director
from cocos.layer import MultiplexLayer
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, CENTER
from cocos.scene import Scene

from gamelib import model

from overview import Overview


def list_saves(directory='save'):
    # TODO: ignore saves which don't match model.DATA_VERSION
    # version is last part of the filename, after last '_' and
    # before the last '.'
    return sorted((os.stat(os.path.join('save', n)).st_mtime, n)
        for n in os.listdir('save') if n not in '..')


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__("Moon Game")
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.font_title['font_size'] = 42
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        self.title_label = "Menu"

        items = []
        if os.path.exists('save'):
            num_saves = len(list_saves())
        else:
            num_saves = 0
        if num_saves < 5:
            # that restriction is to keep the load menu fitting on the screen
            items.append(MenuItem('New Game', self.on_new_game))
        if num_saves:
            items.append(MenuItem('Continue Game', self.on_continue_game))
            items.append(MenuItem('Load Game', self.on_load_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_enter(self):
        print 'Menu.on_enter'
        # when we enter this view - either in from starting up or by returning
        # from the overview screen, we need to clear the global in model.game
        model.game = None
        super(MainMenu, self).on_enter()

    def on_new_game(self):
        if not os.path.exists('save'):
            os.mkdir('save')
        game = model.Game()
        game.json_savefile(os.path.join('save', '%d.json' % game.created))
        model.game = game
        director.push(Overview())

    def on_continue_game(self):
        # play the last modified game
        name = list_saves()[-1][1]
        game = model.Game.json_loadfile(os.path.join('save', name))
        model.game = game
        director.push(Overview())

    def on_load_game(self):
        self.parent.switch_to(2)

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


class LoadMenu(Menu):
    def on_select_game(self, filename):
        game = model.Game.json_loadfile(os.path.join('save', filename))
        model.game = game
        director.push(Overview())

    def on_load_game(self):
        director.push(LoadGame())

    def on_quit(self):
        self.parent.switch_to(0)


def menu():
    return Scene(MultiplexLayer(MainMenu(), OptionMenu(), LoadMenu()))

if __name__ == '__main__':
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    director.run(menu())
