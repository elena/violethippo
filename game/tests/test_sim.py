import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
#from gamelib.plans.base import Plan


class FakeUIZone:
    def __init__(self,ui):
        self.ui=ui
        self.mode=ui.game.moon.zones.keys()[0]
        ui.msg('inside zone %s'%(self.mode))

class FakeUI:
    class SIGNAL_GAMEOVER(Exception):
        pass

    def ask_choice(self,title,choices,callback):
        self.msg('ASK: %s'%([title,choices]))
        while True:
            ask=raw_input('     %s'%([title,choices]))
            try:
                self.msg("   === %s"%(choices[int(ask)]))
                ask=choices[int(ask)]
            except:
                pass
            for c in choices:
                if c.lower()==ask.lower():
                    self.msg("   === %s"%(c))
                    return callback(self,c)
            self.msg("      ? dunno ? %s"%([ask]))
        raise Exception


    def __init__(self, savedir,game):
        self.savedir = savedir
        self.game=game
        model.game=game
        self.messages = []
        self.zone=FakeUIZone(self)
        #
        self.logging_begin(savedir)

    def msgdump(self):
        for m in self.messages:
            print self.msgfix(*m)
        self.messages=[]
    def msgfix(self, msg, args):
        if args:
            try:
                msg=msg % args
            except:
                msg='%s %s'%(msg,args)
        return  msg
    def msg(self, msg, *args):
        self.messages.append((msg, args))

    def logging_begin(self, sdir):
        if os.path.exists(sdir):
            shutil.rmtree(sdir)
        os.mkdir(sdir)
    def update(self):
        self.msgdump()


    def on_new_turn(self):
        try:
            model.game.update(self)
        except self.SIGNAL_GAMEOVER:
            pass
        self.update()



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
    g.json_savefile(os.path.join(savedir, 'save.json'))
    random.seed(1)

    ui = FakeUI(savedir,g)
    ui.on_new_turn()

    g2 = g.json_loadfile(os.path.join(savedir, 'save.json'))
    g2.json_savefile(os.path.join(savedir, 'save.json.verify'))
    # diffing save.json and save.json.verify should be equal...

    n = os.path.join(savedir, 'save.json')
    with open(n) as f1, open(n + '.verify') as f2:
        assert f1.read() == f2.read()

    ui.on_new_turn()
    ui.msg('about to order')
    player_orders.Hideout().execute(ui)
    player_orders.BlowupGoods().execute(ui)
    ui.msg('done order')
    ui.update()
    ui.on_new_turn()
    ui.on_new_turn()
    ui.on_new_turn()


def test_zone_state():
    g = model.Game()
    z = g.moon.zones['industry']
    # at the start of the game, the zone should be strong
    assert z.faction.state_description == 'strong'
    # TODO - when the state can change, test it here
