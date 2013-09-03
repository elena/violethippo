import os
import random
import shutil
import time
import functools

from gamelib import model, player_orders
from gamelib.plans.base import Plan




def test_rolls():
    g = model.Game()

    accuracy=0.001

    for tskill,want in [ [0,0], [.5,0.148148],[1.000000,0.851852],[1.500000, 1.000000], [2.000000,1.500000] ]:
      result=g.roll(tskill)
      print 'rolling',tskill,want,result,result-want
      assert(  abs(result-want)<accuracy )

