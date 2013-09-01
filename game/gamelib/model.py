class Game:
    def __init__(self):
        self.player = Player()
        self.planet = Planet()
        self.moon = Moon()
        self.factions = []
        self.resistance = []

    def update(self, game, ui):
        # we pass in the Game instance and the UI from the top level so the
        # model objects don't need to hang on to them
        self.player.update(self, ui)
        for group in self.factions + self.resistance:
            group.update(self, ui)
        self.planet.update(self, ui)
        self.moon.update(self, ui)
        self.player.calculate_discovery_chance(self, ui)


class Player:
    """Represents the player's orders.
    """
    def __init__(self):
        self.orders = []
        self.discovery_chance = 0
        self.visibility = 0     # Richard made this up "Instigator Noticeable"
        self.activity_points = 0

    def update(self, game, ui):
        for order in self.orders:
            order.enact(game, ui)
        self.orders = []

    def calculate_discovery_chance(self, game, ui):
        raise NotImplementedError()

    def add_order(self, order):
        """Use actvity points per:

        one free player action (any player action, cost 0)
        each group support/discourage within the zone costs 1 activity point
        each group support/discourage outside the zone costs 2 activity points
        each additional player action costs 3 activity points (possibly some
            are more expensive when purchased this way)
        """
        total_cost = 0
        for order in self.orders:
            # add order cost
            # note player action to incur additional player action cost
        # add on new order cost
        # REJECT if cost > self.activity_points
        self.orders.append(order)

class Planet:
    """This is an infinite resource of natives who are sufficiently removed
    from the action that they cannot have direct effect. They are the people
    being fought for, but that may not require any functional detail. May
    require a mood that reflects how easy it is to recruit, but that might be
    fixed (based on difficulty, ultimately?).
    """
    loyalty = 1.0

    def gather_people(self, number):
        return int(number * self.loyalty)


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
    """Convert a raw material into a resource Contain two or more Cohorts
    (population groups) Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work Resource requirements must be
    met or dropoff in output.
    """
    def __init__(self):
        self.requirements = []  # what raw materials are needed, how much
        self.provider = []      # what are created from what volume of inputs
        self.cohorts = []       # population groups

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

    Willingness can be forced through low liberty, or the product of high
    quality of life and cash in combination.

    Rebellion is caused by low liberty, quality of life, and cash.
    """
    def __init___(self):
        self.size = 0           # how many in population
        self.liberty = 0        # freedom from rules and monitoring
        self.quality_of_life = 0        # provided services
        self.cash = 0           # additional discretionary money
        self.willing = 0        # hardworking
        self.rebellious = 0     # ability to be recruited to rebellion

    def update(self, game, ui):
        raise NotImplementedError('%s update not implemented' % self)


class Privileged(Cohort):
    pass


class Servitor(Cohort):
    pass


class Faction(Cohort):
    """Invader Factions
    Led by a boss
    Staffed by zone Privileged Cohort
    controls a power projector (threat to the planet)
    requires support (resource or resources)
    Threat - potential power vs planet
    Numbers
    Informed
    Smart
    Loyal
    Rich?
    """
    def update(self, game, ui):
        # Factions plan - factions plan the action they will take next turn
        # (not visible to player)
        raise NotImplementedError()

class Resistance(Cohort):
    """Resistance Groups
    Numbers - how large, physically powerful in an open fight
    Informed - how connected to information sources
    Smart - technology available and used (multiplier for Numbers and Informed in some cases)
    Loyal - willing to die for the cause
    Rich - do we need wealth?
    Noteable - how obvious to the local Faction, how easy to find
    list Modus Operandi - style of actions to select from with chance of each
    """

