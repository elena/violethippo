from gamelib.plans import register
from gamelib.plans.base import Plan

from gamelib.model import game

class DamageProduction(Plan):
    type = Plan.VIOLENCE

    def search(self, game, zone, group):
        # return the likely chance of this succeeding...
        pass

    def consume_buff(self, game, zone, group, ui):
        pass

    def enact(self, game, zone, ui, group):
        pass


register(DamageProduction)
