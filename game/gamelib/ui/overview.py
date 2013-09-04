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
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite
from cocos.rect import Rect
from cocos.cocosnode import CocosNode

from gamelib import model, player_orders
import ninepatch


def shuffled(l):
    l = list(l)
    random.shuffle(l)
    return l


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(ColorLayer(245, 244, 240, 255),
            Fixed())


class ChoiceLayer(Layer):
    is_event_handler = True
    def __init__(self, title, choices, callback):
        super(ChoiceLayer, self).__init__()
        self.callback = callback
        self.add(ColorLayer(0, 0, 0, 200))
        w, h = director.get_window_size()

        self.add(Label(title, color=(200, 200, 200, 255), x=w//2,
            anchor_x='center', y=h-128, font_size=40))

        self.choice_buts = []
        y = h-256
        for choice in choices:
            but = Label(choice, color=(200, 200, 200, 255), x=w//2,
                anchor_x='center', y=y, font_size=30)
            y -= 64
            self.add(but)
            but.rect = Rect(but.element.x, but.element.y,
                but.element.content_width, but.element.content_height)
            self.choice_buts.append(but)

    def on_mouse_press(self, x, y, button, modifiers):
        for but in self.choice_buts:
            if but.rect.contains(x, y):
                self.callback(self.parent, but.element.text)
        self.callback = None
        self.parent.update()
        self.kill()
        return True

    def on_key_press(self, *args):
        self.callback = None
        self.kill()
        return True


class Fixed(Layer):   # "display" needs to be renamed "the one with buttons and info"
    is_event_handler = True

    def __init__(self):
        super(Fixed, self).__init__()
        w, h = director.get_window_size()

        self.threat_label = Label('', color=(0, 0, 0, 255), x=0, y=h, anchor_y='top')
        self.add(self.threat_label)
        self.visible_label = Label('', color=(0, 0, 0, 255), x=0, y=h-20, anchor_y='top')
        self.add(self.visible_label)

        self.turn_label = Label('Turn: %d\nActivitiy Points: %d',
            multiline=True, color=(0, 0, 0, 255), x=w-64, y=h, width=140,
            anchor_x='right', anchor_y='top')
        self.add(self.turn_label)

        self.end_turn = Sprite('end turn button.png', position=(w-32, h-32))
        self.add(self.end_turn)

        self.player_action_buts = []
        self.update()

        self.info = Info()
        self.add(self.info)

        self.zone = Zone()
        self.add(self.zone)

    def update(self):
        self.turn_label.element.text = 'Turn: %d\nActivity_points: %d\nHideout: %s' % (
            model.game.turn, model.game.player.activity_points, model.game.player.hideout or 'Not Chosen')
        self.threat_label.element.text = 'Threat: %d' % model.game.threat
        self.visible_label.element.text = 'Visibility: %.1f' % model.game.player.visibility

        if not model.game.player.hideout:
            # show Establish/Move hideout button only
            self.end_turn.visible = False
        else:
            # enable turn button and all the player actions
            self.end_turn.visible = True

        w, h = director.get_window_size()
        for but in self.player_action_buts:
            self.remove(but)
        self.player_action_buts = []
        y = h - 128
        for order in player_orders.all:
            cost = order.cost()
            if cost is None:
                continue
            b = LabelNinepatch('border-9p.png', Label('%dAP: %s' % (cost,
                order.label), x = w - 200, y=y, color=(0, 0, 0, 255),
            anchor_x='left', anchor_y='bottom'))
            y -= 32
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

    def ask_choice(self, title, choices, callback):
        '''A player order wants us to ask the user to make a choice.

        We callback the callback with (self, choice from the list). Or not.
        '''
        self.add(ChoiceLayer(title, choices, callback), z=1)

    def msg(self, message, *args):
        # TODO log this crap in something on-screen
        print message % args

    class SIGNAL_GAMEOVER(Exception):
        pass

    def on_new_turn(self):
        try:
            model.game.update(self)
        except self.SIGNAL_GAMEOVER:
            pass
        self.update()


