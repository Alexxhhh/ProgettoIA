```pddl
(define (problem cartoon_quest_problem)
  (:domain cartoon_quest)
  (:objects 
    Dragons_Gate Goblin_Grotto Pixie_Pond Wizards_Watchtower Bubble_Bog Mushroom_Meadow Rainbow_Ridge 
    Spiky_Spine_Cavern Prickly_Pits Arrow_Alley Flame_Forge Trolls_Treetops
    Riddle_Reef Puzzle_Pond Enigma_Edge Mystery_Marsh Unicorns_Vault - room
    key1 - key

  )
  (:init (at Dragons_Gate)
         (connected Dragons_Gate Goblin_Grotto)
         (connected Goblin_Grotto Riddle_Reef)
         (connected Riddle_Reef Unicorns_Vault)
         (locked Riddle_Reef Unicorns_Vault key1)
         (is_trap Spiky_Spine_Cavern)
         (is_riddle Riddle_Reef)

  )
  (:goal (win))
)
```
