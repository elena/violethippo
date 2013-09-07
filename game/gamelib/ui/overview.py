# -*- coding: utf-8 -*-
'''
TODO:
- The player mouses over or selects the points which represent the resistance
  groups and is shown their name, their modus operandi, maybe some other
  stats? Along with the list of plans they are working on.
- Each plan has a name, a brief description, and a bar showing how close to
  completion/activation it is.
- Clicking on a plan pops it up in a larger box, showing the longer
  description, the intended effects and the risks/costs, along with the
  options for player to use points (this screen not shown). A close button
  takes you back to this.
- Similarly, clicking on the Group info area pops up a box with info about the
  group, its current status, and the buffs it has waiting.
- To the right is the current pool of activity points, and the list of player
  orders, with a name and cost for each. Clicking on any of them brings up a
  box with a detailed description of what it does and an “Do this” button (as
  well as a close). Note that costs will change after the first (free) action
  - ie the costs are 0 for the first action, and then change.
'''

import os
import pyglet
import random

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer, PythonInterpreterLayer
from cocos.text import Label
from cocos.sprite import Sprite

from ninepatch import LabelNinepatch

from gamelib import model, player_orders

from dialog import ChoiceLayer
from debug import DebugLayer
from widgets import Button, TextButton, Bargraph, MultipleBargraph


def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(Sprite('bg.jpg', position=(512, 384)), Fixed())


class Fixed(Layer):   # "display" needs to be renamed "the one with buttons and info"
    is_event_handler = True

    def __init__(self):
        super(Fixed, self).__init__()

        self.console = DebugLayer()
        self.add(self.console, z=10)
        self.console.visible = False

        # delay the rest of the initialisation so we can finish creating the
        # game while the debug console is available
        self.initialised = False

        self.buttons = []

    def on_enter(self):
        super(Fixed, self).on_enter()
        if self.initialised:
            return

        self.buttons = []

        # ok, do we need to finish creating the game?
        if model.game.turn == 0:
            # prior to first turn
            model.game.init_new_game(self)

        w, h = director.get_window_size()

        # now it's safe to show information about the game
        self.add(Label('Threat:', x=450, y=680, anchor_y='top',
            font_name='Prototype'), 'threat')
        self.add(MultipleBargraph((200, 8), (.1, .1, .1), position=(260, 332),
            style='solid', colors=[(200, 100, 100), (200, 200, 100),
            (100, 200, 100)]), name='threat_graph')
        self.add(Label('Visible:', x=450, y=660, anchor_y='top',
            font_name='Prototype'))
        self.add(MultipleBargraph((200, 8), (1, 1, 1), position=(260, 322),
            style='solid', colors=[(200, 100, 100), (200, 200, 100),
            (100, 200, 100)]), name='visible_graph')

        self.add(Label('', multiline=True, x=20, y=70, width=200,
            anchor_x='left', anchor_y='bottom', font_name='Prototype'),
            name='turn_label')

        end_turn = Button('end turn button.png', (w-32, h-32), None,
            self.on_new_turn)
        self.buttons.append(end_turn)
        self.add(end_turn, name='end_turn')

        self.info = Details()
        self.info.position = (0, 300)
        self.add(self.info)

        self.zinfo = ZoneInfo()
        self.zinfo.position = (400, h-130)
        self.add(self.zinfo)

        self.zone = Zone()
        self.add(self.zone, z=-1)

        self.update_info()

        # now we're done
        self.initialised = True

    def update_info(self):
        free = ''
        if model.game.player.free_order:
            free = ' + free'
        self.get('turn_label').element.text = 'Turn: %d\nActivity Points: '\
            '%d%s\nHideout: %s' % (model.game.turn,
                model.game.player.activity_points, free,
                model.game.player.hideout or 'Not Chosen')

        zone1 = model.game.moon.zones[model.INDUSTRY]
        zone2 = model.game.moon.zones[model.LOGISTICS]
        zone3 = model.game.moon.zones[model.MILITARY]
        self.get('threat_graph').values = (zone1.faction.threat,
            zone2.faction.threat, zone3.faction.threat)
        self.get('visible_graph').values = (zone1.player_found,
            zone2.player_found, zone3.player_found)
        self.zinfo.display_zone(self.zone.mode)

        if not model.game.player.hideout:
            # show Establish/Move hideout button only
            self.get('end_turn').visible = False
        else:
            # enable turn button and all the player actions
            self.get('end_turn').visible = True

        # remove old player order buttons
        for but in list(self.buttons):
            # player order buttons have an 'order' attribute
            if hasattr(but, 'order'):
                self.remove(but)
                self.buttons.remove(but)

        # add appropriate player order buttons
        x = y = 20
        for order in player_orders.all:
            cost = order.cost(self.zone)
            if cost is None:
                continue
            b = TextButton('%dAP: %s' % (cost, order.label), (x, y), order,
                self.on_player_order)
            b.order = order
            x += b.label.element.content_width + 20
            self.buttons.append(b)
            self.add(b)

    class SIGNAL_GAMEOVER(Exception):
        pass

    def on_new_turn(self, button):
        try:
            model.game.update(self)
        except self.SIGNAL_GAMEOVER:
            pass
        if model.game.player.hideout:
            self.zone.switch_zone_to(self.zone.buts[model.game.player.hideout])
        self.update_info()

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            if button.visible and button.get_rect().contains(x, y):
                button.on_click(button)
                return True         # event handled

    def on_player_order(self, button):
        button.order.execute(self)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.GRAVE:
            self.console.toggle_visible()
            return True

    def ask_choice(self, title, choices, callback):
        '''A player order wants us to ask the user to make a choice.

        We callback the callback with (self, choice from the list). Or not.
        '''
        self.add(ChoiceLayer(title, choices, callback), z=1)

    def msg(self, message, *args):
        self.console.write(message % args)

    def graph(self, graph, line, turn, value):
        pass


