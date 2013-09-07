# -*- coding: utf-8 -*-
import os
import pyglet
import random

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer, PythonInterpreterLayer
from cocos.text import Label
from cocos.sprite import Sprite
from cocos.rect import Rect

from ninepatch import LabelNinepatch

from gamelib import model, player_orders

from dialog import ChoiceLayer, OkLayer
from debug import DebugLayer
from widgets import Button, TextButton, Bargraph, MultipleBargraph

START_TEXT = """When you were young they came from the stars,
adding a new moon to the sky - a moon of steel.

Although there were only handful of them,
the guns on their fortress brought them victory.

Now the time has come for you to strike back.

Travel to their lair and coordinate the resistance
there, deafeating the invaders, and making this
a moon of blood.
"""

GENERAL_HELP_TEXT = """Defeat the ruling factions of each zone
before getting caught.

Each turn help the rebels to enact plans
(using activity points) to weaken the factions.

You are stronger where your hideout is located.
"""

def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(Sprite('bg.jpg', position=(512, 384)),
            Fixed())


class Fixed(Layer):   # "display" needs to be renamed "the one with buttons and info"
    is_event_handler = True
    order_x = 200
    order_y = 485

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
        bar_label_x = 240*2
        bar_graph_x = 305
        bar_label_y = 372*2
        bar_graph_y = 365
        self.add(Label('Faction Strength: ', x=bar_label_x, y=bar_label_y,
                       anchor_y='top', font_name='Prototype'), 'threat')
        self.add(MultipleBargraph((200, 8), (.2, .2, .2),
            position=(bar_graph_x, bar_graph_y),
            style='solid', colors=[(100, 100, 100), (200, 200, 100),
            (200, 100, 100)]), name='threat_graph')

        self.add(Label('Risk of Capture: ', x=bar_label_x, y=bar_label_y-20,
                       anchor_y='top', font_name='Prototype'))
        self.add(MultipleBargraph((200, 8), (1, 1, 1),
            position=(bar_graph_x, bar_graph_y-10),
            style='solid', colors=[(100, 100, 100), (200, 200, 100),
            (200, 100, 100)]), name='visible_graph')

        turn_x = 840
        turn_y = 698
        self.add(Label('', multiline=True, x=turn_x, y=turn_y, width=200,
            anchor_x='left', anchor_y='bottom', font_name='Prototype'),
            name='turn_label')

        end_turn = Button('end turn button.png', (w-64, h-64), None,
            self.on_new_turn)
        self.buttons.append(end_turn)
        self.add(end_turn, name='end_turn')

        help = Button('help.png', (16, 16), None, self.on_help)
        self.buttons.append(help)
        self.add(help, name='help')

        self.info = Details()
        self.info.position = (335, h-25)
        self.add(self.info)

        self.zinfo = ZoneInfo()
        self.zinfo.position = (150, 185)
        self.add(self.zinfo)

        self.zone = Zone()
        self.add(self.zone, z=-1)

        order_label = Label('Choose your actions for this turn: ',
                            position=(self.order_x, self.order_y+40),
                            color=(255,255,255,255), font_name='Prototype')
        self.add(order_label)

        # order_help = Label(GENERAL_HELP_TEXT, position=(30, 320),
        #                    multiline=True, color=(150, 150, 150, 255),
        #                    font_size =10,
        #                    font_name='Prototype', width=400)
        # self.add(order_help)

        self.update_info()

        # now we're done
        self.initialised = True

        if model.game.turn == 1:
            self.ask_ok('Fight Back', lambda *a: None, explanation=START_TEXT,
                width=500)

    def update_info(self):
        free = ''
        if model.game.player.free_order:
            free = ' + free'
        self.get('turn_label').element.text = 'Turn: %d\nHideout: %s'\
            '\nActivity Points:  %d%s' % (model.game.turn,
                model.game.player.hideout or 'Not Chosen',
                model.game.player.activity_points, free
            )

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
            offset = 75
            zone_x = {
                'industry': self.zone.zone1_x+offset,
                'logistics': self.zone.zone2_x+offset,
                'military': self.zone.zone3_x+offset,
            }
            home_logo = Sprite('icon-home.png', position=
                (zone_x[model.game.player.hideout], self.zone.y))
            self.add(home_logo)

        # remove old player order buttons
        for but in list(self.buttons):
            # player order buttons have an 'order' attribute
            if hasattr(but, 'order'):
                self.remove(but)
                self.buttons.remove(but)

        # add appropriate player order buttons
        x = self.order_x+10
        y = self.order_y

        for order in player_orders.all:
            cost = order.cost(self.zone)
            if cost is None:
                continue
            b = TextButton(' %s (%dAP) ' % (order.label, cost), (x, y), order,
                self.on_player_order, color=(240, 240, 240, 255))
            b.order = order
            #x += int(b.label.element.content_height + 20)
            y += int(b.label.element.content_height-60)
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
            self.zone.switch_zone_to(self.zone.get(model.game.player.hideout))
        self.update_info()

    def on_help(self, button):
        self.ask_ok('Help', lambda *a: None, GENERAL_HELP_TEXT)

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

    def ask_choice(self, title, choices, callback, explanation=None, width=400):
        '''A player order wants us to ask the user to make a choice.

        We callback the callback with (self, choice from the list). Or not.
        '''
        self.add(ChoiceLayer(title, choices, callback, explanation, width), z=1)

    def ask_ok(self, title, callback, explanation=None, width=400):
        self.add(OkLayer(title, callback, explanation, width), z=1)

    def msg(self, message, *args):
        self.console.write(message % args)

    def graph(self, graph, line, turn, value):
        pass


