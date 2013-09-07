import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
from gamelib import textui
#from gamelib.plans.base import Plan


MAXTURNS=75



def run_economy(ui=None,**kw):
#    #
#    # On first call... run economy
#    if ui is None:
#        return crunch_economy(callback=run_economy,**kw)
    #
    # On callback... do stuff
    game=ui.game
    turn=game.turn
    if turn==1:
        ui.entered='OK'
        ui.zone.setzone(model.INDUSTRY)
        player_orders.Hideout().execute(ui)

    if turn in kw.get('hitgoods',[]):
        ui.entered='OK'
        player_orders.BlowupGoods().execute(ui)

    if turn in kw.get('hitliberty',[]):
        ui.entered=player_orders.ReplaceWithPlanHurtLiberty.PRIV
        player_orders.ReplaceWithPlanHurtLiberty().execute(ui)

    if ui.helper_ratio_under(5, ui.helper_all_stores() )   <  .4:
        ui.critical("FAILED store check %s %s",ui.helper_ratio_under(5, ui.helper_all_stores() ),ui.helper_all_stores() )
        return False

    if turn>=kw.get('maxturns',MAXTURNS):
        ui.msg('game sim over: reached maxturns')
        return False
    return True



@textui.savedir
def crunch_economy(savedir,**kw):
    random.seed(1)

    g = model.Game()
    ui = textui.FakeUI(savedir,g,**kw)
    g.init_new_game(ui)
    g.json_path=os.path.join(savedir, 'save.json')

    active=True
    while active:
        active=run_economy(ui,**kw)
        ui.msg('done order')
        if active:
            ui.on_new_turn()
        ui.update()
    return ui




RUN_OK=True
RUN_FAIL=False

def hit_hook(g,l,res,**kw):
    savedir='goods_%s__liberty_%s__%s'%('_'.join([`n` for n in g]),
                                          '_'.join([`n` for n in l]),
                                          res )
    ui=crunch_economy(hitgoods=g,hitliberty=l,leave_my_save_data_alone_you_bastard=True,newsavedir=savedir,**kw)
    ui.critical('Called: %s',[g,l,res])
    finished= (ui.game.turn==MAXTURNS)
    ui.msgsave('message.log')
    assert( finished==res )

def cam_playing():
    #a=([2],[],RUN_OK)
    a=([5,],[],RUN_OK)
    hit_hook( *a ,debug=True,debuggraph=False)

def test_economy_hits():
    for g,l,r in [
                     ([5],[],RUN_OK),
                     ([5,6],[],RUN_OK),
                     ([5,6,7],[],RUN_FAIL),
                     ([5,6,7,8],[],RUN_FAIL),
                     ([5,7],[],RUN_OK),
                     ([5,7,9],[],RUN_OK),
                     ([5,7,9,11],[],RUN_OK),
                     ([5,7,9,11,13],[],RUN_FAIL),

#                     ([5,6],[],RUN_OK),
                     ([5,6,8],[],RUN_OK),
                     ([5,6,8,11],[],RUN_FAIL),

                     ([5,8,11],[],RUN_OK),
                     ([5,8,11,14],[],RUN_FAIL),
                     ([5,8,11,14,17],[],RUN_FAIL),
#
#                     ([],[5],RUN_OK),
#                     ([],[5,6],RUN_OK),
#                     ([],[5,6,7],RUN_OK),
#                     ([],[5,6,7,8],RUN_OK),
                 ]:
        yield hit_hook,g,l,r




















