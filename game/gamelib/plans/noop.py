from gamelib.plans import register
from gamelib.plans.base import Plan


class Noop(Plan):
    type = Plan.NOOP

    def score(self, game, zone, group):
        return 1

    def enact(self, game, zone, ui, group):
        pass

# register(Noop)
