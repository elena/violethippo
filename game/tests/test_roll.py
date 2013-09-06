import os
import random
import shutil
import time
import functools

from gamelib import chance

# TODO this is a weak test now, just how many successes within 50 out of 1000
#      we get, nothing about quality of success, although we save that


def test_rolls():
    accuracy=50

    for tskill,want in [ [0,0], [.5,500],[1.000000,1000],[1.500000, 1000], [2.000000,1000] ]:
        won = 0
        tot = 0
        for r in range(0,1000):
            result= chance.roll(tskill)
            if result > 0:
                tot += result
                won += 1
        if won > 0:
            tot = tot / won
        print 'rolling',tskill,want,won,won-want,tot
        assert(  abs(won-want)<accuracy )

