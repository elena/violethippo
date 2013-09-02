import os
import sys
import random
import shlex
import shutil
import time

sys.path.append('..')

from gamelib import model,player_orders,group_plans


class FakeUI:
    class SIGNAL_GAMEOVER(Exception):
        pass

    def __init__(self, savedir):
        self.savedir = savedir
        self.logging_begin(savedir)
        self.messages = []

    def msg(self, msg, *args):
        self.messages.append((msg, args))

    def logging_begin(self, sdir):
        if os.path.exists(sdir):
            shutil.rmtree(sdir)
        os.mkdir(sdir)


def test_model_construction():
    g = model.Game()
    random.seed(1)

    g.moon.zones.append(model.Zone('Industry'))

    f = g.moon.zones[0].faction = model.Faction('baddies')
    f.threat = .25
    f.size = .1
    f.informed = .2
    f.smart = .1
    f.loyal = .5
    f.rich = .5
    f.buffs = ['military', 'military', 'fanatic']

    r = model.Resistance('managers')
    f.size = .2
    f.informed = .1
    f.smart = .1
    f.loyal = .3
    f.rich = .4
    f.buffs = ['leader']
    g.moon.zones[0].resistance_groups.append(r)

    r = model.Resistance('workers')
    f.size = .4
    f.informed = .2
    f.smart = .1
    f.loyal = .2
    f.rich = .1
    f.buffs = ['grunts']
    g.moon.zones[0].resistance_groups.append(r)

    c = g.moon.zones[0].cohorts[0]
    c.size = .1
    c.liberty = .4
    c.quality_of_life = .2
    c.cash = .4

    c = g.moon.zones[0].cohorts[1]
    c.size = .4
    c.liberty = .2
    c.quality_of_life = .1
    c.cash = .2

    ui = FakeUI('save.test')
    g.update(ui)

    g2 = g.json_loadfile(ui.savedir)
    g2.json_savefile(ui.savedir, 'save.json.verify')
    # diffing save.json and save.json.verify should be equal...

    with open('save.test/save.json') as f1, open('save.test/save.json.verify') as f2:
        assert f1.read() == f2.read()

    g.update(ui)
    g.update(ui)
    g.update(ui)

    shutil.rmtree('save.test')
