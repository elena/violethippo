# -*- coding: utf-8 -*-
'''
TODO:
- At the top of the screen is the total threat bar, this is what the player is
  trying to lower. It perhaps should have three (named/labeled?) segements,
  one for each zone.
- Below that is the current “time to being arrested” bar for the player, which
  is related to this zone (they have a separate visible for each zone)
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
- Not shown here: the zone has a servitor and privileged section, with a
  clickable area for the faction and for each cohort, which will show whatever
  info is known about them. I think this means the illustration needs to take
  up more space, but that should be ok.
- The city is also shown, which is important, as it sets our context.
'''

import os
import pyglet
import random

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer, PythonInterpreterLayer
from cocos.text import Label
from cocos.sprite import Sprite

from gamelib import model, player_orders
from ninepatch import LabelNinepatch

from dialog import ChoiceLayer
from debug import DebugLayer


def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(ColorLayer(245, 244, 240, 255),
            Fixed())

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

        self.player_action_buts = []

    def on_enter(self):
        super(Fixed, self).on_enter()
        if self.initialised:
            return

        # ok, do we need to finish creating the game?
        if model.game.turn == 0:
            # prior to first turn
            model.game.init_new_game(self)

        w, h = director.get_window_size()

        # now it's safe to show information about the game
        self.threat_label = Label('', color=(0, 0, 0, 255), x=0, y=h, anchor_y='top')
        self.add(self.threat_label)
        self.visible_label = Label('', color=(0, 0, 0, 255), x=0, y=h-20, anchor_y='top')
        self.add(self.visible_label)

        self.turn_label = Label('Turn: %d\nActivitiy Points: %d',
            multiline=True, color=(0, 0, 0, 255), x=w-200, y=h, width=200,
            anchor_x='right', anchor_y='top')
        self.add(self.turn_label)

        self.end_turn = Sprite('end turn button.png', position=(w-32, h-32))
        self.add(self.end_turn)

        self.info = Info()
        self.add(self.info)

        self.zone = Zone()
        self.add(self.zone)

        self.update_info()

        # now we're done
        self.initialised = True

    def update_info(self):
        self.turn_label.element.text = 'Turn: %d\nActivity_points: %d\nHideout: %s' % (
            model.game.turn, model.game.player.activity_points, model.game.player.hideout or 'Not Chosen')
        assert(len(model.game.moon.zones) == 3)
        zone1 = model.game.moon.zones[model.INDUSTRY]
        zone2 = model.game.moon.zones[model.LOGISTICS]
        zone3 = model.game.moon.zones[model.MILITARY]
        self.threat_label.element.text = 'Threat: %d | %d | %d' % (zone1.faction.threat * 100, zone2.faction.threat * 100, zone3.faction.threat * 100)
        self.visible_label.element.text = 'Hidden: %d | %d | %d' % ((1-zone1.player_found)*100, (1-zone2.player_found)*100, (1-zone3.player_found)*100)
        self.info.display_zone(self.zone.mode)

        if not model.game.player.hideout:
            # show Establish/Move hideout button only
            self.end_turn.visible = False
        else:
            # enable turn button and all the player actions
            self.end_turn.visible = True

        # update player action buttons
        w, h = director.get_window_size()
        for but in self.player_action_buts:
            self.remove(but)
        self.player_action_buts = []
        y = 560
        for order in player_orders.all:
            cost = order.cost(self.zone)
            if cost is None:
                continue
            b = LabelNinepatch('border-9p.png', Label('%dAP: %s' % (cost,
                order.label), x = 730, y=y, color=(0, 0, 0, 255),
                anchor_x='left', anchor_y='bottom'))
            y -= 40
            b.order = order
            self.player_action_buts.append(b)
            self.add(b)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.end_turn.get_rect().contains(x, y):
            self.on_new_turn()
            return True         # event handled
        for action in self.player_action_buts:
            if action.rect.contains(x, y):
                action.order.execute(self)
                return True         # event handled

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

    class SIGNAL_GAMEOVER(Exception):
        pass

    def on_new_turn(self):
        try:
            model.game.update(self)
        except self.SIGNAL_GAMEOVER:
            pass
        if model.game.player.hideout:
            self.zone.switch_zone_to(model.game.player.hideout)
        self.update_info()


