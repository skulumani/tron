# TRON

AI Tron lightcycle game
Based on hexatron but improved

# Battles

Vary start position
Vary map shape/size
Vary obstacles inside the map
Add point goals inside map (powerups)

## 2 way

1. AI vs. random controller
2. AI vs. human
3. AI vs. AI
4. AI vs. optimal controller
1. AI vs. dumb controller

## n way

1. AI vs. n x AI
2. AI vs. n x random
3. AI vs. n x optimal controller

# TODO 

* [x] no more 45 degree moves
* [.] unit tests for player and game grid - make sure motion works as expected
* [-] test for visualization
* [x] pygame human player interface
* [ ] automated testing - save state to some file and playback/print stats
* [ ] replay interface - read saved game data
* [ ] pygame recorder
* [ ] ensure game end logic works in all situations
    * 1, 2, and n players
    * crash into heads
    * crash into tails
    * crash into walls

# References

* [hexatron](https://github.com/pvmolle/hexatron)
* [pygame_recorder](https://github.com/tdrmk/pygame_recorder)
