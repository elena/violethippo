
import os
import json
import time
import random

from gamelib.plans.base import Plan




ENFORCEMENT='enforcement'
RAW_MATERIAL='material'
GOODS='goods'
MANPOWER='lifeforms'






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
        print cls, args
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
        old_val = getattr(instance, self.name + '_value', None)
        if value == old_val:
            return
        if not hasattr(instance, self.name + '_history'):
            setattr(instance, self.name + '_history', [])
        if game is not None:
            turn = game.turn
            getattr(instance, self.name + '_history').append((turn, value))
        setattr(instance, self.name + '_value', value)


# this global will be set to the *current game* when convenient
game = None


class Game(JSONable):

    LOW=.1
    MED=.2
    HIGH=.4
    MAX=1.0

    EASE_LINEAR=0
    EASE_HERMITE=1
    EASE_QUAD=2
    EASE_CUBIC=3

    def __init__(self):
        self.moon = Moon()
        self.player = Player()
        self.turn = 0
        self.calculate_threat()
        self.created = time.time()
        self.turn_date = time.time()
        self.game_over = False
        self.player.visibility = len(self.moon.zones)
        #
        # Seed for repeatable testing
        #
        # random.seed(1)
        #

    def json_savefile_turn(self):
        p = self.json_path
        fn, ext = os.path.splitext(p)
        self.json_savefile('%s_turn_%03d.json' % (fn, self.turn))
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
        v = self.json_dump_simple('turn', 'threat', 'created', 'turn_date',
            'game_over')
        v['player'] = self.player.json_dump()
        v['moon'] = self.moon.json_dump()
        return v

    def json_load(self, jdata):
        self.moon = Moon.json_create(jdata['moon'])
        self.player = Player.json_create(jdata['player'])

    def update(self, ui):
        ui.msg('-'*70)
        ui.msg('game: update starting. turn %s'%(self.turn))
        ui.msg('-'*70)
        self.turn_date = time.time()
        # we pass in the Game instance and the UI from the top level so the
        # model objects don't need to hang on to them
        self.player.update(self, ui)
#        self.planet.update(self, ui)     # not defined
        self.moon.update(self, ui)
        #
        # save to be paranoid
        #
        self.json_savefile_turn()
        self.turn+=1
        #
        # Check for game over condition..
        #
        self.calculate_threat()
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
        #     ret = self.roll(0.2, 0.3)
        #     if ret > 0:
        #         win += 1
        #         tot += ret
        # print "rolled: %d wins, avg: %.3f" % (win, (tot/win))
        #
        ui.msg('game: update done. now turn %s'%(self.turn))

    def calculate_threat(self):
        self.threat = 0
        for zone in self.moon.zones:
            self.threat += self.moon.zones[zone].faction.threat

    def roll(self, d1, d2=0.0):
        total = d1+d2
        if total >= 1.:
            return max(random.random(), random.random()) + (total - 1.)
        #
        # Use if want to extend optimal requirements (lower chance of success)
        # if total > 1.5:
        #     return total - .5
        # total *= 2./3.
        #
        total = self.ease(total)
        ran = random.random()
        return max(0, total-ran)

    def ease(self, total, ease=EASE_CUBIC):
        if ease == self.EASE_LINEAR:
            return total
        elif ease == self.EASE_HERMITE:
            return (3 * total**2) - (2 * total**3)
        elif ease == self.EASE_QUAD:
            total *= 2
            if total < 1:
                return .5 * total**2
            total -= 1
            return -.5 * (total*(total-2) - 1)
        elif ease == self.EASE_CUBIC:
            total *= 2
            if total < 1:
               return .5 * total**3
            total -= 2
            return .5 * (total**3 + 2)
        else:
            return 0



class Player(JSONable):
    """Represents the player's orders.

    Use actvity points per:

    one free player action (any player action, cost 0)
    each group support/discourage within the zone costs 1 activity point
    each group support/discourage outside the zone costs 2 activity points
    each additional player action costs 3 activity points (possibly some
        are more expensive when purchased this way)
    """
    def __init__(self, visibility=0, activity_points=0, hideout=None):
        self.discovery_chance = 0    # TODO I think this is unnecessary...
        self.visibility = visibility   # affected by orders with "Instigator Noticeable"
        self.activity_points = activity_points
        self.hideout = hideout   # one of the zone types, player must choose

    def json_dump(self):
        return self.json_dump_simple('visibility', 'activity_points',
            'hideout')

    @classmethod
    def json_create_args(cls,jdata):
        return [jdata['.visibility'], jdata['.activity_points'],
            jdata['.hideout']]

    def update(self, game,ui):
        self.visibility = len(game.moon.zones)
        for zone in game.moon.zones:
            self.visibility -= game.moon.zones[zone].player_found
        # ui.msg('%s update not implemented' % self)


