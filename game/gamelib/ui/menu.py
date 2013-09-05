# -*- coding: utf-8 -*-
import os
import json
import time
from cocos.director import director
from cocos.layer import MultiplexLayer, Layer
from cocos.sprite import Sprite
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, CENTER
from cocos.scene import Scene

from gamelib import model

from overview import Overview


def list_saves(directory='save'):
    if not os.path.exists(directory):
        return []
    r = []
    for m, n in sorted((os.stat(os.path.join('save', n)).st_mtime, n)
        for n in os.listdir('save') if n not in '..'):
        with open(os.path.join('save', n)) as f:
            d = json.load(f)
            if d['.data_version'] == model.DATA_VERSION:
                # TODO use a nice-date printer of some sort here
                t = time.localtime(d['.turn_date'])
                mon = time.strftime('%b', t)
                h = t.tm_hour
                if h > 12:
                    h -= 12
                    ap = 'PM'
                else:
                    ap = 'AM'
                ds = '%s %d %d:%02d%s' % (mon, t.tm_mday, h, t.tm_min, ap)
                title = '%s (turn %d)' % (ds, d['.turn'])
                r.append((n, title, d))
    return r


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.font_title['font_size'] = 42
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        self.title_label = "Menu"

        items = []
        saves = list_saves()
        if os.path.exists('save'):
            num_saves = len(saves)
        else:
            num_saves = 0
        # if num_saves < 5:
            # that restriction is to keep the load menu fitting on the screen
            # items.append(MenuItem('New Game', self.on_new_game))
        # new game is more important at the moment (and load game no work)
        items.append(MenuItem('New Game', self.on_new_game))
        if num_saves:
            items.append(MenuItem('Continue Game - %s' % saves[-1][1],
                self.on_continue_game))
            items.append(MenuItem('Load Game', self.on_load_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def on_enter(self):
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
        name = list_saves()[-1][0]
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
    # TODO finish me
    def on_select_game(self, filename):
        game = model.Game.json_loadfile(os.path.join('save', filename))
        model.game = game
        director.push(Overview())

    def on_load_game(self):
        director.push(LoadGame())

    def on_quit(self):
        self.parent.switch_to(0)

class TitleLayer(Layer):
    # is_event_handler = True
    def __init__(self):
        super(TitleLayer, self).__init__()
        w, h = director.get_window_size()
        logo = Sprite('Moon_1.jpg')
        lh = logo.height
        logo.position = (w//2, h//2)
        self.add(logo)

def menu():
    return Scene(TitleLayer(), MultiplexLayer(MainMenu(), OptionMenu(), LoadMenu()))

if __name__ == '__main__':
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    director.run(menu())