class Zone(Layer):
    is_event_handler = True

    MODE_INDUSTRY = 'industry'
    MODE_LOGISTICS = 'logistics'
    MODE_MILITARY = 'military'

    def __init__(self):
        super(Zone, self).__init__()
        w, h = director.get_window_size()
        self.mode = self.MODE_INDUSTRY

        self.zone_images = {
            self.MODE_INDUSTRY: pyglet.resource.image('industry.png'),
            self.MODE_LOGISTICS: pyglet.resource.image('logistics.png'),
            self.MODE_MILITARY: pyglet.resource.image('military.png')
        }

        self.active = Sprite(self.zone_images[self.MODE_INDUSTRY],
            position=(75+256, 75+256))
        self.add(self.active)

        self.but_faction = Sprite('faction button.png', position=(0, 200))
        self.active.add(self.but_faction)

        self.but_privileged = Sprite('privileged button.png', position=(-128, 64))
        self.active.add(self.but_privileged)

        self.but_servitors = Sprite('servitors button.png', position=(128, -200))
        self.active.add(self.but_servitors)

        priv_locs = [(60, 164), (160, 64)]
        serv_locs = [(-128, -256), (-100, -200), (-60, -256),
            (160, -64)]
        self.resistance_locations = {
            (self.MODE_INDUSTRY, 'privileged'): shuffled(priv_locs),
            (self.MODE_LOGISTICS, 'privileged'): shuffled(priv_locs),
            (self.MODE_MILITARY, 'privileged'): shuffled(priv_locs),
            (self.MODE_INDUSTRY, 'servitor'): shuffled(serv_locs),
            (self.MODE_LOGISTICS, 'servitor'): shuffled(serv_locs),
            (self.MODE_MILITARY, 'servitor'): shuffled(serv_locs),
        }

        self.but_industry = Sprite('industry button.png', position=(30, 600), anchor=(0, 0))
        self.but_logistics = Sprite('logistics button.png', position=(230, 600), anchor=(0, 0))
        self.but_military = Sprite('military button.png', position=(430, 600), anchor=(0, 0))
        self.resistance_buts = []

        self.add(self.but_industry)
        self.add(self.but_logistics)
        self.add(self.but_military)

    def on_enter(self):
        super(Zone, self).on_enter()
        self.mode = None
        self.switch_zone_to(self.MODE_INDUSTRY)

    def switch_zone_to(self, active_zone):
        if self.mode == active_zone:
            return

        for but in self.resistance_buts:
            self.active.remove(but)

        self.mode = active_zone
        self.active.image = self.zone_images[active_zone]
        self.parent.info.display_zone(active_zone)
        self.parent.info.hide_info()

        self.resistance_buts = []
        zone = model.game.moon.zones[active_zone]
        for name, l in [('privileged', zone.privileged.resistance_groups),
                ('servitor', zone.servitor.resistance_groups)]:
            for n, group in enumerate(l):
                position = self.resistance_locations[active_zone, name][n]
                but = Sprite('resistance button.png', position=position)
                but.resistance_group = group
                self.resistance_buts.append(but)
                self.active.add(but)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.but_industry.get_rect().contains(x, y):
            self.switch_zone_to(self.MODE_INDUSTRY)
            return True         # event handled
        if self.but_logistics.get_rect().contains(x, y):
            self.switch_zone_to(self.MODE_LOGISTICS)
            return True         # event handled
        if self.but_military.get_rect().contains(x, y):
            self.switch_zone_to(self.MODE_MILITARY)
            return True         # event handled

        # faction button is placed relative to the zone image so we need to
        # shift the rect accordingly
        # ALTERNATIVE: just check the relative-to-zone hits from now on, OR
        #              place the faction button absolute...
        x -= self.active.x
        y -= self.active.y
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


class LabelNinepatch(CocosNode):
    def __init__(self, image, around):
        super(LabelNinepatch, self).__init__()
        self.label = around
        self.add(self.label, z=1)
        self.ninepatch = ninepatch.NinePatch(pyglet.resource.image(image))

    def draw(self):
        x, y, w, h = self.ninepatch.draw_around(self.label.element.x,
            self.label.element.y, self.label.element.content_width,
            self.label.element.content_height)
        self.rect = Rect(x, y, w, h)


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
            width=350, anchor_x='left', anchor_y='bottom', x=10, y=500)
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
            'Size: %d' % (faction.size * 10),
            'Informed: %d' % (faction.informed * 10),
            'Smart: %d' % (faction.smart * 10),
            'Loyal: %d' % (faction.loyal * 10),
            'Rich: %d' % (faction.rich * 10),
            'Buffs: %s' % ', '.join(faction.buffs),
            'Threat: %d' % (faction.threat * 10),
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
            'Size: %d' % (group.size * 10),
            'Informed: %d' % (group.informed * 10),
            'Smart: %d' % (group.smart * 10),
            'Rich: %d' % (group.rich * 10),
            'Loyal: %d' % (group.loyal * 10),
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
        self.info_label.element.text = '\n'.join([
            'Cohort: %s' % cohort.__class__.__name__,
            'Size: %d' % (cohort.size * 10),
            'Liberty: %d' % (cohort.liberty * 10),
            'Quality of Life: %d' % (cohort.quality_of_life * 10),
            'Cash: %d' % (cohort.cash * 10),
            'Willingness: %d' % (cohort.willing * 10),
            'Rebelliousness: %d' % (cohort.rebellious * 10),
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
        if self.active_info == zone:
            self.hide_info()
            return
        self.active_info = zone
        text = []
        descr = dict(
            industry='produces goods and food',
            logistics='transports to and from planet',
            military='provides force and stability',
        )
        text.append('Zone ' + descr[active_zone])
        text.append('Provides: %s' % (', '.join(zone.provides), ))
        text.append('Requires: %s' % (', '.join(zone.requirements), ))
        text.append('Store: %s' % (', '.join('%s: %s' % i for i in zone.store.items()), ))
        text.append('Willingness: %d & %d' % (zone.privileged.willing * 10,
            zone.servitor.willing * 10))
        text.append('Rebellious: %d & %d' % (zone.privileged.rebellious * 10,
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
