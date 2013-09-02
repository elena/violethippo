
import os
import json

from gamelib.plans.base import Plan


class JSONable(object):

    # take a list of simple variables to save....
    def json_dump_simple(self,*names):
        v={}
        for k in names:
            v['.'+k]=getattr(self,k)
        return v
    # restore anything simple.....
    def json_load_simple(self,jdata):
        v={}
        for k in jdata:
            if k.startswith('.'):
                v[k]=setattr(self,k[1:],jdata[k])
        return v

    # create an object from a json save.
    @classmethod
    def json_create(cls, jdata):
        o = cls( *cls.json_create_args(jdata) )
        o.json_load_simple(jdata)
        o.json_load(jdata)
        return o
    # handle __init__ args
    @classmethod
    def json_create_args(cls,jdata):
        return []
    # then load the extra (non simple) data bits... default to nothing to load
    def json_load(self,jdata):
        pass


class Game(JSONable):
    def __init__(self):
        self.player = Player()
        self.moon = Moon()
        self.turn = 0

    def json_savefile_turn(self,sdir):
        self.json_savefile(sdir,'turn_%03d.json'%(self.turn))
        self.json_savefile(sdir)
    def json_savefile(self,sdir,name=None):
        if not name:
          name='save.json'
        fd=open( os.path.join(sdir,name),'w' )
        json.dump( self.json_dump(), fd, indent=2,sort_keys=True )
        fd.close()
    @classmethod
    def json_loadfile(cls,sdir,name=None):
        if not name:
          name='save.json'
        jdata=json.load( open( os.path.join(sdir,name) ) )
        return cls.json_create(jdata)

    def json_dump(self):
        v=self.json_dump_simple('turn')
        v['player']=self.player.json_dump()
        v['moon']=self.moon.json_dump()
        return v
    def json_load(self, jdata):
        self.player=Player.json_create( jdata['player'] )
        self.moon=Moon.json_create( jdata['moon'] )


    def update(self, ui):
        # we pass in the Game instance and the UI from the top level so the
        # model objects don't need to hang on to them
        self.player.update(self, ui)
#        self.planet.update(self, ui)     # not defined
        self.moon.update(self, ui)
        #
        # save to be paranoid
        #
        self.json_savefile_turn( ui.savedir )
        self.turn+=1
        #
        # Check for game over condition..
        #
        threat=0
        for zone in self.moon.zones:
            threat+=zone.faction.threat
        if threat>1.2:
          raise ui.SIGNAL_GAMEOVER
        ui.msg('update done threat is %s'%(threat))


class Player(JSONable):
    """Represents the player's orders.

    Use actvity points per:

    one free player action (any player action, cost 0)
    each group support/discourage within the zone costs 1 activity point
    each group support/discourage outside the zone costs 2 activity points
    each additional player action costs 3 activity points (possibly some
        are more expensive when purchased this way)
    """
    def __init__(self):
        self.discovery_chance = 0
        self.visibility = 0   # affected by orders with "Instigator Noticeable"
        self.activity_points = 0

    def json_dump(self):
        return self.json_dump_simple('discovery_chance',
            'visibility', 'activity_points')


    def update(self, game,ui):
        ui.msg( '%s update not implemented' % self)


class Moon(JSONable):
    """Made up of N zones, each ruled by a Boss who has a Faction around him.
    Remote from the Planet, but controlling it economically, militarily, and
    politically. Its ability to project its power is the key to victory and so
    should be represented, or able to be derived from detailed zone/faction
    status.
    """
    def __init__(self):
        self.zones = []

    def json_dump(self):
        v=self.json_dump_simple()
        v['zones']=[ z.json_dump() for z in self.zones ]
        return v

    def json_load(self, jdata):
        self.zones=[ Zone.json_create(z) for z in jdata['zones'] ]

    def update(self, game, ui):
        ui.msg('%s updating moon'%(self))
        for zone in self.zones:
            zone.update(game,ui)