class Moon(JSONable):
    """Made up of N zones, each ruled by a Boss who has a Faction around him.
    Remote from the Planet, but controlling it economically, militarily, and
    politically. Its ability to project its power is the key to victory and so
    should be represented, or able to be derived from detailed zone/faction
    status.
    """
    def __init__(self):
        self.zones = dict(
            industry=Zone.create_industry(),
            military=Zone.create_military(),
            logistics=Zone.create_logistics()
        )

    def json_dump(self):
        v = self.json_dump_simple()
        v['zones'] = dict((z, self.zones[z].json_dump()) for z in self.zones)
        return v

    def json_load(self, jdata):
        self.zones = dict((z, Zone.json_create(jdata['zones'][z]))
            for z in jdata['zones'])

    def update(self, game, ui):
        ui.msg('%s updating moon'%(self))
        for zone in self.zones:
            self.zones[zone].update(game,ui)


class Zone(JSONable):
    """Convert a raw material into a resource

    Contain two Cohorts (population groups)
    Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work
    Resource requirements must be met or dropoff in output.
    """
    def __init__(self, name):
        self.name = name
        # economy / production
        self.requirements = []  # what raw materials are needed, how much
        self.provides = []      # what are created from what volume of inputs
        self.store= {}          # moving stuff around
        # groups
        self.privileged = None  # privileged cohort
        self.servitor = None    # servitor cohort
        self.faction = None
        self.player_found = 0  # close to finding player in zone

    @classmethod
    def create_industry(cls):
        o = cls('industry')
        o.requirements=[ ENFORCEMENT, RAW_MATERIAL ]
        o.provides=[ GOODS ]
        o.privileged = Privileged(size=Game.MED, liberty=Game.MED,
                quality_of_life=Game.HIGH, cash=Game.HIGH)
        o.servitor = Servitor(size=Game.MAX, liberty=Game.LOW,
                quality_of_life=Game.LOW, cash=Game.MED)
        o.faction = Faction('ecobaddy', alert=.01, threat=Game.MAX,
            size=Game.MED, informed=Game.HIGH, smart=Game.LOW, loyal=Game.MED,
            rich=Game.HIGH, buffs=[])
        o.privileged.resistance_groups = [Resistance('industry-res-1',
            size=Game.HIGH, informed=Game.LOW, smart=Game.LOW, loyal=Game.LOW,
            rich=Game.LOW, buffs=[], visibility=Game.LOW,
            modus_operandi=Plan.TYPE_VIOLENCE)]
        o.servitor.resistance_groups = [Resistance('industry-res-2',
            size=Game.LOW, informed=Game.MED, smart=Game.LOW, loyal=Game.LOW,
            rich=Game.LOW, buffs=[], visibility=Game.LOW,
            modus_operandi=Plan.TYPE_SABOTAGE)]
        return o

    @classmethod
    def create_military(cls):
        o = cls('military')
        o.requirements= [MANPOWER, GOODS]
        o.provides= [ ENFORCEMENT ]
        o.privileged = Privileged(size=Game.LOW, liberty=Game.HIGH,
                quality_of_life=Game.HIGH, cash=Game.HIGH)
        o.servitor = Servitor(size=Game.MED, liberty=Game.HIGH,
                quality_of_life=Game.MED, cash=Game.MED)
        o.faction = Faction('mrstompy', alert=.01, threat=Game.MAX,
            size=Game.HIGH, informed=Game.LOW, smart=Game.MED, loyal=Game.HIGH,
            rich=Game.LOW, buffs=[])
        o.servitor.resistance_groups = [Resistance('military-res-1',
            size=Game.LOW, informed=Game.MED, smart=Game.MED, loyal=Game.HIGH,
            rich=Game.MED, buffs=[], visibility=Game.LOW,
            modus_operandi=Plan.TYPE_VIOLENCE)]
        return o

    @classmethod
    def create_logistics(cls):
        o = cls('logistics')
        o.requirements= [ENFORCEMENT,GOODS]
        o.provides= [RAW_MATERIAL,MANPOWER]
        o.privileged = Privileged(size=Game.MED, liberty=Game.HIGH,
                quality_of_life=Game.HIGH, cash=Game.HIGH)
        o.servitor = Servitor(size=Game.LOW, liberty=Game.MED,
                quality_of_life=Game.HIGH, cash=Game.MED)
        o.faction = Faction('mrfedex', alert=.02, threat=Game.MAX,
            size=Game.LOW, informed=Game.MED, smart=Game.HIGH, loyal=Game.HIGH,
            rich=Game.MED, buffs=[])
        o.privileged.resistance_groups = [Resistance('logistics-res-1',
            size=Game.MED, informed=Game.HIGH, smart=Game.HIGH, loyal=Game.MED,
            rich=Game.HIGH, buffs=[], visibility=Game.LOW,
            modus_operandi=Plan.TYPE_SABOTAGE)]
        o.servitor.resistance_groups = [Resistance('logistics-res-2',
            size=Game.MED, informed=Game.HIGH, smart=Game.HIGH, loyal=Game.MED,
            rich=Game.HIGH, buffs=[], visibility=Game.LOW,
            modus_operandi=Plan.TYPE_ESPIONAGE)]
        return o

    def json_dump(self):
        v = self.json_dump_simple('name', 'requirements', 'player_found')
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
        # Process Raw Materials and create Resources
        # (this needs work)
        prodbase=self.privileged.production_output_turn0* self.servitor.production_output_turn0
        prodcurr=self.privileged.production_output()* self.servitor.production_output()
        # requires impacts this too
        output=int(100*prodcurr/prodbase)
        ui.msg('ZONE: %s'%(self.name))
        ui.msg('   store: %s'%(self.store) )
        ui.msg('   req: %s'%(self.requirements) )
        ui.msg('   provides: %s'%(self.provides))
        ui.msg('     priv:base: %s'%(self.privileged.production_output_turn0))
        ui.msg('     serv:base: %s'%(self.servitor.production_output_turn0))
        ui.msg('     priv:curr: %s'%(self.privileged.production_output()))
        ui.msg('     serv:curr: %s'%(self.servitor.production_output()))
        ui.msg('   base: %s  curr: %s'%(prodbase,prodcurr))
        ui.msg('   prod: %s(percent)'%( output ))
        for prod in self.provides:
            if prod not in self.store:
                self.store[ prod ]=0
            self.store[ prod ] += output
            ui.msg('   prod: %s%% %s '%( output,self.store[prod] ))
        ui.msg('   store: %s'%( self.store ))
        # test for killing output
        ui.msg('      killing qol',self.privileged.quality_of_life)
        self.privileged.quality_of_life=self.privileged.quality_of_life*.4
        ui.msg('      killed qol',self.privileged.quality_of_life)
        #
        # continue to search for the player
        if self.player_found < 1:
            self.player_found += self.faction.alert
            self.player_found = min(self.player_found, 1)
            ui.msg('player found in %s: %f'%(self.name, self.player_found))



    def produce(self,boss,workers):
      return workers * boss




