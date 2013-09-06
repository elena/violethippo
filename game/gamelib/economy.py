
import model

ENFORCEMENT='enforcement'
RAW_MATERIAL='material'
GOODS='goods'
MANPOWER='lifeforms'





class Zone_Economy(object):
    """Convert a raw material into a resource

    Contain two Cohorts (population groups)
    Contain and are owned by a single Invader Faction
    Utilize Servitor Cohort to carry out work
    Resource requirements must be met or dropoff in output.
    """
    def __init__(self):
        # economy / production
        self.requirements = []  # what raw materials are needed, how much
        self.provides = []      # what are created from what volume of inputs
        self.store= {}          # moving stuff around

    def setup_turn0(self):
        for n in self.requirements + self.provides:
            # print '>>>>00000 Creating:',self.name,n
            self.store[n]=10.


    def economy_use_goods(self,game,ui,goods):
        #
        # goods are used by 'people' and impact happiness etc
        ui.msg('  USE goods:  %s %s'%(self.name,goods))
        for co in [ self.privileged, self.servitor]:
            co.quality_of_life= co.quality_of_life_base * min(10.,goods+1.)/10.
            ui.msg('    setting qol %s * %s = %s'%(co.quality_of_life_base,goods/10.,co.quality_of_life))

    def economy_consume_goods(self,game,ui,goods):
        ui.msg('   EAT goods:  %s %s'%(self.name,self.store))
        self.store[model.GOODS]=min(0, self.store[model.GOODS]-goods)
        ui.msg('            :  %s %s'%(self.name,self.store))

    def economy_consume_rest(self,game,ui):
        #
        # Consume: in factory
        self.supply_efficiency=10.
        for n in self.requirements:
            self.supply_efficiency=min( self.supply_efficiency,
                                        self.store.get(n,0)
                                      )
        ui.msg('    %s         %s %s'%(self.name,self.supply_efficiency,self.requirements))
        ui.msg('    %s %s'%(self.name,self.store) )
        for n in self.requirements:
            if n not in self.store:
                self.store[n]=0
            self.store[n]-= self.supply_efficiency
        self.supply_efficiency=min( self.supply_efficiency+.5,10.)
        ui.msg('    %s %s final eff %s'%(self.name,self.store,self.supply_efficiency) )

    def economy_transport(self,game,ui):
        #
        # Transport:
        ui.msg('ZONE.economy: production.transport %s'%(self.name))
        for n in self.provides:
            trans=self.store.get(n,0)
            self.store[n]-=trans
            for z in game.moon.zones.values():
                if n in z.requirements:
                    if z!=self:
                        z.store[n]+=trans
                        ui.msg('     mv %s->-%s: %s %s'%(self.name,z.name,n,trans))
        ui.msg('  +++      store: %s'%(self.store) )



    def economy_produce(self, game, ui):
        # Process Raw Materials and create Resources
        # (this needs work)
        #
        # To pipeline the economy, we must:
        #     consume, transport, produce
        #     those first two steps have been done already
        #
        # Produce:
        ui.msg('ZONE.economy: produce %s'%(self.name))
        ui.msg('  +++final pre store: %s'%(self.store) )
        prodbase=self.produce( self.privileged.production_output_turn0,
                               self.servitor.production_output_turn0 )
        prodcurr=self.produce( self.privileged.production_output(),
                               self.servitor.production_output() )
        # requires impacts this too
        output=self.supply_efficiency*prodcurr/prodbase
        ui.msg('   supply use (max 10): %s'%(self.supply_efficiency))
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
            self.store[ prod ] = min( self.store[ prod ]+output, 11. )
            ui.msg('   ......prod: %s %s -> %s '%( prod, output,self.store[prod] ))
        ui.msg('  +++final prod store: %s'%(self.store) )



    def produce(self,boss,workers):
      return workers * boss

