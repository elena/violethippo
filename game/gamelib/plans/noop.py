from gamelib.plans import register
from gamelib.plans.base import Plan


class Noop(Plan):
    type = Plan.TYPE_NOOP

    def check(self, game, group):
        return True

    def consume_buff(self, game, group, ui):
        pass

    def enact(self, game, ui):
        pass

register(Noop)