class Cohort(JSONable):
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

    def __init__(self, size, liberty, quality_of_life, cash):
        self.size = size           # how many in population
        self.liberty = liberty        # freedom from rules and monitoring
        self.quality_of_life = quality_of_life        # provided services
        self.cash = cash           # additional discretionary money
        self.resistance_groups = []   # list of resistance groups
        self.production_output_turn0=self.production_output()

    def json_dump(self):
        names = []
        for name in ['size', 'liberty', 'quality_of_life', 'cash']:
            names.append(name + '_value')
            names.append(name + '_history')
        names.append('production_output_turn0')
        v = self.json_dump_simple(*names)
        v['resistance_groups'] = [g.json_dump()
            for g in self.resistance_groups]
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just pretend it's all ok - json_load will fix things
        return [0, 0, 0, 0]

    def json_load(self, jdata):
        for name in ['size', 'liberty', 'quality_of_life', 'cash']:
            setattr(self, name + '_value', jdata['.%s_value' % name])
            setattr(self, name + '_history', jdata['.%s_history' % name])
        self.production_output_turn0=jdata['.production_output_turn0']
        self.resistance_groups = [Resistance.json_create(g)
            for g in jdata['resistance_groups']]

    @property
    def willing(self):
        """Servitors: Willingness can be forced through low liberty,
           or the product of high quality of life and cash in combination.
        """
        return max(1.-self.liberty, (self.quality_of_life + self.cash)/2)


    @property
    def efficiency(self):
        """priv: efficiency is mostly QOL and somewhat influenced by
        liberty and cash
        """
        return (2* self.quality_of_life + self.quality_of_life + self.cash)/4



    @property
    def rebellious(self):
        """Rebellion is caused by low liberty, quality of life, and cash.
        """
        return min(self.liberty, self.quality_of_life, self.cash)

    def update(self, game, ui):
        for group in self.resistance_groups:
            group.update(game, ui)
        ui.msg('%s update not implemented' % self)