class Zone(Layer):
    is_event_handler = True

    def __init__(self):
        super(Zone, self).__init__()
        w, h = director.get_window_size()
        self.mode = model.INDUSTRY

        self.zone_images = {
            model.INDUSTRY: pyglet.resource.image('industry.png'),
            model.LOGISTICS: pyglet.resource.image('logistics.png'),
            model.MILITARY: pyglet.resource.image('military.png')
        }

        self.icons = {
            ('privileged', False): pyglet.resource.image('icon-priv_off.png'),
            ('privileged', True): pyglet.resource.image('icon-priv_on.png'),
        }

        GAME_WIDTH = 1024
        GAME_HEIGHT = 768

        ZONE_WIDTH = 560
        ZONE_HEIGHT = 640

        self.active = Sprite(self.zone_images[model.INDUSTRY],
            anchor=((-(GAME_WIDTH-ZONE_WIDTH), -(GAME_HEIGHT-ZONE_HEIGHT)))
        )
        self.add(self.active, z=-1)

        self.buts = {
            model.INDUSTRY: Button('but-ind_off.png', (450, 680),
                'industry', self.switch_zone_to),
            model.LOGISTICS: Button('but-log_off.png', (640, 680),
                'logistics', self.switch_zone_to),
            model.MILITARY: Button('but-mil_off.png', (830, 680),
                'military', self.switch_zone_to),
        }
        self.add(self.buts[model.INDUSTRY])
        self.add(self.buts[model.LOGISTICS])
        self.add(self.buts[model.MILITARY])

    def on_enter(self):
        super(Zone, self).on_enter()
        # self.parent.msg('setting zone based on %s'%model.game.player.hideout)
        if model.game.player.hideout:
            self.parent.msg('setting zone to %s'%model.game.player.hideout)
            self.mode = None
            self.switch_zone_to(self.buts[model.game.player.hideout])
        else:
            self.mode = None
            self.switch_zone_to(self.buts[model.LOGISTICS])

    def switch_zone_to(self, but):
        if self.mode == but.info:
            return

        active_zone = but.info
        for name in 'industry logistics military'.split():
            but = self.buts[name]
            nam = name[:3]
            if name == active_zone:
                but.image = pyglet.resource.image('but-%s_on.png' % nam)
            else:
                but.image = pyglet.resource.image('but-%s_off.png' % nam)
        self.mode = active_zone
        # self.buts[self.mode] = pyglet.resource.image('%s button off.png'% self.mode)
        # self.buts[active_zone] = pyglet.resource.image('%s button on.png'% active_zone)
        self.active.image = self.zone_images[active_zone]
        self.parent.update_info()
        self.parent.info.hide_info()

        # clear out unnecessary butts
        for but in list(self.buts):
            if but in (model.INDUSTRY, model.LOGISTICS, model.MILITARY):
                continue
            self.remove(self.buts[but])
            del self.buts[but]

        zone = model.game.moon.zones[active_zone]
        self.buttons = []
        def add_button():
            y = 758
            x = 10
            while 1:
                indent, but = yield
                y -= but.image.height
                but.position = (x + indent, y)
                self.buts[but.info] = but
                self.add(but, z=1)

        adder = add_button()
        adder.next()

        adder.send((0, Button('faction button.png', (0, 0), 'faction',
            self.on_show_info)))
        self.priv_but = Button('icon-priv_off.png', (0, 0), 'privileged',
            self.on_show_info)
        adder.send((20, self.priv_but))
        for group in zone.privileged.resistance_groups:
            adder.send((40, Button('icon-pres_off.png', (0, 0), group,
                self.on_show_info)))
        adder.send((20, Button('icon-serv_off.png', (0, 0), 'servitors',
            self.on_show_info)))
        for group in zone.servitor.resistance_groups:
            adder.send((40, Button('icon-sres_off.png', (0, 0), group,
                self.on_show_info)))

    def on_mouse_press(self, x, y, button, modifiers):
        for key, but in self.buts.items():
            if key == self.mode:
                continue
            if but.get_rect().contains(x, y):
                but.on_click(but)
                return True         # event handled

    def on_show_info(self, but):
        zone = model.game.moon.zones[self.mode]
        if but.info == 'faction':
            self.parent.info.show_faction(self.mode)
        elif but.info == 'privileged':
            self.parent.info.show_cohort(zone.privileged)
        elif but.info == 'servitors':
            self.parent.info.show_cohort(zone.servitor)
        else:
            self.parent.info.show_resistance(but.info)


