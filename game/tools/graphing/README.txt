
If in the game/ directory you run:

     py.test --pyargs tests/test_economy.py

it generates a series of simulated economy runs (with hits from the player
to the economy) and saves the debug logs and save files into:

     save.test/



By changing directory (or in another window) to game/tools/graphing
and running the script:

     graph.py

You will generate an index.html in each directory inside:

   save.test/<TESTNAME>

which plots the cohort status values and the stores for that run.
In this way you can tweak the economy, run the tests and see the result.



NOTE: due to late changes that allow rebels to attack factions, all those
      tests will FAIL (they were written before the rebels could attack
      the factions).
