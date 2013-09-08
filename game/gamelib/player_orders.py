from gamelib import model
from random import random

all = []
YES = 'OK'
NO = 'Cancel'
YESNO = [YES, NO]


class Order(object):
    """The player has X activity points to spend for the turn, and may take
    one free personal action at any point during the phase, in addition to any
    further actions they wish to purchase. activity points will be a base per
    turn, but might be affected by previous actions or different levels of
    difficulty or different player character stats (race or class/skills).
    """
    full_cost = 0
    OUT_ZONE_PENALTY = 1

    # @staticmethod
    def cost(self, zone):
        if model.game.moon.zones[zone.mode].is_safe:
            return None
        # player can't do anything except find a hideout if there's no hideout
        if not model.game.player.hideout:
            return None
        return self._determine_cost(zone)

    def _determine_cost(self, zone):
        cost = 0
        if not model.game.player.free_order:
            cost = self.full_cost
        if zone.mode != model.game.player.hideout and not (not model.game.player.hideout and model.game.turn == 1):
            cost += self.OUT_ZONE_PENALTY
        if model.game.player.activity_points < cost:
            return None
        return cost


class Hideout(Order):
    """Establish/Move hideout - select a zone, adds to time until caught
    (harder to apply support points to groups in other zones? most player
    orders only in same zone as hideout?) Note: first turn this is the
    player's first order, and must be done before any support is allocated
    """
    label = 'Establish Hideout'

    def __init__(self):
        super(Hideout, self).__init__()
        self.full_cost = 2

    def cost(self, zone):
        if model.game.moon.zones[zone.mode].is_safe:
            return None
        if model.game.moon.zones[zone.mode].player_found >= 1:
            return None
        if model.game.player.hideout == zone.mode:
            return None
        return super(Hideout, self)._determine_cost(zone)

    def execute(self, ui):
        ui.ask_choice('Establish your hideout in the %s zone?'%ui.zone.mode,
            YESNO, self.chosen_yn)

    def chosen_yn(self, ui, choice):
        if choice == YES:
            model.game.player.pay_order_cost(self.cost(ui.zone))
            model.game.player.hideout = ui.zone.mode
            ui.msg('setting player hideout to %s'%(ui.zone.mode))
            ui.hideout_moved()
            ui.update_info()

all.append(Hideout())


class BlowupGoods(Order):
    """DEBUG: Attack goods in an area"""
    label = 'Blow up Goods'

    def __init__(self):
        super(BlowupGoods, self).__init__()
        self.full_cost = 1

    def cost(self, zone):
        if zone.mode != model.INDUSTRY:
            return None
        return super(BlowupGoods, self).cost(zone)

    def execute(self, ui):
        ui.ask_choice('Attack goods stored in %s zone?'%ui.zone.mode,
            YESNO, self.chosen_yn)

    def chosen_yn(self, ui, choice):
        ui.msg('blowing up goods: %s'%(choice))
        if choice == YES:
            model.game.player.pay_order_cost(self.cost(ui.zone))
            zone=model.game.moon.zones[ ui.zone.mode ]
            if model.GOODS in zone.store:
                ui.msg('blowing up goods in %s: %s'%(zone.name, zone.store))
                boom=zone.store[model.GOODS]
                boom=max( 0, boom-2.0 )
                zone.store[model.GOODS]=boom
                ui.msg('booooooooooooooooom %s'%(zone.store))
            else:
                ui.msg('no goods to blow up in %s: %s'%(zone.name, zone.store))
            ui.update_info()

all.append(BlowupGoods())


