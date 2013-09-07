from random import random

EASE_LINEAR=0
EASE_HERMITE=1
EASE_QUAD=2
EASE_CUBIC=3

def roll(d1, d2=0.0):
    total = d1+d2
    if total >= 1.:
        return max(random(), random()) + (total - 1.)
    #
    # Use if want to extend optimal requirements (lower chance of success)
    # if total > 1.5:
    #     return total - .5
    # total *= 2./3.
    #
    total = ease(total)
    ran = random()
    return max(0, total-ran)

def ease(total, easetype=EASE_CUBIC):
    if total > 2:
        raise Exception('EasingValueTooLarge')
    if total > 1:
        return ease(total-1, easetype) + 1
    if easetype == EASE_LINEAR:
        return total
    elif easetype == EASE_HERMITE:
        return (3 * total**2) - (2 * total**3)
    elif easetype == EASE_QUAD:
        total *= 2
        if total < 1:
            return .5 * total**2
        total -= 1
        return -.5 * (total*(total-2) - 1)
    elif easetype == EASE_CUBIC:
        total *= 2
        if total < 1:
           return .5 * total**3
        total -= 2
        return .5 * (total**3 + 2)
    else:
        return 0
