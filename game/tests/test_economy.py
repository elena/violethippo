import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
from gamelib import textui
#from gamelib.plans.base import Plan





@textui.savedir
def crunch_economy(savedir,callback,**kw):
    random.seed(1)

    g = model.Game()
    ui = textui.FakeUI(savedir,g)
    g.init_new_game(ui)
    g.json_path=os.path.join(savedir, 'save.json')


    active=True
    while active:
        active=callback(ui)
        ui.msg('done order')
        if active:
            ui.on_new_turn()
        ui.update()


def test_economy(ui=None,**kw):
    #
    # On first call... run economy
    if ui is None:
        return crunch_economy(callback=test_economy)
    #
    # On callback... do stuff
    game=ui.game
    turn=game.turn
    if turn==1:
        ui.entered='OK'
        ui.zone.setzone(model.INDUSTRY)
        player_orders.Hideout().execute(ui)
    if turn in [ 5,6,7,16,17,18 ]:
        ui.entered='OK'
        player_orders.BlowupGoods().execute(ui)
    if ui.helper_ratio_under(5, ui.helper_all_stores() )   <  .4:
        ui.critical("FAILED store check %s %s",ui.helper_ratio_under(5, ui.helper_all_stores() ),ui.helper_all_stores() )
        return False
    if turn>=75:
        ui.msg('game sim over: passed')
        return False
    return True