class Zone(Layer):
    is_event_handler = True

    x = 485
    y = 640
    s = 150
    zone1_x, zone2_x, zone3_x = x, x+s, x+s*2

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

        w, h = director.get_window_size()

        self.active = Sprite(self.zone_images[model.INDUSTRY],
            anchor=((-(w-550),
                     -(h-605)))
        )
        self.add(self.active, z=-1)

        self.add(Button('but-ind_off.png', (self.zone1_x, self.y), 'industry',
            self.switch_zone_to), name=model.INDUSTRY)
        self.add(Button('but-log_off.png', (self.zone2_x, self.y), 'logistics',
            self.switch_zone_to), name=model.LOGISTICS)
        self.add(Button('but-mil_off.png', (self.zone3_x, self.y), 'military',
            self.switch_zone_to), name=model.MILITARY)

    def on_enter(self):
        super(Zone, self).on_enter()
        # self.parent.msg('setting zone based on %s'%model.game.player.hideout)
        if model.game.player.hideout:
            self.parent.msg('setting zone to %s'%model.game.player.hideout)
            self.mode = None
            self.switch_zone_to(self.get(model.game.player.hideout))
        else:
            self.mode = None
            self.switch_zone_to(self.get(model.LOGISTICS))

    def switch_zone_to(self, but):
        if self.mode == but.info:
            return

        active_zone = but.info
        for name in 'industry logistics military'.split():
            but = self.get(name)
            nam = name[:3]
            if name == active_zone:
                but.image = pyglet.resource.image('but-%s_on.png' % nam)
            else:
                but.image = pyglet.resource.image('but-%s_off.png' % nam)
        self.mode = active_zone

        self.active.image = self.zone_images[active_zone]
        self.parent.update_info()
        self.parent.info.hide_info()

        # clear out unnecessary butts
        for name in list(self.children_names):
            if name in (model.INDUSTRY, model.LOGISTICS, model.MILITARY):
                continue
            but = self.get(name)
            if hasattr(but, 'on_click'):
                self.remove(but.label_ob)
                self.remove(name)

        zone = model.game.moon.zones[active_zone]
        self.buttons = []
        def add_button():
            y = 758
            x = 10
            while 1:
                indent, but, label = yield
                y -= but.image.height
                but.position = (x + indent, y)
                if isinstance(but.info, str):
                    name = but.info
                else:
                    name = but.info.name
                self.add(but, z=1, name=name)
                lx = x + indent + but.image.width + 10
                l = Label(label, position=(lx, y+8), color=(255,255,255,255),
                    font_name='Prototype')
                l.rect = Rect(l.x, l.y, l.element.content_width, l.element.content_height)
                self.add(l)
                but.label_ob = l

        adder = add_button()
        adder.next()

        adder.send((10, Button('icon-priv_off.png', (0, 0), 'privileged',
            self.on_show_info, img_prefix='icon-priv'), 'Privileged Cohort'))
        for group in zone.privileged.resistance_groups:
            label = group.name # '%s %r' % (group.name, group.plans)
            adder.send((20, Button('icon-pres_off.png', (0, 0), group,
                self.on_show_info, img_prefix='icon-pres'), label))
        adder.send((10, Button('icon-serv_off.png', (0, 0), 'servitors',
            self.on_show_info, img_prefix='icon-serv'), 'Servitor Cohort'))
        for group in zone.servitor.resistance_groups:
            label = group.name # '%s %r' % (group.name, group.plans)
            adder.send((20, Button('icon-sres_off.png', (0, 0), group,
                self.on_show_info, img_prefix='icon-sres'), label))

    def on_mouse_press(self, x, y, button, modifiers):
        for z, but in self.children:
            if not hasattr(but, 'on_click'):
                continue
            if but.info == self.mode:
                continue
            if but.get_rect().contains(x, y):
                but.on_click(but)
                return True         # event handled
            if hasattr(but, 'label_ob') and but.label_ob.rect.contains(x, y):
                but.on_click(but)
                return True         # event handled

    def on_show_info(self, but):
        zone = model.game.moon.zones[self.mode]
        for name, ob in self.children_names.items():
            if hasattr(ob, 'img_prefix'):
                ob.image = pyglet.resource.image('%s_off.png' % ob.img_prefix)
        if but.info == 'faction':
            self.parent.info.show_faction(self.mode)
            # self.get('faction').image = pyglet.resource.image('icon-fact_on.png')
        elif but.info == 'privileged':
            self.parent.info.show_cohort(zone.privileged)
            self.get('privileged').image = pyglet.resource.image('icon-priv_on.png')
        elif but.info == 'servitors':
            self.parent.info.show_cohort(zone.servitor)
            self.get('servitors').image = pyglet.resource.image('icon-serv_on.png')
        else:
            self.parent.info.show_resistance(but.info)
            self.get(but.info.name).image = pyglet.resource.image('%s_on.png' % but.img_prefix)


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
    active_info = None

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
            ('Size:', None, faction.buffed('size')),
            ('Informed:', None, faction.buffed('informed')),
            ('Smart:', None, faction.buffed('smart')),
            ('Loyal:', None, faction.buffed('loyal')),
            ('Rich:', None, faction.buffed('rich')),
            ('Buffs:', ', '.join(faction.buffs), None),
            ('Threat:', None, faction.buffed('threat')),
            ('Alert:', None, faction.buffed('alert')),
        ])

    def show_resistance(self, group):
        if self.active_info == group:
            self.hide_info()
            return
        self.active_info = group
        self.show_info([
            ('Name:', group.name, None),
            ('Size:', None, group.buffed('size')),
            ('Informed:', None, group.buffed('informed')),
            ('Smart:', None, group.buffed('smart')),
            ('Rich:', None, group.buffed('rich')),
            ('Loyal:', None, group.buffed('loyal')),
            ('Visibility:', None, group.buffed('visibility')),
            ('Buffs:', ', '.join(group.buffs), None),
            ('Plans:', str(len(group.plans)), None),
            ('Modus Operandi:', group.modus_operandi, None),
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
            ('Size:', None, cohort.buffed('size')),
            ('Liberty:', None, cohort.buffed('liberty')),
            ('Quality of Life:', None, cohort.buffed('quality_of_life')),
            ('Cash:', None, cohort.buffed('cash')),
            output,
            ('Rebelliousness:', None, cohort.rebellious),
        ])

    def show_info(self, info):
        for z, child in list(self.children):
            self.remove(child)

        packer = self.packer()
        for row in info:
            packer(*row)

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

        status_color = {
            'strong':     (170, 0, 0, 255),
            'battered':   (170, 50, 0, 255),
            'shaky':      (170, 100, 0, 255),
            'vulnerable': (200, 170, 0, 255),
            'turmoil':    (180, 255, 0, 255),
            'destroyed':  (0, 170, 0, 255),
        }
        desc = zone.faction.state_description
        status = TextButton('%s: %s  ' % (zone.faction.name, desc.upper()),
            (500, -15), None, None, color=status_color[desc])
        self.add(status)

        packer = self.packer()
        # packer('Faction Status:', zone.faction.state_description, None)
        packer('Provides:', ', '.join(zone.provides), None)
        packer('Requires:', ', '.join(zone.requirements), None)
        for n in zone.store:
            packer('%s:' % n.title(), None, zone.store[n] / 10.)
        # packer('Privileged Rebellious:', None, zone.privileged.rebellious)
        # packer('Servitor Rebellious:', None, zone.servitor.rebellious)
        # packer('Privileged Willing:', None, zone.privileged.willing)
        # packer('Servitor Willing:', None, zone.servitor.willing)
        packer('Zone', self.descr[active_zone], None)
        self.width = self.max_x - self.min_x

if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()
    pyglet.resource.add_font('Prototype.ttf')

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
