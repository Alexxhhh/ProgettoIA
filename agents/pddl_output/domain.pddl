(define (domain treasure_quest)
  (:requirements :strips :typing :negative-preconditions) ; define requirements for the planner

  (:types ; define the types of objects in the world
    room key item puzzle direction
  )

  (:predicates ; define the properties and relationships of objects
    (at ?r - room) ; agent is currently in room ?r
    (connected ?a - room ?b - room ?d - direction) ; room ?a is connected to room ?b via direction ?d
    (locked ?r - room) ; room ?r is locked and cannot be entered
    (key_opens ?k - key ?r - room) ; key ?k can open the lock on room ?r
    (has_key ?k - key) ; agent possesses key ?k
    (has_item ?i - item) ; agent possesses item ?i
    (key_in_room ?k - key ?r - room) ; key ?k is located in room ?r
    (trap_item_room ?r - room ?i - item) ; room ?r has a trap that requires item ?i
    (trap_active ?r - room) ; the trap in room ?r is currently active
    (puzzle_in_room ?p - puzzle ?r - room) ; puzzle ?p is located in room ?r
    (answer_known ?p - puzzle) ; the agent knows the answer to puzzle ?p
    (life3) ; agent has 3rd life point
    (life2) ; agent has 2nd life point
    (life1) ; agent has 1st life point
    (dead) ; agent is dead
  )

  (:action move ; move from one room to an adjacent one
    :parameters (?from - room ?to - room ?d - direction)
    :precondition (and
      (at ?from) ; must be in the starting room
      (connected ?from ?to ?d) ; the rooms must be connected
      (not (locked ?to)) ; the destination room must not be locked
      (not (dead)) ; the agent must be alive
    )
    :effect (and
      (not (at ?from)) ; no longer in the starting room
      (at ?to) ; now in the destination room
    )
  )

  (:action unlock ; unlock a door to an adjacent room
    :parameters (?from - room ?to - room ?d - direction ?k - key)
    :precondition (and
      (at ?from) ; must be in the room adjacent to the locked one
      (connected ?from ?to ?d) ; must be a connection to the locked room
      (has_key ?k) ; must have a key
      (key_opens ?k ?to) ; the key must be the correct one for the room
      (locked ?to) ; the destination room must be locked
      (not (dead)) ; the agent must be alive
    )
    :effect (and
      (not (locked ?to)) ; the room is no longer locked
    )
  )

  (:action pickup_key ; pick up a key from the current room
    :parameters (?k - key ?r - room)
    :precondition (and
      (at ?r) ; must be in the room with the key
      (key_in_room ?k ?r) ; the key must be in the room
      (not (dead)) ; the agent must be alive
    )
    :effect (and
      (has_key ?k) ; agent now has the key
      (not (key_in_room ?k ?r)) ; key is no longer in the room
    )
  )

  (:action use_item_trap ; use an item to disable a trap in the current room
    :parameters (?r - room ?i - item)
    :precondition (and
      (at ?r) ; must be in the room with the trap
      (trap_active ?r) ; the trap must be active
      (trap_item_room ?r ?i) ; the room's trap must require this item
      (has_item ?i) ; agent must possess the required item
      (not (dead)) ; the agent must be alive
    )
    :effect (and
      (not (trap_active ?r)) ; the trap is now disabled
    )
  )

  (:action solve_puzzle ; solve a puzzle to disable a trap in the current room
    :parameters (?p - puzzle ?r - room)
    :precondition (and
      (at ?r) ; must be in the room with the puzzle
      (puzzle_in_room ?p ?r) ; the puzzle must be in this room
      (answer_known ?p) ; the agent must know the answer
      (trap_active ?r) ; the trap associated with the puzzle must be active
      (not (dead)) ; the agent must be alive
    )
    :effect (and
      (not (trap_active ?r)) ; the trap is now disabled
    )
  )

  (:action lose_life3 ; lose the third life point
    :parameters ()
    :precondition (and (life3)) ; must have life 3 to lose it
    :effect (and (not (life3))) ; life 3 is lost
  )

  (:action lose_life2 ; lose the second life point
    :parameters ()
    :precondition (and (not (life3)) (life2)) ; must have lost life 3 and have life 2
    :effect (and (not (life2))) ; life 2 is lost
  )

  (:action lose_life1 ; lose the final life point and die
    :parameters ()
    :precondition (and (not (life3)) (not (life2)) (life1)) ; must have lost lives 3 and 2, and have life 1
    :effect (and (not (life1)) (dead)) ; life 1 is lost and agent is dead
  )
)