class Zone(JSONable):
    """Convert a raw material into a resource

    Contain two Cohorts (population groups)
    Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work
    Resource requirements must be met or dropoff in output.
    """
    def __init__(self,name):
        self.name=name
        self.requirements = []  # what raw materials are needed, how much
        self.provider = []      # what are created from what volume of inputs
        self.cohorts = [Privileged(), Servitor()]       # population groups
        self.faction = None
        self.resistance_groups = []   # list of resistance groups

    def json_dump(self):
        v=self.json_dump_simple('name')
        v['faction']=self.faction.json_dump()
        v['cohorts.priv']=self.cohorts[0].json_dump()
        v['cohorts.serv']=self.cohorts[1].json_dump()
        v['resistance_groups']=[ g.json_dump() for g in self.resistance_groups ]
        return v
    @classmethod
    def json_create_args(cls,jdata):
        return [ jdata['.name'] ]
    def json_load(self, jdata):
        self.cohorts=[ Privileged.json_create( jdata['cohorts.priv'] ),
                       Servitor.json_create( jdata['cohorts.serv'] ),
                     ]
        self.faction=Faction.json_create( jdata['faction'] )
        self.resistance_groups=[ Resistance.json_create(g) for g in jdata['resistance_groups'] ]


    def update(self, game, ui):
        ui.msg('%s updating zone'%(self))
        # do plans and orders
        for group in self.resistance_groups:
            group.update(game, ui)
        for group in self.cohorts:
            group.update(game, ui)
        self.faction.update(game, ui)
        #
        # Process Raw Materials and create Resources
        # (this needs work)
        produce=0
        for group in self.cohorts:
            produce+= group.update_production(game,ui,self)
        ui.msg('total produce=%s'%(produce))
        self.faction.rich+=produce


class Cohort(JSONable):
    """Each zone has at least two cohorts:

        Privileged - staff zone faction
        Servitor - create zone resource

    We must know how willing each cohort is to carry out its appointed task.
    And how easily resistance can be recruited/created from there. Willingness
    is derived from the way the cohort is treated.

    """
    def __init__(self):
        self.size = 0           # how many in population
        self.liberty = 0        # freedom from rules and monitoring
        self.quality_of_life = 0        # provided services
        self.cash = 0           # additional discretionary money

    def json_dump(self):
        return self.json_dump_simple('size','liberty','quality_of_life','cash')

    @property
    def willing(self):
        """Willingness can be forced through low liberty, or the product of
        high quality of life and cash in combination.
        """
        return min( self.liberty, (self.quality_of_life+self.cash)/2 )

    @property
    def rebellious(self):
        """Rebellion is caused by low liberty, quality of life, and cash.
        """
        return min( self.liberty, self.quality_of_life, self.cash )


    def update(self, game, ui):
        ui.msg( '%s update not implemented' % self)

    def update_production(self,game,ui,zone):
        produce=self.willing * self.size
        ui.msg( '%s produced: %s' %( self,produce) )
        return produce


class Privileged(Cohort):
    def __init__(self):
        super(Privileged, self).__init__()


class Servitor(Cohort):
    def __init__(self):
        super(Servitor, self).__init__()


class Group(JSONable):
    """A group of non-rabble that actually do stuff in the game.
    """
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.informed = 0
        self.smart = 0
        self.loyal = 0
        self.rich = 0
        self.buffs = []

    def json_dump(self):
        return self.json_dump_simple('name', 'size', 'informed', 'smart',
            'loyal', 'rich', 'buffs')
    @classmethod
    def json_create_args(cls,jdata):
        return [jdata['.name']]

    def update(self, game, ui):
        # Groups plan - plan the action they will take next turn
        # (not visible to player)
        ui.msg( '%s update not implemented' % self)


class Faction(Group):
    """Invader Factions
    Led by a boss
    Staffed by zone Privileged Cohort
    controls a power projector (threat to the planet)
    requires support (resource or resources)
    """
    def __init__(self,name):
        super(Faction, self).__init__(name)
        self.threat = 0     # potential power vs planet

    def json_dump(self):
        v=Group.json_dump(self)
        v.update( self.json_dump_simple( 'threat' ) )
        return v

    def update(self, game, ui):
        super(Faction, self).update(game, ui)
        # alter threat level against planet
        ui.msg( '%s update not implemented' % self)


class Resistance(Group):
    """Resistance Group
    """
    def __init__(self,name):
        super(Resistance, self).__init__(name)
        # how obvious to the local Faction, how easy to find
        self.visibility = 0
        # style of actions to select from with chance of each
        self.modus_operandi = Plan.TYPE_ESPIONAGE

    def json_dump(self):
        v=Group.json_dump(self)
        v.update(self.json_dump_simple('visibility', 'modus_operandi'))
        return v

    def update(self, game, ui):
        super(Resistance, self).update(game, ui)
        # alter threat level against planet
        ui.msg( '%s update not implemented' % self)
