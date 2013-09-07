
import os
import json
import time
import random

from gamelib.plans.base import Plan

import economy
from chance import roll, ease

# please update this when saves will not be valid
# do not use '.' or '_'
DATA_VERSION = '07'
# 02 - added max_resistance to cohorts
# 03 - removed faction threat from saved data
#      added _base values
#      removed history on resistance modus operandi
# 04 - made buffs a dictionary
# 05 - added free_order to player
# 06 - added plans to groups
# 07 - added need_plan to resistance groups

ENFORCEMENT='enforcement'
RAW_MATERIAL='material'
GOODS='goods'
MANPOWER='lifeforms'

INDUSTRY='industry'
MILITARY='military'
LOGISTICS='logistics'



class Buffable(object):
    def buff_stat(self, name, *args):
        if name not in self.buffs:
            self.buffs[name] = []
        for n in range(len(args)):
            if n == len(self.buffs[name]):
                self.buffs[name].append( args[n] )
            elif n >= len(self.buffs[name]):
                raise Exception,['Should never happen?']
            else:
                self.buffs[name][n] += args[n]

    def buffed(self,name):
        v = getattr(self, name, 0.0)
        buffs = self.buffs.get(name, [])
        if buffs:
            v += buffs[0]
        return v

    def buffs_end_turn(self):
        for v in self.buffs.values():
            if v:
                del v[0]


class JSONable(object):
    # take a list of simple variables to save....
    def json_dump_simple(self, *names):
        v = {}
        for k in names:
            v['.' + k] = getattr(self, k)
        return v
    # restore anything simple.....
    def json_load_simple(self, jdata):
        v = {}
        for k in jdata:
            if k.startswith('.'):
                v[k] = setattr(self, k[1:], jdata[k])
        return v

    # create an object from a json save.
    @classmethod
    def json_create(cls, jdata):
        args = cls.json_create_args(jdata)
#        print cls, args
        o = cls(*args)
        o.json_load_simple(jdata)
        o.json_load(jdata)
        return o

    # handle __init__ args
    @classmethod
    def json_create_args(cls, jdata):
        return []

    # then load the extra (non simple) data bits... default to nothing to load
    def json_load(self, jdata):
        pass


class RecordedAttribute(object):
    def __init__(self, name):
        self.name = name
    def __get__(self, instance, owner):
        return getattr(instance, self.name + '_value', None)
    def __set__(self, instance, value):
        if not hasattr(instance, self.name + '_base'):
            setattr(instance, self.name + '_base', value)
        old_val = getattr(instance, self.name + '_value', None)
        if value == old_val:
            return
        if not hasattr(instance, self.name + '_history'):
            setattr(instance, self.name + '_history', [])
        if game is not None:
            turn = game.turn
        else:
            turn = 0
        getattr(instance, self.name + '_history').append((turn, value))
        setattr(instance, self.name + '_value', value)


# this global will be set to the *current game* when convenient
game = None


class Game(JSONable):

    LOW=.1
    MED=.2
    HIGH=.4
    VHIGH=.6
    MAX=1.0

    def __repr__(self):
        return '{{{GAME}}}'

    def __init__(self):
        self.moon = Moon()
        self.player = Player()
        self.turn = 0
        self.created = time.time()
        self.turn_date = time.time()
        self.game_over = False
        self.player.visibility = len(self.moon.zones)
        self.player.activity_points = self.player.max_activity_points
        self.data_version = DATA_VERSION
        #
        # Seed for repeatable testing
        #
        # random.seed(1)
        #

    def json_savefile_turn(self):
        p = self.json_path
        fn, ext = os.path.splitext(p)
        self.json_savefile('%s_turn_%03d_%s.json' % (fn, self.turn, self.data_version))
        # save again under the original name
        self.json_savefile(p)

    def json_savefile(self, filename=None):
        if filename:
            self.json_path = filename
        else:
            assert self.json_path, 'saving without loading or explicit filename'
        with open(self.json_path, 'w') as f:
            json.dump(self.json_dump(), f, indent=2, sort_keys=True)

    @classmethod
    def json_loadfile(cls, filename):
        with open(filename) as f:
            jdata = json.load(f)
        o = cls.json_create(jdata)
        o.json_path = filename
        return o

    def json_dump(self):
        v = self.json_dump_simple('turn', 'created', 'turn_date',
            'game_over', 'data_version')
        v['player'] = self.player.json_dump()
        v['moon'] = self.moon.json_dump()
        return v

    def json_load(self, jdata):
        self.moon = Moon.json_create(jdata['moon'])
        self.player = Player.json_create(jdata['player'])

    def init_new_game(self, ui):
        ui.msg('game: initializing game at start')
        for t in range(3):
            for z in self.moon.zones:
                self.moon.zones[z].privileged.spawn_rebels(self, ui)
                self.moon.zones[z].servitor.spawn_rebels(self, ui)
        self.turn = 1

    def update(self, ui):
        ui.msg('-'*70)
        ui.msg('game: update starting. turn %s'%self.turn)
        ui.msg('-'*70)
        self.turn_date = time.time()
        # we pass in the Game instance and the UI from the top level so the
        # model objects don't need to hang on to them
        self.player.update(self, ui)
