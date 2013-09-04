Huh?
====

I need to try and make sense of the spec, so im going to vomit info
into this file

Lets try and split this into:

    * production

    * group actions



Defaults
========
I had to pick some defaults for some of the settings...


Industry - Goods and Food
Privileged Cohort - Size: medium, Liberty: , QoL: , Cash: high
Servitor Cohort - Size: large, Liberty: , QoL: , Cash:.

  Privileged(size=Game.MED, liberty=Game.MED,
             quality_of_life=Game.HIGH, cash=Game.HIGH),
  Servitor(size=Game.MAX, liberty=Game.LOW,
             quality_of_life=Game.LOW, cash=Game.MED)



Military - Force and Stability
Privileged Cohort - Size: small, Liberty: , QoL: , Cash:.
Servitor/Warrior Cohort - Size: medium, Liberty: , QoL: , Cash:.

  Privileged(size=Game.LOW, liberty=Game.HIGH,
             quality_of_life=Game.HIGH, cash=Game.HIGH),
  Servitor(size=Game.MED, liberty=Game.HIGH,
             quality_of_life=Game.MED, cash=Game.MED)



Logistics - Transport to and from Planet
Privileged Cohort - Size: medium, Liberty: , QoL: , Cash:.
Servitor Cohort - Size: small, Liberty: , QoL: , Cash:.

  Privileged(size=Game.MED, liberty=Game.HIGH,
             quality_of_life=Game.HIGH, cash=Game.HIGH),
  Servitor(size=Game.LOW, liberty=Game.MED,
             quality_of_life=Game.HIGH, cash=Game.MED)






Production: what we know
========================
factions consume resources

zones produce resources depending on cohort.willingness and efficiency

city zones convert raw into resources

resources requirements must be met or a drop off in output (efficency?)
  * list requirements -what we need, how much
  * list provided - what are created from what vol of inputs

invader factions rquire support (resource and resources)

servitor cohorts create zone resource

cohort size -- good resource required to support each tuen is derived from this (and quality of life?)

efficiency can be increased by plan


Industry - Goods and Food
  Processing done by huge Servitor Cohort
  Staffed by Privileged Cohort
  Requires Enforcement (military)
  Requires Raw Materials (logistics)
  Provides Resources

Military - Force and Stability
  Run by Privileged Cohort
  Staffed by Servitor/Warrior Cohort (harder to infiltrate than others)
  Requires Resources (economic)
  Requires Manpower (logistics)
  Provides Enforcement

Logistics - Transport to and from Planet
  Staffed by Privileged Cohort
  Supported by small Servitor Cohort
  Requires Resources (economic)
  Requires Enforcement (military)
  Provides Raw Material from planet
  Provides Manpower from planet



