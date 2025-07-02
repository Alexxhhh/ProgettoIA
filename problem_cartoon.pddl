(define (problem quest_problem)
  (:domain questmaster)

  (:objects
    player1 - player

    Dragons_Gate Goblin_Grotto Pixie_Pond Wizards_Watchtower - location
    Spiky_Spine_Cavern Prickly_Pits Trolls_Treetops Arrow_Alley Flame_Forge - trap
    Bubble_Bog Mushroom_Meadow Rainbow_Ridge - location
    Riddle_Reef Puzzle_Pond Enigma_Edge Mystery_Marsh - location
    Unicorns_Vault - location

    key1 key2 key3 key4 - key

    strada1 strada2 strada3 strada4 strada5 strada6 strada7 strada8 strada9
    strada10 strada11 strada12 strada13 strada14 strada15 strada16 strada17
    strada18 strada19 strada20 strada21 strada22 strada23 strada24 strada25
    strada26 strada27 - strada
  )

  (:init
    (at player1 Dragons_Gate)

    (connects strada1 Dragons_Gate Trolls_Treetops)
    (connects strada2 Dragons_Gate Spiky_Spine_Cavern)
    (connects strada3 Dragons_Gate Bubble_Bog)

    (connects strada4 Goblin_Grotto Bubble_Bog)
    (connects strada5 Goblin_Grotto Arrow_Alley)
    (connects strada6 Goblin_Grotto Flame_Forge)

    (connects strada7 Pixie_Pond Mushroom_Meadow)
    (connects strada8 Pixie_Pond Flame_Forge)
    (connects strada9 Pixie_Pond Prickly_Pits)

    (connects strada10 Wizards_Watchtower Prickly_Pits)
    (connects strada11 Wizards_Watchtower Rainbow_Ridge)
    (connects strada12 Wizards_Watchtower Spiky_Spine_Cavern)

    (connects strada13 Spiky_Spine_Cavern Enigma_Edge)
    (connects strada14 Trolls_Treetops Puzzle_Pond)
    (connects strada15 Bubble_Bog Puzzle_Pond)
    (connects strada16 Arrow_Alley Puzzle_Pond)
    (connects strada17 Arrow_Alley Riddle_Reef)
    (connects strada18 Flame_Forge Riddle_Reef)
    (connects strada19 Mushroom_Meadow Riddle_Reef)
    (connects strada20 Mushroom_Meadow Mystery_Marsh)
    (connects strada21 Prickly_Pits Mystery_Marsh)
    (connects strada22 Rainbow_Ridge Mystery_Marsh)
    (connects strada23 Rainbow_Ridge Enigma_Edge)

    (connects strada24 Riddle_Reef Unicorns_Vault)
    (connects strada25 Puzzle_Pond Unicorns_Vault)
    (connects strada26 Enigma_Edge Unicorns_Vault)
    (connects strada27 Mystery_Marsh Unicorns_Vault)

    (unlocked strada1) (unlocked strada2) (unlocked strada3)
    (unlocked strada4) (unlocked strada5) (unlocked strada6)
    (unlocked strada7) (unlocked strada8) (unlocked strada9)
    (unlocked strada10) (unlocked strada11) (unlocked strada12)
    (locked strada13) (locked strada14) (locked strada15) (locked strada16)
    (locked strada17) (locked strada18) (locked strada19) (locked strada20)
    (locked strada21) (locked strada22) (locked strada23)
    (locked strada24) (locked strada25) (locked strada26) (locked strada27)

    (at trap_spikes Spiky_Spine_Cavern)
    (at trap_spikes Prickly_Pits)
    (at trap_arrow Arrow_Alley)
    (at trap_fire Flame_Forge)
    (at trap_gorilla Trolls_Treetops)

    (riddle-unanswered Riddle_Reef)
    (riddle-unanswered Puzzle_Pond)
    (riddle-unanswered Enigma_Edge)
    (riddle-unanswered Mystery_Marsh)
    (riddle-unanswered Unicorns_Vault)

    (at key1 Riddle_Reef)
    (at key2 Puzzle_Pond)
    (at key3 Enigma_Edge)
    (at key4 Mystery_Marsh)

    (at final_treasure Unicorns_Vault)
  )

 (:goal
  (and
    (at player1 Unicorns_Vault)
    (has-treasure player1)
  )
)
)