#        self.planet.update(self, ui)     # not defined
        self.moon.update(self, ui)
        self.turn+=1
        #
        # Check for game over condition..
        #
        ui.msg('threat is %s' % self.threat)
        if self.threat <= 0:
            self.game_over = True
            raise ui.SIGNAL_GAMEOVER  # player won
        if self.player.visibility <= 0:
            self.game_over = True
            raise ui.SIGNAL_GAMEOVER  # player lost
        #
        # Liam's debug code
        #
        # win = 0
        # tot = 0
        # for rollnum in range(0,100):
        #     ret = roll(0.2, 0.3)
        #     if ret > 0:
        #         win += 1
        #         tot += ret
        # print "rolled: %d wins, avg: %.3f" % (win, (tot/win))
        #

        #
        # save to be paranoid
        #
        ui.msg('game: saving')
        self.json_savefile_turn()
        ui.msg('-'*70)
        ui.msg('game: update DONE. now turn %s'%self.turn)
        ui.msg('-'*70)

    @property
    def threat(self):
        threat = 0
        for zone in self.moon.zones:
            threat += self.moon.zones[zone].faction.threat
        return threat


class Player(JSONable):
    """Represents the player's orders.

    Use actvity points per:

    one free player action (any player action, cost 0)
    each group support/discourage within the zone costs 1 activity point
    each group support/discourage outside the zone costs 2 activity points
    each additional player action costs 3 activity points (possibly some
        are more expensive when purchased this way)
    """
    def __repr__(self):
        return '{{{Player}}}'

    def __init__(self, visibility=0, activity_points=0, max_activity_points=3,
        free_order=True, hideout=None):
        self.discovery_chance = 0    # TODO I think this is unnecessary...
        self.visibility = visibility   # affected by orders with "Instigator Noticeable"
        self.activity_points = activity_points
        self.max_activity_points = max_activity_points
        self.hideout = hideout   # one of the zone types, player must choose
        self.free_order = free_order  # is free order available this turn?

    def json_dump(self):
        return self.json_dump_simple('visibility', 'activity_points',
            'max_activity_points', 'free_order', 'hideout')

    @classmethod
    def json_create_args(cls,jdata):
        return [jdata['.visibility'], jdata['.activity_points'],
            jdata['.max_activity_points'], jdata['.free_order'],
            jdata['.hideout']]

    def pay_order_cost(self, cost):
        if self.free_order:
            self.free_order = False
        else:
            self.activity_points = max(0, self.activity_points - cost)

    def update(self, game,ui):
        ui.msg('%s update player'% self)
        self.visibility = 0
        for zone in game.moon.zones:
            self.visibility += 1 - game.moon.zones[zone].player_found
        self.activity_points = self.max_activity_points
        self.free_order = True


