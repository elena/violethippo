class Game:
    def __init__(self):
        self.player = Player()
        self.moon = Moon()
        self.factions = []
        self.resistance = []

    def to_json(self, filename):
        # dump my state to a file to save it
        raise NotImplementedError()

    @classmethod
    def from_json(cls, filename):
        o = cls()
        # load my state from a file
        raise NotImplementedError()
        return o

    def update(self, ui):
        # we pass in the Game instance and the UI from the top level so the
        # model objects don't need to hang on to them
        self.player.update(self, ui)
        for group in self.factions + self.resistance:
            group.update(self, ui)
        self.planet.update(self, ui)
        self.moon.update(self, ui)
        # tally planet threat, check for game over
        raise NotImplementedError()


class Player:
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


class Moon:
    """Made up of N zones, each ruled by a Boss who has a Faction around him.
    Remote from the Planet, but controlling it economically, militarily, and
    politically. Its ability to project its power is the key to victory and so
    should be represented, or able to be derived from detailed zone/faction
    status.
    """
    def __init__(self):
        self.zones = []

    def update(self, game, ui):
        for zone in self.zones:
            zone.update(ui)


class Zone:
    """Convert a raw material into a resource

    Contain two Cohorts (population groups)
    Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work
    Resource requirements must be met or dropoff in output.
    """
    def __init__(self):
        self.requirements = []  # what raw materials are needed, how much
        self.provider = []      # what are created from what volume of inputs
        self.cohorts = [Privileged(), Servitor()]       # population groups
        self.faction = Faction(type)
        self.resistance_groups = []   # list of resistance groups

    def update(self, game, ui):
        # Process Raw Materials and create Resources
        raise NotImplementedError('%s update not implemented' % self)


class Cohort:
    """Each zone has at least two cohorts:

        Privileged - staff zone faction
        Servitor - create zone resource

    We must know how willing each cohort is to carry out its appointed task.
    And how easily resistance can be recruited/created from there. Willingness
    is derived from the way the cohort is treated.

    """
    def __init___(self):
        self.size = 0           # how many in population
        self.liberty = 0        # freedom from rules and monitoring
        self.quality_of_life = 0        # provided services
        self.cash = 0           # additional discretionary money

    def update(self, game, ui):
        raise NotImplementedError('%s update not implemented' % self)

    @property
    def willing(self):
        """Willingness can be forced through low liberty, or the product of
        high quality of life and cash in combination.
        """
        pass

    @property
    def rebellious(self):
        """Rebellion is caused by low liberty, quality of life, and cash.
        """
        pass


class Privileged(Cohort):
    pass


class Servitor(Cohort):
    pass


class Group:
    """A group of non-rabble that actually do stuff in the game.
    """
    def __init__(self):
        self.size = 0
        self.informed = 0
        self.smart = 0
        self.loyal = 0
        self.rich = 0
        self.buffs = []

    def update(self, game, ui):
        # Groups plan - plan the action they will take next turn
        # (not visible to player)
        raise NotImplementedError()


class Faction(Group):
    """Invader Factions
    Led by a boss
    Staffed by zone Privileged Cohort
    controls a power projector (threat to the planet)
    requires support (resource or resources)
    """
    def __init__(self):
        super(Faction, self).__init__()
        self.threat = 0     # potential power vs planet

    def update(self, game, ui):
        super(Faction, self).update(game, ui)
        # alter threat level against planet
        raise NotImplementedError()


class Resistance(Group):
    """Resistance Group
    """
    def __init__(self):
        super(Resistance, self).__init__()
        # how obvious to the local Faction, how easy to find
        self.visibility = 0
        # style of actions to select from with chance of each
        self.modus_operandi = Plan.TYPE_ESPIONAGE