class InfoLayer(Layer):
    def packer(self):
        def add_info():
            self.height = 0
            self.min_x = self.max_x = 0
            while 1:
                text, info, value = yield
                y = -self.height
                label = Label(text, align='right', anchor_x='right',
                    anchor_y='top', x=0, y=y, font_name='Prototype')
                self.min_x = min(self.min_x, -label.element.content_width)
                self.height += label.element.content_height
                self.add(label)
                if info is not None:
                    label = Label(info, align='left', anchor_x='left',
                        anchor_y='top', x=2, y=y, font_name='Prototype')
                    self.add(label)
                    self.max_x = max(self.max_x, label.element.content_width)
                else:
                    self.bg = Bargraph((80, 10), value, position=(2, y-16))
                    self.max_x = max(self.max_x, 80)
                    if value < .3:
                        self.bg.color = (200, 100, 100)
                    elif value < .7:
                        self.bg.color = (200, 200, 100)
                    else:
                        self.bg.color = (100, 200, 100)
                    self.add(self.bg)
                self.width = self.max_x - self.min_x

        adder = add_info()
        adder.next()
        add_info = lambda *a: adder.send(a)
        return add_info


class Details(InfoLayer):
    # is_event_handler = True
    active_info = None

    # def on_mouse_press(self, x, y, button, modifiers):
    #     if self.visible and self.rect.contains(x, y):
    #         self.visible = False
    #         return True         # event handled

    def hide_info(self):
        self.visible = False
        self.active_info = None

    def show_faction(self, active_zone):
        zone = model.game.moon.zones[active_zone]
        faction = zone.faction
        if self.active_info == faction:
            self.hide_info()
            return
        self.active_info = faction
        self.show_info([
            ('Faction:', active_zone, None),
            ('Leader:', faction.name, None),
            ('Size:', None, faction.size),
            ('Informed:', None, faction.informed),
            ('Smart:', None, faction.smart),
            ('Loyal:', None, faction.loyal),
            ('Rich:', None, faction.rich),
            ('Buffs:', ', '.join(faction.buffs), None),
            ('Threat:', None, faction.threat),
            ('Alert:', None, faction.alert),
        ])

    def show_resistance(self, group):
        if self.active_info == group:
            self.hide_info()
            return
        self.active_info = group
        self.show_info([
            ('Name:', group.name, None),
            ('Size:', None, group.size),
            ('Informed:', None, group.informed),
            ('Smart:', None, group.smart),
            ('Rich:', None, group.rich),
            ('Loyal:', None, group.loyal),
            ('Visibility:', None, group.visibility),
            ('Buffs:', ', '.join(group.buffs), None),
        ])

    def show_cohort(self, cohort):
        if self.active_info == cohort:
            self.hide_info()
            return
        self.active_info = cohort
        if cohort.is_servitor:
            output = ('Willingness:', None, cohort.willing)
        else:
            output = ('Efficiency:', None, cohort.efficiency)
        self.show_info([
            ('Cohort:', cohort.__class__.__name__, None),
            ('Size:', None, cohort.size),
            ('Liberty:', None, cohort.liberty),
            ('Quality of Life:', None, cohort.quality_of_life),
            ('Cash:', None, cohort.cash),
            output,
            ('Rebelliousness:', None, cohort.rebellious),
        ])

    def show_info(self, info):
        for z, child in list(self.children):
            self.remove(child)

        packer = self.packer()
        for row in info:
            packer(*row)

        self.x = -self.min_x + 10
#        self.y = self.height

        # self.popup_9p = LabelNinepatch('border-9p.png', self)
        # self.add(self.popup_9p)
        self.visible = True


class ZoneInfo(InfoLayer):
    descr = dict(
        industry='produces goods and food',
        logistics='transports to and from planet',
        military='provides force and stability',
    )

    def display_zone(self, active_zone):
        for z, child in list(self.children):
            self.remove(child)

        zone = model.game.moon.zones[active_zone]

        packer = self.packer()
        packer('Zone', self.descr[active_zone], None)
        packer('Provides:', ', '.join(zone.provides), None)
        packer('Requires:', ', '.join(zone.requirements), None)
        for n in zone.store:
            packer('%s:' % n.title(), None, zone.store[n] / 10.)
        # packer('Privileged Rebellious:', None, zone.privileged.rebellious)
        # packer('Servitor Rebellious:', None, zone.servitor.rebellious)
        # packer('Privileged Willing:', None, zone.privileged.willing)
        # packer('Servitor Willing:', None, zone.servitor.willing)
        packer('Faction Status:', zone.faction.state_description, None)

        self.width = self.max_x - self.min_x

if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