class Zone(Layer):
    is_event_handler = True

    ZONE_BUTTONS = {
        model.INDUSTRY: {model.LOGISTICS: (30, 95), model.MILITARY: (70, 15)},
        model.LOGISTICS: {model.INDUSTRY: (45, 530), model.MILITARY: (70, 15)},
        model.MILITARY: {model.INDUSTRY: (45, 530), model.LOGISTICS: (15, 450)},
    }

    def __init__(self):
        super(Zone, self).__init__()
        w, h = director.get_window_size()
        self.mode = model.INDUSTRY

        self.zone_images = {
            model.INDUSTRY: pyglet.resource.image('industry.png'),
            model.LOGISTICS: pyglet.resource.image('logistics.png'),
            model.MILITARY: pyglet.resource.image('military.png')
        }

        self.active = Sprite(self.zone_images[model.INDUSTRY],
            position=(75+256, 75+256))
        self.add(self.active)

        self.but_faction = Sprite('faction button.png', position=(270, 460),
            anchor=(0, 0))
        self.add(self.but_faction, z=1)

        self.but_privileged = Sprite('privileged button.png',
            position=(85, 361), anchor=(0, 0))
        self.add(self.but_privileged, z=1)

        self.but_servitors = Sprite('servitors button.png',
            position=(340, 200), anchor=(0, 0))
        self.add(self.but_servitors, z=1)

        priv_locs = [(340, 385), (440, 400)]
        serv_locs = [(120, 280), (220, 220), (300, 285), (420, 275)]
        self.resistance_locations = {
            (model.INDUSTRY, 'privileged'): shuffled(priv_locs),
            (model.LOGISTICS, 'privileged'): shuffled(priv_locs),
            (model.MILITARY, 'privileged'): shuffled(priv_locs),
            (model.INDUSTRY, 'servitor'): shuffled(serv_locs),
            (model.LOGISTICS, 'servitor'): shuffled(serv_locs),
            (model.MILITARY, 'servitor'): shuffled(serv_locs),
        }

        self.zone_buts = {
            model.INDUSTRY: Sprite('industry button.png', anchor=(0, 0)),
            model.LOGISTICS: Sprite('logistics button.png', anchor=(0, 0)),
            model.MILITARY: Sprite('military button.png', anchor=(0, 0)),
        }

        self.resistance_buts = []

        self.add(self.zone_buts[model.INDUSTRY])
        self.add(self.zone_buts[model.LOGISTICS])
        self.add(self.zone_buts[model.MILITARY])

    def on_enter(self):
        super(Zone, self).on_enter()
        # self.parent.msg('setting zone based on %s'%model.game.player.hideout)
        if model.game.player.hideout:
            self.parent.msg('setting zone to %s'%model.game.player.hideout)
            self.mode = None
            self.switch_zone_to(model.game.player.hideout)
        else:
            self.mode = None
            self.switch_zone_to(model.LOGISTICS)

    def switch_zone_to(self, active_zone):
        if self.mode == active_zone:
            return

        for but in self.resistance_buts:
            self.remove(but)

        # move buttons around
        self.zone_buts[active_zone].position = (730, 630)
        for other, location in self.ZONE_BUTTONS[active_zone].items():
            self.zone_buts[other].position = location

        self.mode = active_zone
        self.active.image = self.zone_images[active_zone]
        self.parent.update_info()
        self.parent.info.hide_info()

        self.resistance_buts = []
        zone = model.game.moon.zones[active_zone]
        for name, l in [('privileged', zone.privileged.resistance_groups),
                ('servitor', zone.servitor.resistance_groups)]:
            for n, group in enumerate(l):
                position = self.resistance_locations[active_zone, name][n]
                but = Sprite('resistance button.png', position=position, anchor=(0, 0))
                but.resistance_group = group
                self.resistance_buts.append(but)
                self.add(but, 2)

    def on_mouse_press(self, x, y, button, modifiers):
        for zone, but in self.zone_buts.items():
            if zone == self.mode:
                continue
            if but.get_rect().contains(x, y):
                self.switch_zone_to(zone)
                return True         # event handled

        # check other info display buttons
        if self.but_faction.get_rect().contains(x, y):
            self.parent.info.show_faction(self.mode)
            return True         # event handled
        zone = model.game.moon.zones[self.mode]
        if self.but_privileged.get_rect().contains(x, y):
            self.parent.info.show_cohort(zone.privileged)
            return True         # event handled
        if self.but_servitors.get_rect().contains(x, y):
            self.parent.info.show_cohort(zone.servitor)
            return True         # event handled
        for but in self.resistance_buts:
            if but.get_rect().contains(x, y):
                self.parent.info.show_resistance(but.resistance_group)
                return True         # event handled


