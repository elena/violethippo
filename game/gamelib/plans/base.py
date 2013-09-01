class Plan:
    TYPE_NOOP = 'No Operation'
    TYPE_ESPIONAGE = 'Espionage'
    TYPE_VIOLENCE = 'Violence'
    TYPE_SABOTAGE = 'Sabotage'

    def check(self, game, group):
        # check the plan is feasible
        raise NotImplementedError()

    def consume_buff(self, game, group, ui):
        # this plan wishes to consume a buff from group.buffs to work
        raise NotImplementedError()

    def enact(self, game, ui):
        # enact this plan
        raise NotImplementedError()