class ReplaceWithPlanHurtLiberty(Order):
    """Hurt liberty... this needs to be replaced with a rebel plan"""
    label = 'Hurt liberty'

    def __init__(self):
        super(ReplaceWithPlanHurtLiberty, self).__init__()
        self.full_cost = 1

    def cost(self, zone):
        return super(ReplaceWithPlanHurtLiberty, self).cost(zone)

    PRIV="privileged"
    SERV="servitor"
    def execute(self, ui):
        ui.ask_choice('Attack LIBERTY in cohort in %s zone?'%ui.zone.mode,
            [self.PRIV,self.SERV,NO], self.chosen_target)

    def chosen_target(self, ui, choice):
        if choice == NO:
            return
        model.game.player.pay_order_cost(self.cost(ui.zone))
        zone=model.game.moon.zones[ ui.zone.mode ]
        co=None
        if choice==self.PRIV:
            co=zone.privileged
        elif choice==self.SERV:
            co=zone.servitor
        if co is None:
            return
        ui.msg('un-liberty up %s %s'%(choice,co))
        #co.buff_stat('liberty',-.5,-.4,-.3,-.2)
        co.buff_stat('liberty',-1.5)
        ui.msg('          buffs %s'%(co.buffs))
        ui.update_info()

# all.append(ReplaceWithPlanHurtLiberty())



class ZoneIntel(Order):
    """Information on the disposition of the cohorts and the zone itself. We
    want the player to do this when they arrive (second turn) because they
    really need to know this stuff, and be worth doing every now and then
    later on. Information on cohorts might be along the lines of 'biggest
    problem is xxx', along with general information on their sizes and
    functions in the zone? Perhaps several levels of info requiring several
    successive attempts (not necessarily one after another)?
    """


class InfiltrateFaction(Order):
    """uncover information that might be useful in working out what the
    Faction is doing this turn (an already planned action) which might enable
    the player to warn the groups through discouraging or encouraging specific
    plans, as well as showing more detailed indication of the faction's
    current status?
    """


class LocateResistance(Order):
    """locate resistance groups
    """


class Funding(Order):
    """Seek funding source - prepare for Develop Group on a later turn
    """


class DevelopGroup(Order):
    """Enhance a group's stat (Smarts, Informed, Rich)
    """


class MakeAPlan(Order):
    """Reveal a potential plan and assign it to a group (or forget it),
    perhaps select style of plan? Or presented with brief summary of three and
    you select one?
    """


class MovePlan(Order):
    """Take a plan from one group and give it to another (this will likely
    affect its chance of success, as the groups will be unlikely to have the
    same stats)
    """


class Sabotage(Order):
    """Reduce production efficiency for this turn?
    """


class Disrupt(Order):
    """Interdict faction plan reducing its chance of success
    """


class Frame(Order):
    """Plant evidence (situational must have evidence and conditions to make
    it relevant)
    """


class Steal(Order):
    """Steal something
    """


class RemoveResistanceLeader(Order):
    """Changes the modus operandi for the group, potentially affects its other
    stats negatively, potentially disbanding the group
    """


class AttackFactionLeader(Order):
    """When a Faction is weakened enough, this should become available, and
    allow the player to permanently reduce the zone/faction to providing
    minimal resources, taking no Faction actions. But also increases awareness
    for all other Factions significantly
    """
    label='Remove faction'

    def __init__(self):
        super(AttackFactionLeader, self).__init__()
        self.full_cost = 3

    def cost(self, zone):
        if model.game.moon.zones[zone.mode].is_safe:
            return None
        faction = model.game.moon.zones[zone.mode].faction
        cost = model.game.player.max_activity_points
        if faction.state > .3:
            return None
        if zone.mode != model.game.player.hideout and not (not model.game.player.hideout and model.game.turn == 1):
            cost += self.OUT_ZONE_PENALTY
        if model.game.player.activity_points < cost:
            return None
        return cost

    def execute(self, ui):
        faction = model.game.moon.zones[ui.zone.mode].faction
        ui.ask_choice('Assassiniate the leader and destroy the %s faction?'%faction.name,
            YESNO, self.chosen_yn)

    def chosen_yn(self, ui, choice):
        if choice == YES:
            model.game.player.pay_order_cost(self.cost(ui.zone))
            faction = model.game.moon.zones[ui.zone.mode].faction
            faction.size = 0
            faction.informed = 0
            faction.smart = 0
            faction.loyal = 0
            faction.rich = 0
            faction.buffs = {}
            faction.name = "Destroyed"
            ui.msg('%s faction destroyed'%(faction.name))
            zone = faction.zone
            for co in [zone.privileged, zone.servitor]:
                # return both cohorts to starting (or better)
                co.buffs = {}
                co.resistance_groups = []
                # for gr in co.resistance_groups:
                #     gr.size = 0
                #     gr.buffs = {}
                for st in ['size', 'liberty', 'quality_of_life', 'cash']:
                    newval = max(getattr(co, st), getattr(co, st + '_base'))
                    setattr(co, st, newval)
            # warn the other zones
            for zonetype in model.game.moon.zones:
                if zonetype == ui.zone.mode:
                    continue
                zone = model.game.moon.zones[zonetype]
                # increase alert and player_found
                zone.player_found += (1-zone.player_found)/4
                zone.faction.alert = min(1, zone.faction.alert + .2)
                zone.faction.buff_stat('alert', .5,.45,.4,.3,.2,.05)
            ui.update_info()