class Moon(JSONable):
    """Made up of N zones, each ruled by a Boss who has a Faction around him.
    Remote from the Planet, but controlling it economically, militarily, and
    politically. Its ability to project its power is the key to victory and so
    should be represented, or able to be derived from detailed zone/faction
    status.
    """
    def __repr__(self):
        return '{{{Moon}}}'

    def __init__(self):
        self.zones = { INDUSTRY:Zone.create_industry(),
                       MILITARY:Zone.create_military(),
                       LOGISTICS:Zone.create_logistics()
                     }

    def json_dump(self):
        v = self.json_dump_simple()
        v['zones'] = dict((z, self.zones[z].json_dump()) for z in self.zones)
        return v

    def json_load(self, jdata):
        self.zones = dict((z, Zone.json_create(jdata['zones'][z]))
            for z in jdata['zones'])

    def update(self, game, ui):
        ui.msg('%s updating moon'%self)
        for zone in self.zones:
            self.zones[zone].update(game,ui)
        goods=self.zones[INDUSTRY].store.get(GOODS,0)
        ui.msg('ECONOMY.consume: %sgoods'%(goods))
        for zone in self.zones:
            z=self.zones[zone]
            z.economy_use_goods(game,ui,goods)
            z.economy_consume_rest(game,ui)
        self.zones[INDUSTRY].economy_consume_goods(game,ui,goods)
        ui.msg('ECONOMY.transport')
        for zone in self.zones:
            self.zones[zone].economy_transport(game,ui)
        ui.msg('ECONOMY.produce')
        for zone in self.zones:
            self.zones[zone].economy_produce(game,ui)


class Zone(JSONable, economy.Zone_Economy):
    """Convert a raw material into a resource

    Contain two Cohorts (population groups)
    Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work
    Resource requirements must be met or dropoff in output.
    """
    def __repr__(self):
        return '{{{Zone:%s}}}'%(self.name)

    def __init__(self, name):
        self.name = name
        # economy / production
        super(Zone, self).__init__()
        # groups
        self.privileged = None  # privileged cohort
        self.servitor = None    # servitor cohort
        self.faction = None
        self.player_found = 0  # close to finding player in zone

    @classmethod
    def create_industry(cls):
        o = cls(INDUSTRY)
        o.requirements=[ ENFORCEMENT, RAW_MATERIAL ]
        o.provides=[ GOODS ]
        o.privileged = Privileged(size=Game.MED*2, liberty=Game.MED*2,
                quality_of_life=Game.HIGH*2, cash=Game.HIGH*2, max_resistance=2)
        o.servitor = Servitor(size=Game.MAX, liberty=Game.LOW*2,
                quality_of_life=Game.LOW*2, cash=Game.MED*2, max_resistance=4)
        o.faction = Faction('ecobaddy', alert=.01,
            size=Game.MED, informed=Game.HIGH, smart=Game.LOW, loyal=Game.MED,
            rich=Game.HIGH, buffs={})
        # o.privileged.new_resistance('industry-res-1',
        #     size=Game.HIGH, informed=Game.LOW, smart=Game.LOW, loyal=Game.LOW,
        #     rich=Game.LOW, buffs={}, visibility=Game.LOW,
        #     modus_operandi=Plan.VIOLENCE, 0)
        # o.servitor.new_resistance('industry-res-2',
        #     size=Game.LOW, informed=Game.MED, smart=Game.LOW, loyal=Game.LOW,
        #     rich=Game.LOW, buffs={}, visibility=Game.LOW,
        #     modus_operandi=Plan.SABOTAGE, 0)
        o.setup_turn0()
        return o

    @classmethod
    def create_military(cls):
        o = cls(MILITARY)
        o.requirements= [MANPOWER]
        o.provides= [ ENFORCEMENT ]
        o.privileged = Privileged(size=Game.LOW*2, liberty=Game.HIGH*2,
                quality_of_life=Game.HIGH*2, cash=Game.HIGH*2, max_resistance=2)
        o.servitor = Servitor(size=Game.MED*2, liberty=Game.HIGH*2,
                quality_of_life=Game.MED*2, cash=Game.MED*2, max_resistance=4)
        o.faction = Faction('mrstompy', alert=.01,
            size=Game.HIGH, informed=Game.LOW, smart=Game.MED, loyal=Game.HIGH,
            rich=Game.LOW, buffs={})
        # o.servitor.new_resistance('military-res-1',
        #     size=Game.LOW, informed=Game.MED, smart=Game.MED, loyal=Game.HIGH,
        #     rich=Game.MED, buffs={}, visibility=Game.LOW,
        #     modus_operandi=Plan.VIOLENCE, 0)
        o.setup_turn0()
        return o

    @classmethod
    def create_logistics(cls):
        o = cls(LOGISTICS)
        o.requirements= [ENFORCEMENT]
        o.provides= [RAW_MATERIAL,MANPOWER]
        o.privileged = Privileged(size=Game.MED*2, liberty=Game.HIGH*2,
                quality_of_life=Game.HIGH*2, cash=Game.HIGH*2, max_resistance=2)
        o.servitor = Servitor(size=Game.LOW*2, liberty=Game.MED*2,
                quality_of_life=Game.HIGH*2, cash=Game.MED*2, max_resistance=4)
        o.faction = Faction('mrfedex', alert=.02,
            size=Game.LOW, informed=Game.MED, smart=Game.HIGH, loyal=Game.HIGH,
            rich=Game.MED, buffs={})
        # o.privileged.new_resistance('logistics-res-1',
        #     size=Game.MED, informed=Game.HIGH, smart=Game.HIGH, loyal=Game.MED,
        #     rich=Game.HIGH, buffs={}, visibility=Game.LOW,
        #     modus_operandi=Plan.SABOTAGE, 0)
        # o.servitor.new_resistance('logistics-res-2',
        #     size=Game.MED, informed=Game.HIGH, smart=Game.HIGH, loyal=Game.MED,
        #     rich=Game.HIGH, buffs={}, visibility=Game.LOW,
        #     modus_operandi=Plan.ESPIONAGE, 0)
        o.setup_turn0()
        return o

    def json_dump(self):
        v = self.json_dump_simple('name', 'requirements', 'provides',
            'player_found','store')
        v['faction'] = self.faction.json_dump()
        v['priv'] = self.privileged.json_dump()
        v['serv'] = self.servitor.json_dump()
        return v

    @classmethod
    def json_create_args(cls,jdata):
        return [jdata['.name']]

    def json_load(self, jdata):
        self.privileged = Privileged.json_create(jdata['priv'])
        self.servitor = Servitor.json_create(jdata['serv'])
        self.faction = Faction.json_create(jdata['faction'])

    def update(self, game, ui):
        ui.msg('%s updating zone'%(self))
        # do plans and orders
        self.privileged.update(game, ui)
        self.servitor.update(game, ui)
        self.faction.update(game, ui)
        #
        # continue to search for the player
        if self.player_found < 1:
            if game.player.hideout == self.name:
                self.player_found += self.faction.alert
            else:
                self.player_found += self.faction.alert * .1
                # perhaps not able to be found unless hideout in zone?
            self.player_found = min(self.player_found, 1)
            ui.msg('player found in %s: %f'%(self.name, self.player_found))
        #
        # Economy is now updated *after* update via moon.update.
        # Economy code is now in economy.py
        #
        for n in [ ENFORCEMENT,RAW_MATERIAL,GOODS,MANPOWER ]:
            v=self.store.get(n,0)
            ui.graph('store',self.name+'.'+n,game.turn,v)
        for c in [ self.privileged, self.servitor]:
            for n in ['size','liberty','quality_of_life','cash','willing','efficiency']:
                ui.graph(self.name+'.pop',c.NAME+'/'+n,game.turn,getattr(c,n))
            ui.msg('BUFFCHECK: %s %s %s/%s -- %s'%(self.name, c.NAME,
                c.liberty, c.buffed('liberty'), c.buffs))


