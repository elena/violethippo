import model

from gamelib.plans import base,faction


#
# Yes, i am aware this is a horrible way to do this :)
# ... but its late and id rather not be bothered with repo collisions
# and saving stuff i can just re'lookup ;)
#

IS_DEAD='0xdeadbeef'

FLAVORS={ model.INDUSTRY:[],
          model.MILITARY:[],
          model.LOGISTICS:[],
        }



class   Brain(object):

    def make_plans(self,game,ui):
        flav=FLAVORS[ self.zone.name ]
        ui.msg( '%s brain for %s = %s'%(self,self.zone,flav))
        plans=[]
        if not IS_DEAD in flav:
            pass
#            plans.append(
#                faction.PatrolZone('patrol:%s:%s'%(self.name,game.turn), self )
#                )
#            plans.append(
#                faction.ForceProduction('ForceProduction:%s:%s'%(self.name,game.turn), self )
#                )

        if not plans:
            plans.append( base.Plan("idle:%s:%s"%(self.name,game.turn),
                            self, base.Plan.NOOP, "passing time",0, [])
                        )
        for p in plans:
            ui.msg('   brain.plan %s'%(p))
        return plans




