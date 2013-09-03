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
            Display())


class Display(Layer):
    is_event_handler = True

    def __init__(self):
        super(Display, self).__init__()
        w, h = director.get_window_size()

        self.turn_label = Label('', color=(0, 0, 0, 255), x=0, y=h, anchor_y='top')
        self.add(self.turn_label)
        self.threat_label = Label('', color=(0, 0, 0, 255), x=0, y=h-20, anchor_y='top')
        self.add(self.threat_label)
        self.visible_label = Label('', color=(0, 0, 0, 255), x=0, y=h-40, anchor_y='top')
        self.add(self.visible_label)
        self.update()

        self.industry = pyglet.resource.image('industry.png')
        self.logistics = pyglet.resource.image('logistics.png')
        self.military = pyglet.resource.image('military.png')

        self.add(Sprite(self.industry, position=(w//2, h//2)))

        self.end_turn = Sprite('end turn button.png', position=(w-32, h-32))
        self.add(self.end_turn)

    def update(self):
        self.turn_label.element.text = 'Turn: %d' % model.game.turn
        self.threat_label.element.text = 'Threat: %d' % model.game.threat
        self.visible_label.element.text = 'Visibility: %d' % model.game.player.visibility

    def on_mouse_press(self, x, y, button, modifiers):
        if self.end_turn.get_rect().contains(x, y):
            self.on_new_turn()

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

if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)

    model.game = model.Game()
    model.game.json_savefile('/tmp/overview_save.json')
    director.run(Overview())
