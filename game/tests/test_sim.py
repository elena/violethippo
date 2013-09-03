import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
from gamelib.plans.base import Plan

class FakeUI:
    class SIGNAL_GAMEOVER(Exception):
        pass

    def __init__(self, savedir):
        self.savedir = savedir
        self.logging_begin(savedir)
        self.messages = []

    def msg(self, msg, *args):
        if args:
            print msg % args
        else:
            print msg
        self.messages.append((msg, args))

    def logging_begin(self, sdir):
        if os.path.exists(sdir):
            shutil.rmtree(sdir)
        os.mkdir(sdir)


def savedir(test):
    @functools.wraps(test)
    def wrapper(*args, **kw):
        tempdir = os.path.join('save.test', test.__name__)
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        os.makedirs(tempdir)
        r = test(tempdir, *args, **kw)
        shutil.rmtree(tempdir)
        return r
    return wrapper


@savedir
def test_model_construction(savedir):
    print 'HAI', savedir
    g = model.Game()
    random.seed(1)

    g.moon.zones.append(model.Zone('Industry', []))

    f = g.moon.zones[0].faction = model.Faction('baddies', threat=.25, size=.1,
        informed=.2, smart=.1, loyal=.5, rich=.5, buffs=['military',
        'military', 'fanatic'])

    r = model.Resistance('managers', size=.2, informed=.1, smart=.1, loyal=.3,
        rich=.4, buffs=['leader'], visibility=.1,
        modus_operandi=Plan.TYPE_ESPIONAGE)
    g.moon.zones[0].resistance_groups.append(r)

    r = model.Resistance('workers', size=.4, informed=.2, smart=.1, loyal=.2,
        rich=.1, buffs=['grunts'], visibility=.4,
        modus_operandi=Plan.TYPE_VIOLENCE)
    g.moon.zones[0].resistance_groups.append(r)

    ui = FakeUI(savedir)
    g.update(ui)

    g2 = g.json_loadfile(savedir)
    g2.json_savefile(savedir, 'save.json.verify')
    # diffing save.json and save.json.verify should be equal...

    n = os.path.join(savedir, 'save.json')
    with open(n) as f1, open(n + '.verify') as f2:
        assert f1.read() == f2.read()

    g.update(ui)
    g.update(ui)
    g.update(ui)