class Cohort(JSONable, Buffable):
    """Each zone has two cohorts:

        Privileged - staff zone faction
        Servitor - create zone resource

    We must know how willing each cohort is to carry out its appointed task.
    And how easily resistance can be recruited/created from there. Willingness
    is derived from the way the cohort is treated.

    """
    size = RecordedAttribute('size')
    liberty = RecordedAttribute('liberty')
    quality_of_life = RecordedAttribute('quality_of_life')
    cash = RecordedAttribute('cash')
    NAME='cohort'
    def __repr__(self):
        return '{{{Cohort}}}'

    def __init__(self, size, liberty, quality_of_life, cash, max_resistance):
        self.size = size           # how many in population
        self.liberty = liberty        # freedom from rules and monitoring
        self.quality_of_life = quality_of_life        # provided services
        self.cash = cash           # additional discretionary money
        self.resistance_groups = []   # list of resistance groups
        self.buffs = {}
        self.production_output_turn0=self.production_output()
        self.max_resistance = max_resistance

    def json_dump(self):
        names = []
        for name in ['size', 'liberty', 'quality_of_life', 'cash']:
            names.append(name + '_value')
            names.append(name + '_base')
            names.append(name + '_history')
        names.append('production_output_turn0')
        names.append('max_resistance')
        names.append('buffs')
        v = self.json_dump_simple(*names)
        v['resistance_groups'] = [g.json_dump()
            for g in self.resistance_groups]
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just pretend it's all ok - json_load will fix things
        return [0, 0, 0, 0, 0]

    def json_load(self, jdata):
        for name in ['size', 'liberty', 'quality_of_life', 'cash']:
            setattr(self, name + '_value', jdata['.%s_value' % name])
            setattr(self, name + '_base', jdata['.%s_base' % name])
            setattr(self, name + '_history', jdata['.%s_history' % name])
        self.production_output_turn0=jdata['.production_output_turn0']
        self.max_resistance = jdata['.max_resistance']
        self.resistance_groups = [Resistance.json_create(g)
            for g in jdata['resistance_groups']]

    def new_resistance(self, name, size, informed, smart, loyal, rich, buffs,
        visibility, modus_operandi, need_plan):
        if len(self.resistance_groups) < self.max_resistance:
            self.resistance_groups.append(Resistance(name, size, informed,
                smart, loyal, rich, buffs, visibility, modus_operandi,
                need_plan))
            return self.resistance_groups[-1]
        return None

    @property
    def willing(self):
        """Servitors: Willingness can be forced through low liberty,
           or the product of high quality of life and cash in combination.
        """
        return max(1.-self.buffed('liberty'), (self.quality_of_life + self.cash)/2)

    @property
    def efficiency(self):
        """priv: efficiency is mostly QOL and somewhat influenced by
        liberty and cash
        """
        return (2* self.quality_of_life + self.buffed('liberty') + self.cash)/4.

    @property
    def rebellious(self):
        """Rebellion is caused by low liberty, quality of life, and cash.
        """
        # TODO: temporary changes to quality of life should not lower rebellion
        # - shortfalls in food do not make more rebels, only long term loss
        vals = [self.liberty, self.quality_of_life, self.cash]
        return 1. - sum(vals + [min(vals)]) / 4.

    def update(self, game, ui):
        # check for new rebellion
        self.spawn_rebels(game, ui)
        for group in self.resistance_groups:
            group.update(game, ui)
        self.buffs_end_turn()
        ui.msg('cohort %s update done' % self)

    def spawn_rebels(self, game, ui):
        rebelchance = ease(self.rebellious)
        ui.msg('rebel chance: %.1f' % (rebelchance * 100., ))
        if not random.random() <= rebelchance:
            return
        ui.msg('rebels spawned in %s' % self)
        new_group = None
        if not (len(self.resistance_groups)) or (random.random() <= self.size):
            new_group = self.new_resistance('res%d ' % random.randint(1, 1000),
                Resistance.START_SIZE, Resistance.START_INFORMED,
                Resistance.START_SMART, Resistance.START_LOYAL,
                Resistance.START_RICH, {}, 0, Plan.NOOP, 0)
        cohort_effect = ease(self.size)
        if new_group:
            # change defaults to fit this cohort
            # TODO should have some more random in here
            new_group.size += Resistance.START_SIZE * cohort_effect
            new_group.rich = self.cash * cohort_effect
            new_group.loyal = max(Resistance.START_LOYAL,
                random.random() * cohort_effect)
            # TODO should affect all stats somehow
            ui.msg('new rebels created: %s'%new_group.name)
        elif len(self.resistance_groups):
            # no new group, so boost an existing group
            cohort_effect /= 5.
            group = self.resistance_groups[random.randint(0,
                len(self.resistance_groups)-1)]
            group.size = min(1,
                group.size + (cohort_effect * self.rebellious))
            group.loyal = max(Resistance.START_LOYAL,
                group.loyal - (cohort_effect * 0.5))
            group.rich = min(1, group.rich + (cohort_effect * self.cash))
            group.visibility = min(1, group.visibility + ((1-cohort_effect)*(.1*random.random())))
            ui.msg('boosted existing rebels %s' % group.name)


