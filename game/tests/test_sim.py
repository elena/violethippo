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
        if not kw.get('leave_my_save_data_alone_you_bastard'):
            shutil.rmtree(tempdir)
        return r
    return wrapper


@savedir
def test_model_construction(savedir,*args,**kw):
    g = model.Game()
    random.seed(1)

    g.moon.zones = [
        model.Zone('industry'), model.Zone('military'), model.Zone('logistics')
    ]

    #  from page 17: Industry
    z = g.moon.zones[0]
    z.cohorts = [
        model.Privileged(size=g.MED, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.HIGH),
        model.Servitor(size=g.HIGH, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.UNDEF)
    ]
    z.faction = model.Faction('ecobaddy', threat=g.MAX, size=g.MED,informed=g.HIGH,smart=g.LOW,loyal=g.MED,rich=g.HIGH,buffs=[])

    #  from page 17: military
    z = g.moon.zones[1]
    z.cohorts = [
        model.Privileged(size=g.LOW, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.UNDEF),
        model.Servitor(size=g.MED, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.UNDEF)
    ]
    z.faction = model.Faction('mrstompy', threat=g.MAX, size=g.HIGH,informed=g.LOW,smart=g.MED,loyal=g.HIGH,rich=g.LOW,buffs=[])

    #  from page 17: logistics
    z = g.moon.zones[2]
    z.cohorts = [
        model.Privileged(size=g.MED, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.UNDEF),
        model.Servitor(size=g.LOW, liberty=g.UNDEF, quality_of_life=g.UNDEF, cash=g.UNDEF)
    ]
    z.faction = model.Faction('mrfedex', threat=g.MAX, size=g.LOW,informed=g.MED,smart=g.HIGH,loyal=g.HIGH,rich=g.MED,buffs=[])

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
