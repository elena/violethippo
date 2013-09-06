import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
from gamelib import textui
#from gamelib.plans.base import Plan



@textui.savedir
def test_model_construction(savedir,*args,**kw):
    random.seed(1)

    g = model.Game()
    ui = textui.FakeUI(savedir,g,True)

    g.init_new_game(ui)

    g.json_savefile(os.path.join(savedir, 'save.json'))
    g2 = g.json_loadfile(os.path.join(savedir, 'save.json'))
    g2.json_savefile(os.path.join(savedir, 'save.json.verify'))
    # diffing save.json and save.json.verify should be equal...

    n = os.path.join(savedir, 'save.json')
    with open(n) as f1, open(n + '.verify') as f2:
        assert f1.read() == f2.read()


    for n in range(100):
        if n in [ 5,6,7,8,9 ]:
        #if n in [ 5,6,7,8 ]:
        #if n in [ 5,6,7 ]:
        #if n in [ 5,6 ]:
        #if n in [ 5, ]:
        #if n in [ 5,7,8,9,11 ]:
        #if n in [ 5,7,8,9 ]:
        #if n in [ 5,7,8 ]:
        #if n in [ 5,7 ]:
            ui.msg('about to order')
            if n==5:
                ui.entered='OK'
                ui.zone.setzone(model.INDUSTRY)
                player_orders.Hideout().execute(ui)
            #ui.entered='OK'
            #player_orders.BlowupGoods().execute(ui)
            ui.entered=player_orders.ReplaceWithPlanHurtLiberty.PRIV
            player_orders.ReplaceWithPlanHurtLiberty().execute(ui)
            ui.msg('done order')
            ui.update()
        ui.on_new_turn()


def test_zone_state():
    g = model.Game()
    z = g.moon.zones[model.INDUSTRY]
    # at the start of the game, the zone should be strong
    assert z.faction.state_description == 'strong'
    # TODO - when the state can change, test it here

