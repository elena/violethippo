class Plan:
    TYPE_NOOP = 'No Operation'
    TYPE_ESPIONAGE = 'Espionage'
    TYPE_VIOLENCE = 'Violence'
    TYPE_SABOTAGE = 'Sabotage'

    def __init__(self, name, style=TYPE_NOOP, description='', plan_time=0,
        attack_stats=[], defend_stats=[], target=None, costs=[], risks=[],
        effects=[]):
        self.name = name
        self.style = style  # style is from TYPES, above
        self.description = description
        self.plan_time = plan_time  # turns until enacting
        self.attack_stats = attack_stats  # stats used to see if success
        self.defend_stats = defend_stats  # target's stats use to resist success
        self.target = target  # the target object for this plan
        self.costs = costs  # list of (who, buff) where buff is (stat, val) and who indicates object to buf
        self.risks = risks  # as costs, only take effect if defender wins
        self.effects = effects  # as costs, only take effect if successful

    def check(self, game, group):
        # check the plan is feasible
        raise NotImplementedError()

    def consume_buff(self, game, group, ui):
        # this plan wishes to consume a buff from group.buffs to work
        raise NotImplementedError()

    def enact(self, game, ui, attacker):
        if not attacker:
            return False
        result = self.check_success(game, ui, attacker)
        if result == 0:
            # pay costs
            return False
        if result < 0:
            # pay costs
            # enact risks
            return False
        if result > 0:
            # pay costs
            # enact effects
            return True

    def check_success(self, game, ui, attacker):
        if not attacker:
            return 0
        if not len(self.attack_stats):
            return 1  # nothing to check, defense doesn't matter?
        if len(self.attack_stats) >= 3:
            raise Exception('TooManyStatsForRollError')
        # roll for attacker
        result = 0.0
        if len(self.attack_stats) == 1:
            result = game.roll(attacker.getattr(self.attack_stats[0]))  # buffed
        if len(self.attack_stats) == 2:
            result = game.roll(attacker.getattr(self.attack_stats[0]),
            attacker.getattr(self.attack_stats[1]))  # buffed
        result = game.ease(result)  # assumes < 2
        if self.target:
            defense = 0.0
            if len(self.defend_stats) == 1:
                defense = game.roll(target.getattr(self.defend_stats[0]))  # buffed
            if len(self.defend_stats) == 2:
                defense = game.roll(target.getattr(self.defend_stats[0]),
                attatargetcker.getattr(self.defend_stats[1]))  # buffed
            defense = game.ease(defense)  # assumes < 2
            # lower the attack with the defense
            if abs(result - defense) < SUCCESS_THRESHOLD:
                result = 0
            else:
                result -= defense
        return result

