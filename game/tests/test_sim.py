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

    ui = FakeUI(savedir)
    g.update(ui)

    g2 = g.json_loadfile(os.path.join(savedir, 'save.json'))
    g2.json_savefile(os.path.join(savedir, 'save.json.verify'))
    # diffing save.json and save.json.verify should be equal...

    n = os.path.join(savedir, 'save.json')
    with open(n) as f1, open(n + '.verify') as f2:
        assert f1.read() == f2.read()

    g.update(ui)
    g.update(ui)
    g.update(ui)
