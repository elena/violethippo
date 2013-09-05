

ENFORCEMENT='enforcement'
RAW_MATERIAL='material'
GOODS='goods'
MANPOWER='lifeforms'





class Zone_Economy:
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
            self.store[n]=100.


    def economy_consume(self,game,ui):
        #
        # Consume:
        ui.msg('ZONE.economy: production.consume %s'%(self.name))
        self.supply_use=100
        for n in self.requirements:
            self.supply_use=min( self.supply_use, self.store.get(n,0) )
        ui.msg('  +++pre   consume store: %s'%(self.store) )
        for n in self.requirements:
            ui.msg('     consume: %s %s'%(n,self.supply_use))
            if n not in self.store:
                self.store[n]=0
            self.store[n]-= self.supply_use
        ui.msg('  +++final consume store: %s'%(self.store) )

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
        ui.msg('  +++final trans store: %s'%(self.store) )



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
        output=int(self.supply_use*prodcurr/prodbase)
        ui.msg('   supply use (man 100): %s'%(self.supply_use))
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
            ui.msg('   ......prod: %s %s -> %s '%( prod, output,self.store[prod] ))
        ui.msg('  +++final prod store: %s'%(self.store) )



    def produce(self,boss,workers):
      return workers * boss

