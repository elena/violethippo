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

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite


from gamelib import model


class Overview(Scene):
    def __init__(self):
        super(Overview, self).__init__(ColorLayer(245, 244, 240, 255),
            Fixed())


class Fixed(Layer):   # "display" needs to be renamed "the one with buttons and info"
    is_event_handler = True

    def __init__(self):
        super(Fixed, self).__init__()
        w, h = director.get_window_size()

        self.threat_label = Label('', color=(0, 0, 0, 255), x=0, y=h, anchor_y='top')
        self.add(self.threat_label)
        self.visible_label = Label('', color=(0, 0, 0, 255), x=0, y=h-20, anchor_y='top')
        self.add(self.visible_label)

        self.turn_label = Label('', color=(0, 0, 0, 255), x=w-64, y=h-32,
            anchor_x='right', anchor_y='top')
        self.add(self.turn_label)

        self.update()

        self.zone = Zone()
        self.add(self.zone)

        self.info = Info()
        self.add(self.info)

        self.end_turn = Sprite('end turn button.png', position=(w-32, h-32))
        self.add(self.end_turn)

    def update(self):
        self.turn_label.element.text = 'Turn: %d' % model.game.turn
        self.threat_label.element.text = 'Threat: %d' % model.game.threat
        self.visible_label.element.text = 'Visibility: %d' % model.game.player.visibility

    def on_mouse_press(self, x, y, button, modifiers):
        if self.end_turn.get_rect().contains(x, y):
            self.on_new_turn()
            return True         # event handled

    def msg(self, message, *args):
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

        self.industry = pyglet.resource.image('industry.png')
        self.logistics = pyglet.resource.image('logistics.png')
        self.military = pyglet.resource.image('military.png')

        self.active = Sprite(self.industry, position=(75+256, 75+256))
        self.add(self.active)

        self.but_industry = Sprite('industry button.png', position=(30, 600), anchor=(0, 0))
        self.but_logistics = Sprite('logistics button.png', position=(230, 600), anchor=(0, 0))
        self.but_military = Sprite('military button.png', position=(430, 600), anchor=(0, 0))

        self.add(self.but_industry)
        self.add(self.but_logistics)
        self.add(self.but_military)


    def on_mouse_press(self, x, y, button, modifiers):
        if self.but_industry.get_rect().contains(x, y):
            self.mode = self.MODE_INDUSTRY
            self.active.image = self.industry
            return True         # event handled
        if self.but_logistics.get_rect().contains(x, y):
            self.mode = self.MODE_LOGISTICS
            self.active.image = self.logistics
            return True         # event handled
        if self.but_military.get_rect().contains(x, y):
            self.mode = self.MODE_MILITARY
            self.active.image = self.military
            return True         # event handled


class Info(Layer):
    def __init__(self):
        super(Info, self).__init__()

        self.anchor = (0, 0)
        self.x = 660
        self.y = 10

        self.bg = ColorLayer(200, 198, 190, 255, width=350, height=680)
        self.add(self.bg)


if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