class Privileged(Cohort):
    NAME='coh_priv'
    def __repr__(self):
        return '{{{Cohort.priv}}}'

    def production_output(self):
        return self.efficiency

    @property
    def is_servitor(self):
        return False


class Servitor(Cohort):
    NAME='coh_serv'
    def __repr__(self):
        return '{{{Cohort.serv}}}'

    def production_output(self):
        return self.willing

    @property
    def is_servitor(self):
        return True


class Group(JSONable, Buffable):
    """A group of non-rabble that actually do stuff in the game.
    """
    size = RecordedAttribute('size')
    informed = RecordedAttribute('informed')
    smart = RecordedAttribute('smart')
    loyal = RecordedAttribute('loyal')
    rich = RecordedAttribute('rich')

    def __repr__(self):
        return '{{{Group:%s}}}'%(self.name)

    def __init__(self, name, size, informed, smart, loyal, rich, buffs):
        self.name = name
        self.size = size
        self.informed = informed
        self.smart = smart
        self.loyal = loyal
        self.rich = rich
        self.buffs = buffs
        self.plans = []

    def json_dump(self):
        names = ['buffs', 'name']
        for name in ['size', 'informed', 'smart', 'loyal', 'rich']:
            names.append(name + '_value')
            names.append(name + '_base')
            names.append(name + '_history')
        v = self.json_dump_simple(*names)
        v['plans'] = [p.to_json() for p in self.plans]
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return [jdata['.name'], 0, 0, 0, 0, 0, jdata['.buffs']]

    def json_load(self, jdata):
        for name in ['size', 'informed', 'smart', 'loyal', 'rich']:
            setattr(self, name + '_value', jdata['.%s_value' % name])
            setattr(self, name + '_base', jdata['.%s_base' % name])
            setattr(self, name + '_history', jdata['.%s_history' % name])
        self.plans = [Plan.from_json(d) for d in jdata['plans']]

    def update(self, game, ui):
        # Groups plan - plan the action they will take next turn
        # (not visible to player)
        # ui.msg('%s update not implemented' % self)
        pass

    @property
    def state(self):
        # TODO
        # State is primarily based on our damage below starting stats
        # perhaps our highest starting stats matter most
        # should include the effects of temporary buffs
        # find the stats which were HIGH or better at the start
        # the damage to them is 2/3 our state
        # the avg of the rest is the other 1/3
        main = []
        rest = []
        for stat in ['size', 'informed', 'smart', 'loyal', 'rich']:
            base = getattr(self, stat + '_base')
            diff = (getattr(self, stat + '_base') - getattr(self, stat))/getattr(self, stat + '_base')
            if base >= Game.HIGH:
                main.append(diff)
            else:
                rest.append(diff)
        if not len(main):
            return 1-sum(rest)/len(rest)
        if not len(rest):
            return 1-sum(main)/len(main)
        return 1-((3*(sum(main)/len(main))) + (sum(rest)/len(rest)))/4.
        # return 1.0

    @property
    def state_description(self):
        st = self.state
        if st > .75:
            return 'strong'
        if st > .5:
            return 'battered'
        if st > .3:
            return 'shaky'
        if st > .1:
            return 'vulnerable'
        if st > 0:
            return 'turmoil'
        return 'destroyed'


