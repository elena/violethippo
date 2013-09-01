# note: Order vs Plan (plans are what NPCs do)
class Order:
    """The player has X activity points to spend for the turn, and may take
    one free personal action at any point during the phase, in addition to any
    further actions they wish to purchase. activity points will be a base per
    turn, but might be affected by previous actions or different levels of
    difficulty or different player character stats (race or class/skills).
    """
    pass


class Hideout:
    """Establish/Move hideout - select a zone, adds to time until caught
    (harder to apply support points to groups in other zones? most player
    orders only in same zone as hideout?) Note: first turn this is the
    player’s first order, and must be done before any support is allocated
    """


class ZoneIntel:
    """Information on the disposition of the cohorts and the zone itself. We
    want the player to do this when they arrive (second turn) because they
    really need to know this stuff, and be worth doing every now and then
    later on. Information on cohorts might be along the lines of “biggest
    problem is xxx”, along with general information on their sizes and
    functions in the zone? Perhaps several levels of info requiring several
    successive attempts (not necessarily one after another)?
    """


class InfiltrateFaction:
    """uncover information that might be useful in working out what the
    Faction is doing this turn (an already planned action) which might enable
    the player to warn the groups through discouraging or encouraging specific
    plans, as well as showing more detailed indication of the faction’s
    current status?
    """


class LocateResistance:
    """locate resistance groups
    """


class Funding:
    """Seek funding source - prepare for Develop Group on a later turn
    """


class DevelopGroup:
    """Enhance a group’s stat (Smarts, Informed, Rich)
    """


class MakeAPlan:
    """Reveal a potential plan and assign it to a group (or forget it),
    perhaps select style of plan? Or presented with brief summary of three and
    you select one?
    """


class MovePlan:
    """Take a plan from one group and give it to another (this will likely
    affect its chance of success, as the groups will be unlikely to have the
    same stats)
    """


class Sabotage:
    """Reduce production efficiency for this turn?
    """


class Disrupt:
    """Interdict faction plan reducing its chance of success
    """


class Frame:
    """Plant evidence (situational must have evidence and conditions to make
    it relevant)
    """


class Steal:
    """Steal something
    """


class RemoveResistanceLeader:
    """Changes the modus operandi for the group, potentially affects its other
    stats negatively, potentially disbanding the group
    """


class AttackFactionLeader:
    """When a Faction is weakened enough, this should become available, and
    allow the player to permanently reduce the zone/faction to providing
    minimal resources, taking no Faction actions. But also increases awareness
    for all other Factions significantly
    """
