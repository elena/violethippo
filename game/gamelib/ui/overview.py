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
        self.threat_label = Label('Threat:', x=450, y=680, anchor_y='top',
            font_name='Prototype')
        self.add(self.threat_label)
        self.threat_graph = MultipleBargraph((200, 8), (.1, .1, .1),
            position=(260, 332), style='solid',
            colors=[(200, 100, 100), (200, 200, 100), (100, 200, 100)])
        self.add(self.threat_graph)
        self.visible_label = Label('Visible:', x=450, y=660, anchor_y='top',
            font_name='Prototype')
        self.add(self.visible_label, z=1)
        self.visible_graph = MultipleBargraph((200, 8), (1, 1, 1),
            position=(260, 322), style='solid',
            colors=[(200, 100, 100), (200, 200, 100), (100, 200, 100)])
        self.add(self.visible_graph, z=1)

        self.turn_label = Label('', multiline=True, x=20, y=70, width=200,
            anchor_x='left', anchor_y='bottom', font_name='Prototype')
        self.add(self.turn_label)

        self.end_turn = Button('end turn button.png', (w-32, h-32), None,
            self.on_new_turn)
        self.buttons.append(self.end_turn)
        self.add(self.end_turn)

        self.info = Info()
        self.add(self.info)

        self.zinfo = ZoneInfo()
        self.zinfo.position = (300, h-300)
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
        self.turn_label.element.text = 'Turn: %d\nActivity_points: %d%s\nHideout: %s' % (
            model.game.turn, model.game.player.activity_points, free,
            model.game.player.hideout or 'Not Chosen')
        zone1 = model.game.moon.zones[model.INDUSTRY]
        zone2 = model.game.moon.zones[model.LOGISTICS]
        zone3 = model.game.moon.zones[model.MILITARY]
        self.threat_graph.values = (zone1.faction.threat, zone2.faction.threat,
            zone3.faction.threat)
        self.visible_graph.values = (zone1.player_found,
            zone2.player_found, zone3.player_found)
        self.zinfo.display_zone(self.zone.mode)

        if not model.game.player.hideout:
            # show Establish/Move hideout button only
            self.end_turn.visible = False
        else:
            # enable turn button and all the player actions
            self.end_turn.visible = True

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
            model.INDUSTRY: Button('industry button.png', (450, 680),
                'industry', self.switch_zone_to),
            model.LOGISTICS: Button('logistics button.png', (640, 680),
                'logistics', self.switch_zone_to),
            model.MILITARY: Button('military button.png', (830, 680),
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


class Info(Layer):
    is_event_handler = True
    def __init__(self):
        super(Info, self).__init__()

        self.info_label = Label('', multiline=True,
            width=350, anchor_x='left', anchor_y='bottom', x=10, y=250,
            font_name='Prototype')
        self.info_label.visible = False

        self.popup_9p = LabelNinepatch('border-9p.png', self.info_label)
        self.add(self.popup_9p)
        self.popup_9p.visible = False

        self.active_info = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.popup_9p.visible and self.popup_9p.rect.contains(x, y):
            self.info_label.element.text = ''
            self.info_label.visible = False
            self.popup_9p.visible = False
            return True         # event handled

    def hide_info(self):
        self.info_label.visible = False
        self.popup_9p.visible = False
        self.active_info = None

    def show_faction(self, active_zone):
        zone = model.game.moon.zones[active_zone]
        faction = zone.faction
        if self.active_info == faction:
            self.hide_info()
            return
        self.active_info = faction
        self.info_label.element.text = '\n'.join([
            'Faction: %s' % active_zone,
            'Leader: %s' % faction.name,
            'Size: %.1f' % (faction.size * 10),
            'Informed: %.1f' % (faction.informed * 10),
            'Smart: %.1f' % (faction.smart * 10),
            'Loyal: %.1f' % (faction.loyal * 10),
            'Rich: %.1f' % (faction.rich * 10),
            'Buffs: %s' % ', '.join(faction.buffs),
            'Threat: %.1f' % (faction.threat * 10),
            'Alert: %.2f' % (faction.alert,),
        ])
        self.info_label.visible = True
        self.popup_9p.visible = True

    def show_resistance(self, group):
        if self.active_info == group:
            self.hide_info()
            return
        self.active_info = group
        self.info_label.element.text = '\n'.join([
            'Name: %s' % group.name,
            'Size: %.1f' % (group.size * 10),
            'Informed: %.1f' % (group.informed * 10),
            'Smart: %.1f' % (group.smart * 10),
            'Rich: %.1f' % (group.rich * 10),
            'Loyal: %.1f' % (group.loyal * 10),
            'Buffs: %s' % (', '.join(group.buffs),)
        ])
        self.info_label.visible = True
        self.popup_9p.visible = True

    def show_cohort(self, cohort):
        if self.active_info == cohort:
            self.hide_info()
            return
        self.active_info = cohort
        if cohort.is_servitor:
            output = 'Willingness: %.1f' % (cohort.willing * 10)
        else:
            output = 'Efficiency: %.1f' % (cohort.efficiency * 10)
        self.info_label.element.text = '\n'.join([
            'Cohort: %s' % cohort.__class__.__name__,
            'Size: %.1f' % (cohort.size * 10),
            'Liberty: %.1f' % (cohort.liberty * 10),
            'Quality of Life: %.1f' % (cohort.quality_of_life * 10),
            'Cash: %.1f' % (cohort.cash * 10),
            output,
            'Rebelliousness: %.1f' % (cohort.rebellious * 10),
        ])
        self.info_label.visible = True
        self.popup_9p.visible = True


class ZoneInfo(Layer):
    descr = dict(
        industry='produces goods and food',
        logistics='transports to and from planet',
        military='provides force and stability',
    )

    def display_zone(self, active_zone):
        for z, child in list(self.children):
            self.remove(child)

        def add_info():
            self.height = 0
            while 1:
                text, info, value = yield
                y = -self.height
                label = Label(text, align='right', anchor_x='right',
                    anchor_y='top', x=0, y=y, font_name='Prototype')
                self.height += label.element.content_height
                self.add(label)
                if info:
                    self.add(Label(info, align='left', anchor_x='left',
                        anchor_y='top', x=2, y=y, font_name='Prototype'))
                else:
                    self.bg = Bargraph((80, 10), value, position=(2, y-16))
                    if value < .3:
                        self.bg.color = (200, 100, 100)
                    elif value < .7:
                        self.bg.color = (200, 200, 100)
                    else:
                        self.bg.color = (100, 200, 100)
                    self.add(self.bg)

        adder = add_info()
        adder.next()
        add_info = lambda *a: adder.send(a)

        zone = model.game.moon.zones[active_zone]

        add_info('Zone', self.descr[active_zone], None)
        add_info('Provides:', ', '.join(zone.provides), None)
        add_info('Requires:', ', '.join(zone.requirements), None)
        for n in zone.store:
            add_info('%s:' % n.title(), '', zone.store[n] / 10.)
        # add_info('Privileged Rebellious:', '', zone.privileged.rebellious)
        # add_info('Servitor Rebellious:', '', zone.servitor.rebellious)
        # add_info('Privileged Willing:', '', zone.privileged.willing)
        # add_info('Servitor Willing:', '', zone.servitor.willing)
        add_info('Faction Status:', zone.faction.state_description, '')

        self.anchor_y = -self.height

if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
