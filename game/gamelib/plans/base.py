
import weakref
import types
from gamelib.chance import roll, ease


def _get_who(zone, actor, name):
    # late import to avoid circle
    if name is None:
        return None
    elif name == 'zone':
        return zone
    elif name == 'actor':
        return actor
    elif name == 'faction' or name == zone.faction.name:
        return zone.faction
    elif name == 'privileged':
        return zone.privileged
    elif name == 'servitor':
        return zone.servitor
    for g in zone.privileged.resistance_groups:
        if g.name == name:
            return g
    for g in zone.servitor.resistance_groups:
        if g.name == name:
            return g

SUCCESS_THRESHOLD = .01

class Plan:
    '''More generic plans may use costs, risks and effects to capture the
    buffs that are applied as a cost, when the plan succeeds and when the
    plan fails. The buffs are listed as (who, buff) where the who is a name
    looked up with _get_who above, and refers only to things in the same
    zone as the actor.

    Likewise the target is specified as a "who" or None if there is no specific
    target to chance against.
    '''

    NOOP = 'Financial'
    ESPIONAGE = 'Espionage'
    VIOLENCE = 'Violence'
    SABOTAGE = 'Sabotage'
    WHO_ACTOR = 'actor'
    WHO_ZONE = 'zone'
    WHO_FACTION = 'faction'
    WHO_PRIVILEGED = 'privileged'
    WHO_SERVITOR = 'servitor'

    def __repr__(self):
        return '{{{PLAN:%s}}}'%(self.name)
    def __init__(self, name, actor, style=NOOP, description='',
            plan_time=0, attack_stats=[], defend_stats=[], target=None,
            costs=[], risks=[], effects=[]):
        self.name = name
        # use weakref to avoid reference circles (probably unnecessary with GC)
        self._actor = weakref.ref(actor)
        self.style = style  # style is from TYPES, above
        self.description = description
        self.plan_time = plan_time  # turns until enacting
        self.attack_stats = attack_stats  # stats used to see if success
        self.defend_stats = defend_stats  # target's stats use to resist success
        self.target = target
        self.costs = costs  # list of (who, buff) where buff is (stat, val) and who indicates object to buf
        self.risks = risks  # as costs, only take effect if defender wins
        self.effects = effects  # as costs, only take effect if successful

    actor = property(lambda s: s._actor())
    zone = property(lambda s: s._actor().zone)

    def to_json(self):
        return dict(name=self.name, zone=self.zone.name,
            actor=self.actor.name, style=self.style,
            description=self.description, plan_time=self.plan_time,
            attack_stats=self.attack_stats, defend_stats=self.defend_stats,
            target=self.target, costs=self.costs, risks=self.risks,
            effects=self.effects)

    @classmethod
    def from_json(cls, jdata, actor):
        return cls(jdata['name'], actor, jdata['style'],
            jdata['description'], jdata['plan_time'], jdata['attack_stats'],
            jdata['defend_stats'], jdata['target'], jdata['costs'],
            jdata['risks'], jdata['effects'])

    @classmethod
    def score(cls, game, zone, group):
        # check the plan is feasible - return a score which is the chance of
        # success
        return 0

    def enact(self, ui):
        self.pay_costs(ui)
        result = self.check_success(ui)
        ret = False
        result_text = ''  # want to list effects
        success = ''
        if result == 0:
            success = 'FAILED'
            ui.msg('plan %s FAILED'%self.name)
            ret = False
        if result < 0:
            success = 'was a DISASTER'
            ui.msg('plan %s was a DISASTER'%self.name)
            self.apply_risks(ui)
            ret = False
        if result > 0:
            success = 'SUCCEDED'
            ui.msg('plan %s SUCCEDED'%self.name)
            self.apply_effects(ui)
            ret = True
        if self.actor.__class__.__name__ == 'Faction':
            title = '%s ZoneNews'%self.actor.zone.name
            result_text = '%s faction takes action, and %s'%(self.actor.name, success)
        elif self.actor.__class__.__name__ == 'Resistance':
            title = '%s\'s plan %s %s'%(self.actor.name, self.name, success)
        ui.ask_ok(title, self.ask_callback, result_text)
        return ret

    def ask_callback(self, ui):
        pass

    def _apply_buffs(self, ui, buffs):
        from gamelib.model import game
        for who, buff in buffs:
            who = _get_who(self.zone, self.actor, who)
            if who is None:
                ui.msg("cost can't find who %r for buff %r" % (who, buff))
                continue
            attribute, value = buff
            # TODO make buffs a defaultdict(list)
            if type(value) not in ( types.TupleType,types.ListType ):
                value=[value]
            who.buff_stat(attribute,*value)

    def pay_costs(self, ui):
        '''Things to do (usually just buffs to apply) regardless of success
        or failure.
        '''
        self._apply_buffs(ui, self.costs)

    def apply_risks(self, ui):
        '''Things to do (usually just buffs to apply) when failed.
        '''
        self._apply_buffs(ui, self.risks)

    def apply_effects(self, ui):
        '''Things to do (usually just buffs to apply) when succeeded.
        '''
        self._apply_buffs(ui, self.effects)

    def check_success(self, ui):
        attacker = self.actor
        target = _get_who(self.zone, attacker, self.target)
        return self.mechanics(attacker,target)

    def mechanics(self, attacker,target):
        if not len(self.attack_stats):
            return 1  # nothing to check, defense doesn't matter?
        if len(self.attack_stats) >= 3:
            raise Exception('TooManyStatsForRollError')
        # roll for attacker
        result = 0.0
        if len(self.attack_stats) == 1:
            result = roll(attacker.buffed(self.attack_stats[0]))
        if len(self.attack_stats) == 2:
            result = roll(attacker.buffed(self.attack_stats[0]),
                attacker.buffed(self.attack_stats[1]))
        result = ease(result)  # assumes < 2
        if target is not None:
            defense = 0.0
            if len(self.defend_stats) == 1:
                defense = roll(target.buffed(self.defend_stats[0]))
            if len(self.defend_stats) == 2:
                defense = roll(target.buffed(self.defend_stats[0]),
                               target.buffed(self.defend_stats[1]))
            defense = ease(defense)  # assumes < 2
            # lower the attack with the defense
            if abs(result - defense) < SUCCESS_THRESHOLD:
                result = 0
            else:
                result -= defense
        return result