class Privileged(Cohort):
    def production_output(self):
        return self.efficiency


class Servitor(Cohort):
    def production_output(self):
        return self.willing





class Group(JSONable):
    """A group of non-rabble that actually do stuff in the game.
    """
    size = RecordedAttribute('size')
    informed = RecordedAttribute('informed')
    smart = RecordedAttribute('smart')
    loyal = RecordedAttribute('loyal')
    rich = RecordedAttribute('rich')

    def __init__(self, name, size, informed, smart, loyal, rich, buffs):
        self.name = name
        self.size = size
        self.informed = informed
        self.smart = smart
        self.loyal = loyal
        self.rich = rich
        self.buffs = buffs

    def json_dump(self):
        names = ['buffs', 'name']
        for name in ['size', 'informed', 'smart', 'loyal', 'rich']:
            names.append(name + '_value')
            names.append(name + '_history')
        return self.json_dump_simple(*names)

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return [jdata['.name'], 0, 0, 0, 0, 0, jdata['.buffs']]

    def json_load(self, jdata):
        for name in ['size', 'informed', 'smart', 'loyal', 'rich']:
            setattr(self, name + '_value', jdata['.%s_value' % name])
            setattr(self, name + '_history', jdata['.%s_history' % name])

    def update(self, game, ui):
        # Groups plan - plan the action they will take next turn
        # (not visible to player)
        ui.msg('%s update not implemented' % self)

    @property
    def state(self):
        # TODO
        # State is primarily based on our damage below starting stats
        # perhaps our highest starting stats matter most
        # should include the effects of temporary buffs
        return 1.0

    @property
    def state_description(self):
        st = self.state
        if st > .5:
            return 'strong'
        if st > .2:
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
    threat = RecordedAttribute('threat')

    def __init__(self, name, size, informed, smart, loyal, rich, buffs,
            threat, alert):
        super(Faction, self).__init__(name, size, informed, smart, loyal, rich,
            buffs)
        self.threat = threat     # potential power vs planet
        self.alert = alert       # awareness of rebellion and player

    def json_dump(self):
        v = super(Faction, self).json_dump()
        v.update(self.json_dump_simple('threat_value', 'threat_history', 'alert'))
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return super(Faction, cls).json_create_args(jdata) + [0, 0]

    def json_load(self, jdata):
        super(Faction, self).json_load(jdata)
        self.threat_value = jdata['.threat_value']
        self.threat_history = jdata['.threat_history']

    def update(self, game, ui):
        super(Faction, self).update(game, ui)
        # alter threat level against planet
        ui.msg('%s update not implemented' % self)


class Resistance(Group):
    """Resistance Group
    """
    visibility = RecordedAttribute('visibility')
    modus_operandi = RecordedAttribute('modus_operandi')

    def __init__(self, name, size, informed, smart, loyal, rich, buffs,
            visibility, modus_operandi):
        super(Resistance, self).__init__(name, size, informed, smart, loyal,
            rich, buffs)
        # how obvious to the local Faction, how easy to find
        self.visibility = visibility
        # style of actions to select from with chance of each
        self.modus_operandi = modus_operandi

    def json_dump(self):
        v = super(Resistance, self).json_dump()
        v.update(self.json_dump_simple('visibility_value', 'visibility_history'))
        v.update(self.json_dump_simple('modus_operandi_value', 'modus_operandi_history'))
        return v

    @classmethod
    def json_create_args(cls, jdata):
        # just dummy values that'll be filled in by load below
        return super(Resistance, cls).json_create_args(jdata) + [0, 0]

    def json_load(self, jdata):
        super(Resistance, self).json_load(jdata)
        self.visibility_value = jdata['.visibility_value']
        self.visibility_history = jdata['.visibility_history']
        self.modus_operandi_value = jdata['.modus_operandi_value']
        self.modus_operandi_history = jdata['.modus_operandi_history']

    def update(self, game, ui):
        super(Resistance, self).update(game, ui)
        # alter threat level against planet
        ui.msg('%s update not implemented' % self)
