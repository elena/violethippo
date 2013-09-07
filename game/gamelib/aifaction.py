import model

from gamelib.plans.base import Plan
import gamelib.plans.faction


IS_DEAD='0xdeadbeef'

FLAVORS={ model.INDUSTRY:[IS_DEAD],
          model.MILITARY:[IS_DEAD],
          model.LOGISTICS:[IS_DEAD],
        }



class   Brain(object):

    def make_plans(self,game,ui):
        flav=FLAVORS[ self.zone.name ]
        print 'brain for',[self,self.zone],flav
        plans=[]
        if IS_DEAD in flav:
            new_plan = Plan("factionplan", self, Plan.NOOP,
                            "a faction plan", 0, [])
            ui.msg('faction %s made a plan: %s'%(self.name, new_plan))
            plans.append( new_plan )
        else:
            pass
        return plans




