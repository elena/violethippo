
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


class PatrolZone(Plan):
    """Increases visibility of resistance groups for all resistance in
       zone for a while (if sucessful).
    """
    def __init__(self,name,actor):
        Plan.__init__(self,name,actor,
                      Plan.ESPIONAGE,
                      'looking for rebel groups in area %s'%(actor.zone.name),
                      0,['informed','smart'],['smart','loyal'])

    def check_success(self, ui):
        return 1


    def apply_effects(self,ui):
        a=self.actor
        z=self.actor.zone
        ui.msg('    brain.>>>: %s / %s'%(self.attack_stats,self.defend_stats))
        for c in [self.actor.zone.privileged,self.actor.zone.servitor]:
            for r in c.resistance_groups:
                roll=self.mechanics( a, r )
                ui.msg('    brain.attacking: %s %s'%(r.name,roll))
                if roll>0:
                    r.buff_stat('visibility',.1,.05,.025,.025)
                    ui.msg('   brain.      2 %s  %s'%(r.name,r.buffed('visibility')))
                else:
                    ui.msg('   brain.  missed')


class ForceProduction(Plan):
    """Force production 
            servitor liberty down
            privileged qol up.
    """
    def __init__(self,name,actor):
        Plan.__init__(self,name,actor,
                      Plan.ESPIONAGE,
                      'boosting production in area %s'%(actor.zone.name),
                      0,['size','rich'],[],None,[],[],[('privileged',('quality_of_life',(.1,.1,.1,.1))),('servitor',('liberty',(-.1,-.1,-.1,-.1)))])






