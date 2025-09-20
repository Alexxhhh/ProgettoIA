(define (problem treasure_quest_problem)
  (:domain treasure_quest)

  (:objects ; define all the specific objects in this problem instance
    r1_entrance r2_bat_room r3_key4_room r4_wisdom_room r5_gas_room r6_fountain_room r7_seasons_room r8_key3_room r9_chair_room r10_arrow_room r11_key1_room r12_mystery_room r13_opaque_room r14_key2_room r15_flood_room r16_antechamber r17_treasure_room - room
    k1 k2 k3 k4 - key
    torch wet_cloth shield iron_rod - item
    p2_torch p4_time p5_gas p7_seasons p10_shield p12_statue p13_darkness p15_flood p16_sphinx - puzzle
    n s e w - direction
  )

  (:init ; define the initial state of the world
    (at r1_entrance) ; the agent starts at the entrance
    (life3) ; agent starts with 3 lives
    (life2) ; agent starts with 2 lives
    (life1) ; agent starts with 1 life

    ; agent's starting inventory
    (has_item torch) ; for the bat room
    (has_item wet_cloth) ; for the gas room
    (has_item shield) ; for the arrow room
    (has_item iron_rod) ; for the flood room

    ; key locations
    (key_in_room k1 r11_key1_room) ; key 1 is in room 11
    (key_in_room k2 r14_key2_room) ; key 2 is in room 14
    (key_in_room k3 r8_key3_room) ; key 3 is in room 8
    (key_in_room k4 r3_key4_room) ; key 4 is in room 3

    ; locked rooms and the keys that open them
    (locked r5_gas_room) ; room 5 is locked
    (key_opens k1 r5_gas_room) ; key 1 opens room 5
    (locked r10_arrow_room) ; room 10 is locked
    (key_opens k4 r10_arrow_room) ; key 4 opens room 10
    (locked r9_chair_room) ; room 9 is locked
    (key_opens k4 r9_chair_room) ; key 4 opens room 9
    (locked r15_flood_room) ; room 15 is locked
    (key_opens k1 r15_flood_room) ; key 1 can open room 15
    (key_opens k2 r15_flood_room) ; key 2 can open room 15
    (key_opens k3 r15_flood_room) ; key 3 can open room 15

    ; map connections (bidirectional)
    (connected r1_entrance r2_bat_room n)
    (connected r2_bat_room r1_entrance s)
    (connected r1_entrance r13_opaque_room e)
    (connected r13_opaque_room r1_entrance w)
    (connected r1_entrance r12_mystery_room s)
    (connected r12_mystery_room r1_entrance n)
    (connected r2_bat_room r3_key4_room e)
    (connected r3_key4_room r2_bat_room w)
    (connected r3_key4_room r4_wisdom_room e)
    (connected r4_wisdom_room r3_key4_room w)
    (connected r4_wisdom_room r5_gas_room e)
    (connected r5_gas_room r4_wisdom_room w)
    (connected r4_wisdom_room r14_key2_room s)
    (connected r14_key2_room r4_wisdom_room n)
    (connected r5_gas_room r6_fountain_room e)
    (connected r6_fountain_room r5_gas_room w)
    (connected r5_gas_room r15_flood_room s)
    (connected r15_flood_room r5_gas_room n)
    (connected r6_fountain_room r7_seasons_room s)
    (connected r7_seasons_room r6_fountain_room n)
    (connected r7_seasons_room r8_key3_room s)
    (connected r8_key3_room r7_seasons_room n)
    (connected r7_seasons_room r15_flood_room w)
    (connected r15_flood_room r7_seasons_room e)
    (connected r8_key3_room r9_chair_room w)
    (connected r9_chair_room r8_key3_room e)
    (connected r9_chair_room r15_flood_room n)
    (connected r15_flood_room r9_chair_room s)
    (connected r9_chair_room r10_arrow_room w)
    (connected r10_arrow_room r9_chair_room e)
    (connected r10_arrow_room r14_key2_room n)
    (connected r14_key2_room r10_arrow_room e)
    (connected r10_arrow_room r11_key1_room w)
    (connected r11_key1_room r10_arrow_room e)
    (connected r11_key1_room r13_opaque_room w)
    (connected r13_opaque_room r11_key1_room s)
    (connected r12_mystery_room r14_key2_room e)
    (connected r14_key2_room r12_mystery_room s)
    (connected r13_opaque_room r14_key2_room e)
    (connected r14_key2_room r13_opaque_room w)
    (connected r15_flood_room r16_antechamber w)
    (connected r16_antechamber r15_flood_room e)
    (connected r16_antechamber r17_treasure_room w)
    (connected r17_treasure_room r16_antechamber e)

    ; item-based traps
    (trap_item_room r2_bat_room torch) ; bats require the torch
    (trap_item_room r5_gas_room wet_cloth) ; gas requires the wet cloth
    (trap_item_room r10_arrow_room shield) ; arrows require the shield
    (trap_item_room r15_flood_room iron_rod) ; flood lever requires the iron rod

    ; knowledge-based puzzles
    (puzzle_in_room p4_time r4_wisdom_room) ; time puzzle in room 4
    (puzzle_in_room p7_seasons r7_seasons_room) ; seasons puzzle in room 7
    (puzzle_in_room p12_statue r12_mystery_room) ; statue puzzle in room 12
    (puzzle_in_room p13_darkness r13_opaque_room) ; darkness puzzle in room 13
    (puzzle_in_room p16_sphinx r16_antechamber) ; sphinx puzzle in room 16

    ; trap and puzzle activation states
    (trap_active r2_bat_room) ; trap is active
    (trap_active r4_wisdom_room) ; trap is active
    (trap_active r5_gas_room) ; trap is active
    (trap_active r7_seasons_room) ; trap is active
    (trap_active r10_arrow_room) ; trap is active
    (trap_active r12_mystery_room) ; trap is active
    (trap_active r13_opaque_room) ; trap is active
    (trap_active r15_flood_room) ; trap is active
    (trap_active r16_antechamber) ; trap is active

    ; known puzzle answers
    (answer_known p2_torch) ; agent knows how to handle bats
    (answer_known p4_time) ; agent knows the answer to the time puzzle
    (answer_known p5_gas) ; agent knows how to handle gas
    (answer_known p7_seasons) ; agent knows the answer to the seasons puzzle
    (answer_known p10_shield) ; agent knows how to handle arrows
    (answer_known p12_statue) ; agent knows the answer to the statue puzzle
    (answer_known p13_darkness) ; agent knows the answer to the darkness puzzle
    (answer_known p15_flood) ; agent knows how to handle the flood
    (answer_known p16_sphinx) ; agent knows the answer to the sphinx puzzle
  )

  (:goal (and ; the conditions to be met to solve the problem
    (at r17_treasure_room) ; must be in the treasure room
    (not (dead)) ; must not be dead
  ))
)