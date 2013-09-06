import os
import sys
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

    def helper_all_stores(self):
        rv={}
        for n,o in self.game.moon.zones.items():
            for k,v in o.store.items():
                rv[ n+'/'+k]=v
        return rv

    def helper_ratio_under(self,number,vals):
        n=0
        t=0
        for k,v in vals.items():
            t+=1
            if v>number: n+=1
        return float(n)/t


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
        pass
    def msgfix(self, msg, args):
        if args:
            try:
                msg=msg % args
            except:
                msg='%s %s'%(msg,args)
        return  msg

    def msg(self, msg, *args):
        print self.msgfix(msg,args)
    def critical(self, msg, *args):
        sys.stderr.write( self.msgfix(msg,args)+'\n' )
        self.msg(msg,*args)
    def graph(self,graph,line,turn,value):
        self.msg("GRAPH: %s %s %s %s"%(graph,line,turn,value))

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