all.append(AttackFactionLeader())


class AttackFaction(Order):
    """Attack a faction and damage its size
    Just a debug attack useful against military
    """
    label = 'Attack Faction'

    def __init__(self):
        super(AttackFaction, self).__init__()
        self.full_cost = 2

    def execute(self, ui):
        ui.ask_choice('War against %s faction in this zone? (hurt size and random stat)'%model.game.moon.zones[ui.zone.mode].name,
            YESNO, self.chosen_yn)

    def chosen_yn(self, ui, choice):
        if choice == YES:
            model.game.player.pay_order_cost(self.cost(ui.zone))
            zone=model.game.moon.zones[ui.zone.mode]
            fact=zone.faction
            fact.size = max(0, fact.size - 0.05)
            secondary = random()
            if secondary > .75:
                fact.loyal = max(0, fact.loyal - 0.05)
            if secondary > .5:
                fact.informed = max(0, fact.informed - 0.05)
            if secondary > .25:
                fact.smart = max(0, fact.smart - 0.05)
            else:
                fact.rich = max(0, fact.rich - 0.05)
            zone.player_found = min(1, zone.player_found + 0.15)
            ui.msg('Player attacked faction in %s'%ui.zone.mode)
            ui.update_info()

all.append(AttackFaction())

class ChangePlan(Order):
    """Modify a plan
    """
    label = 'Modify a plan'

    def __init__(self):
        super(ChangePlan, self).__init__()
        self.full_cost = 1

    def cost(self, zone):
        if model.game.player.free_order:
            return None
        z = model.game.moon.zones[zone.mode]
        if not any(g for g in z.privileged.resistance_groups
                if g.plans) and not any(g for g in z.servitor.resistance_groups
                if g.plans):
            return None

        return super(ChangePlan, self).cost(zone)

    def execute(self, ui):
        self.zone = model.game.moon.zones[ui.zone.mode]
        namelist = [g.name for g in self.zone.privileged.resistance_groups
            if g.plans] + [g.name for g in self.zone.servitor.resistance_groups
            if g.plans]
        ui.ask_choice('Modify a plan from which group?',
            namelist, self.chosen_group)

    def chosen_group(self, ui, choice):
        for co in [self.zone.privileged, self.zone.servitor]:
            for g in co.resistance_groups:
                if choice == g.name:
                    self.group = g
                    break
                    break
        if not self.group:
            return
        # list all plans
        planlist = [p.description for p in self.group.plans]
        ui.ask_choice('Choose a plan to modify', planlist, self.chosen_plan,
            'Modify which plan that %s is working on?' % self.group.name)

    def chosen_plan(self, ui, choice):
        for p in self.group.plans:
            if p.description == choice:
                self.plan = p
                break
        if not self.plan:
            return
        opslist = ['speed up']
        description = 'How do you want to modify the plan (%s) that %s is '\
            'working on?' % (self.plan.description, self.group.name)
        ui.ask_choice('Modify it how?', opslist + ['Cancel'], self.chosen_op,
            description)

    def chosen_op(self,ui, choice):
        if choice == 'speed up':
            self.plan.plan_time = max(1, self.plan.plan_time - 1)
            ui.msg('sped up %s plan %s, to %d'%(self.group.name,
                self.plan.name, self.plan.plan_time))
        # more ops, more changes
        model.game.player.pay_order_cost(self.cost(ui.zone))

all.append(ChangePlan())
