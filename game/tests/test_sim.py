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
    ui = textui.FakeUI(savedir,g)

    g.init_new_game(ui)

    g.json_savefile(os.path.join(savedir, 'save.json'))
    g2 = g.json_loadfile(os.path.join(savedir, 'save.json'))
    g2.json_savefile(os.path.join(savedir, 'save.json.verify'))
    # diffing save.json and save.json.verify should be equal...

    n = os.path.join(savedir, 'save.json')
    with open(n) as f1, open(n + '.verify') as f2:
        assert f1.read() == f2.read()




def test_zone_state():
    g = model.Game()
    z = g.moon.zones[model.INDUSTRY]
    # at the start of the game, the zone should be strong
    assert z.faction.state_description == 'strong'
    # TODO - when the state can change, test it here