class Faction(Group):
    """Invader Factions
    Led by a boss
    Staffed by zone Privileged Cohort
    controls a power projector (threat to the planet)
    requires support (resource or resources)
    """

    def __init__(self, name, size, informed, smart, loyal, rich, buffs,
        alert):
        super(Faction, self).__init__(name, size, informed, smart, loyal, rich,
            buffs)
        self.alert = alert       # awareness of rebellion and player


    def json_dump(self):
        v = super(Faction, self).json_dump()
        v.update(self.json_dump_simple('alert'))
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return super(Faction, cls).json_create_args(jdata) + [0]

    def json_load(self, jdata):
        super(Faction, self).json_load(jdata)

    @property
    def threat(self):
        return self.state

    def update(self, game, ui):
        '''
        Factions carry out the plan they were working on
        Perhaps Factions recover a small amount based on Privileged cohort
        Perhaps Factions may find a resistance group (small chance)
        Factions decide on a new plan for next turn
        '''
        if self.size <= 0:  # not buffed, perhaps this should be self.state
            return  # we are dead? do nothing
        ui.msg('Faction %s: update'%self.name)
        super(Faction, self).update(game, ui)
        # carry out plan
        for plan in self.plans:
            if plan.plan_time == 0:
                plan.enact(ui)
                self.plans.remove(plan)
            else:
                plan.plan_time -= 1  # we don't expect this for factions
        # TODO: select a new plan

