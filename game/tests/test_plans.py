from gamelib import plans
from gamelib.plans.base import Plan

from gamelib import model


class ui:
    @staticmethod
    def msg(*args):
        print args


def test_plan_registry():
    print plans.registry
    assert any(plan for plan in plans.registry
        if plan.__name__ == 'DamageProduction')


def test_basic_plan(monkeypatch):
    game = model.Game()
    game.init_new_game(ui)
    monkeypatch.setattr(model, 'game', game)

    for zone in game.moon.zones.values():
        if zone.servitor.resistance_groups:
            actor = zone.servitor.resistance_groups[0]
            target = 'faction'
            break
    else:
        # NO servitor resistance groups!?
        FAIL

    p = Plan('test', zone, actor, Plan.VIOLENCE,
        plan_time=0, attack_stats=['size', 'informed'],
        defend_stats=['size', 'loyalty'], target='privileged',
        costs=[('actor', ('rich', -.1))], risks=[('actor', ('size', -.1))],
        effects=[('privileged', ('size', -.1))])

    p.enact(ui)
