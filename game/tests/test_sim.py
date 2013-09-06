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
        self.setzone( ui.game.moon.zones.keys()[0] )
    def setzone(self,area):
        self.ui.msg('setting UI zone %s %s'%(area, self.ui.game.moon.zones.keys()))
        if area in self.ui.game.moon.zones.keys():
          self.mode=area
          self.ui.msg('        UI zone %s'%(self.mode))


class FakeUI:
    class SIGNAL_GAMEOVER(Exception):
        pass

    def __init__(self, savedir,game):
        self.savedir = savedir
        self.game=game
        model.game=game
        self.messages_on=True
        self.messages = []
        self.zone=FakeUIZone(self)
        self.enter=None
        #
        if savedir:
            self.logging_begin(savedir)

    def update_info(self):
        pass

    def ask_choice(self,title,choices,callback):
        self.msg('ASK: %s'%([title,choices]))
        while True:
            if self.entered:
                ask=self.entered
                self.entered=None
            else:
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


    def msgdump(self):
        if self.messages_on:
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
    random.seed(1)

    g = model.Game()
    ui = FakeUI(savedir,g)

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


@savedir
def test_buffing(savedir,*args,**kw):

    g = model.Game()
    ui = FakeUI(savedir,g)
    ui.messages_on=False
    g.init_new_game(ui)
    g.json_savefile(os.path.join(savedir, 'save.json'))

    bufftest=[.1,.2,.3,.4]
    buff=[]
    priv=g.moon.zones[ model.INDUSTRY ].privileged
    for n in range(100):
        if n in [ 5 ]:
            ui.msg('about to order')
            if n==5:
                ui.entered='OK'
                ui.zone.setzone(model.INDUSTRY)
                player_orders.Hideout().execute(ui)
            priv.buff_stat('liberty',*bufftest)
            buff=bufftest[:]

        dm=0
        if buff:
            dm=buff[0]
            del buff[0]
        print 'gturn %s'%(g.turn)
        print 'buff %s'%(buff)
        print 'testing %s with %s'%( priv.liberty,priv.buffs )
        print 'testing %s == %s'%( priv.liberty,priv.buffed('liberty') )
        assert( priv.liberty==g.MED*2 )
        assert( priv.buffed('liberty')==g.MED*2+dm )
        ui.on_new_turn()