class Resistance(Group):
    """Resistance Group
    """
    START_SIZE=.1
    START_INFORMED=.1
    START_SMART=.1
    START_LOYAL=.1
    START_RICH=.1
    MAX_PLANS=3
    BASE_NEED_PLAN=Game.LOW
    NEED_PLAN_TURN_FACTOR=1.2
    INACTION_LOSS=.05
    visibility = RecordedAttribute('visibility')

    def __repr__(self):
        return '{{{Resistance:%s}}}'%(self.name)

    def __init__(self, name, size, informed, smart, loyal, rich, buffs,
            visibility, modus_operandi, need_plan):
        super(Resistance, self).__init__(name, size, informed, smart, loyal,
            rich, buffs)
        # how obvious to the local Faction, how easy to find
        self.visibility = visibility
        # style of actions to select from with chance of each
        self.modus_operandi = modus_operandi
        self.need_plan = need_plan  # bonus to chance to find a new plan

    def json_dump(self):
        v = super(Resistance, self).json_dump()
        v.update(self.json_dump_simple('visibility_value', 'visibility_base',
            'visibility_history'))
        v.update(self.json_dump_simple('modus_operandi', 'need_plan'))
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return super(Resistance, cls).json_create_args(jdata) + [0, 0, 0]

    def json_load(self, jdata):
        super(Resistance, self).json_load(jdata)
        self.visibility_value = jdata['.visibility_value']
        self.visibility_base = jdata['.visibility_base']
        self.visibility_history = jdata['.visibility_history']
        self.modus_operandi = jdata['.modus_operandi']
        self.need_plan = jdata['.need_plan']

    def search_for_plan(self, num_plans, ui):
        '''
        Resistance groups search for more plans:
            low chance of success if they have other plans already
              (lower the more plans they have, reducing to 0 when they have
              two or three on the boil)
            higher if they have no plans yet
              (and rising over successive turns with no plan?)
        '''
        find_plan = Game.MED * ((self.MAX_PLANS - num_plans)/self.MAX_PLANS)
        found = roll(find_plan, self.buffed('need_plan'))
        if found > 0:
            ui.msg('resistance group %s should find a plan'%self.name)
            # TODO: select new plan based on self.modus_operandi and zone???
            # this doesn't work because I need zone...
            # zone = ???
            # new_plan = Plan("newplan", zone, self, self.modus_operandi,
            #     "a new plan", 1+random.randint(1,4), [])
            # ui.msg('%s found a new plan: '%self.name, new_plan.name)
            # add new plan to self.plans
            # self.plans.append(new_plan)

    def update(self, game, ui):
        '''
        Resistance groups with no plan suffer a loss of loyalty
        Resistance groups with plans ready to go, enact them
        Resistance groups suffer an erosion of size when they do not enact
            any action, amount depending on loyalty
        Resistance groups with plans to work on, advance them by a turn
        Resistance groups search for plans if they do not have enough
        '''
        if self.size <= 0:
            return  # we are dead and should do nothing
        ui.msg('Resistance group %s: update'%self.name)
        super(Resistance, self).update(game, ui)
        num_plans = len(self.plans)
        if num_plans == 0:
            # loss of loyalty, note need_plan could be a factor
            if not self.need_plan:
                self.need_plan = self.BASE_NEED_PLAN
            else:
                self.need_plan = min(1.,
                    self.need_plan * self.NEED_PLAN_TURN_FACTOR)
        else:
            self.need_plan = 0  # not urgent any more
            # do we have a plan ready to go?
            ready_plans = []
            for plan in self.plans:
                if plan.plan_time == 0:
                    ready_plans.append(plan)
                    # remove from self.plans
                    self.plans.remove(plan)
            if len(ready_plans):
                # enact plans
                for plan in ready_plans:
                    plan.enact(ui)
            else:
                # get smaller, based on loyalty
                self.size = max(0,
                    self.size - (self.INACTION_LOSS * (1-self.buffed('loyalty'))))
            for plan in self.plans:
                # advance plan by a turn (more with smarts roll?)
                plan.plan_time -= 1
        # increase visibility by local faction's alert
        # TODO: how do we know the local faction?
        # check for group dead
        if self.size <= 0:  # not buffed, only permanent counts for death
            self.size = 0
            # TODO: how do we remove this group?
            # TODO: tell player about group removal
            ui.msg('resistance group %s is dead'%self.name)
            pass
        if num_plans < self.MAX_PLANS:
            self.search_for_plan(num_plans, ui)