class Info(Layer):
    is_event_handler = True
    def __init__(self):
        super(Info, self).__init__()

        self.anchor = (0, 0)
        self.x = 660
        self.y = 10

        self.zone_label = Label('', multiline=True, color=(0, 0, 0, 255),
            width=350, anchor_x='left', anchor_y='bottom', x=10, y=10)
        self.add(self.zone_label)

        self.info_label = Label('', multiline=True, color=(0, 0, 0, 255),
            width=350, anchor_x='left', anchor_y='bottom', x=10, y=250)
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
        """When we click on the faction button we want to see what we know
        about the faction here, which is limited unless we’ve gathered intel
        through a recent Order or Resistance Plan

        Contents: Name of faction, Name of leader, brief description; current
        status (need a process here, but if you have no special intel, we
        should know only what the most damaged stat is, eg. “Smarts impaired”;
        balance may indicate we need rough info like this on all, but ideally
        not; When we have intel we should see a clear indication of the stats,
        perhaps as value *10 with one decimal place?)
        """
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
        """This pane shows some basic Resistance Group info, and then lists
        the Plans they are currently working on, briefly. clicking on the
        Group or the Plans lets you investigate further.

        Contents: Resistance Group name, modus operandi, perhaps their Trust
        of the player if that is used/useful; list of Plans, showing at least
        a name and progress bar towards carrying them out (full means they are
        going ahead this turn).

        Out: click outside the pane?
        Resistance Info: summon Resistance Info Pane (over this one)
        Resistance Plan: summon Resistance Plan Pane (over this one)
        """
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
        """The information about cohorts is more readily available (walk the
        streets, listen to the chatter) so we should get pretty solid
        indicators of how the people are feeling.

        Contents: current stats (Size, Liberty, Quality of Life, Cash)
        probably in x10 on decimal place; size should perhaps be a word
        instead - we don’t expect it to change, I think - it is more a
        reflection of inertia. I don’t think we want to see the Willingness,
        Rebelliousness, and Efficiency directly, but perhaps a word would be
        ok. We want the player to know what is going on, but not have too
        close a view of the numbers.
        """
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

    def display_zone(self, active_zone):
        """It would be good not to have to summon a
        pane for this, but instead to have room on the screen all the time
        (even if it can get buried by other panes).

        Contents: Brief description of zone. State of production (what it last
        produced, state of inputs this turn, notes of supply shortfalls,
        alerts of low willingness and high rebelliousness, really summarised
        status for the faction along the lines of “strong”, “damaged”,
        “shaky”, “vulnerable”, “destroyed”, and the level of alert to player
        and resistance activity)."""
        zone = model.game.moon.zones[active_zone]
        # if self.active_info == zone:
        #     self.hide_info()
        #     return
        # self.active_info = zone
        text = []
        descr = dict(
            industry='produces goods and food',
            logistics='transports to and from planet',
            military='provides force and stability',
        )
        text.append('Zone ' + descr[active_zone])
        text.append('Provides: %s' % (', '.join(zone.provides), ))
        text.append('Requires: %s' % (', '.join(zone.requirements), ))
        text.append('Store:\n    %s' % ('\n    '.join('%s: %d%%' % (n, v*10) for (n,v) in zone.store.items()), ))
        text.append('Efficiency: %.1f' % (zone.privileged.efficiency * 10))
        text.append('Willingness: %.1f' % (zone.servitor.willing * 10))
        text.append('Rebellious: %.1f & %.1f' % (zone.privileged.rebellious * 10,
            zone.servitor.rebellious * 10))
        text.append('Faction Status: %s' % zone.faction.state_description)
        self.zone_label.element.text = '\n'.join(text)


if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
