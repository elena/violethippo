
'''
Patrol - reduce rebellious this turn
Root out Resistance - search for most visible resistance in a Cohort; prevents visibility from dropping this turn for other Groups in the Cohort?
Assault Known Resistance Group - direct attack
Upgrade equipment - increase Smarts
Increase Funding
Suppress cohort - reduce liberty (to increase willingness) for a turn/permanently
Alter cohort stats - various deliberate changes possible, with fallout for each
Recruit? - not sure if this should be possible, other than to recover what was lost
Defend particular target (eg. production, or a cohort, or the Faction) - reduce chance of success of relevant actions this turn, increase visibility cost
Informants - intel on planned actions for next turn (and/or targets)
Search for player
'''

from gamelib.plans.base import Plan


class Patrol(Plan):
    """Increases difficulty of resistance groups operations
    """
