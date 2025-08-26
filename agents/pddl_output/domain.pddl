(define (domain treasure_quest)
  (:requirements :strips :typing :negative-preconditions)
  (:types room key item puzzle direction)
  (:predicates
    (at ?r - room) ; agent is in room ?r
    (connected ?a - room ?b - room ?d - direction) ; room ?a is connected to room ?b in direction ?d
    (locked ?r - room) ; room ?r is locked
    (key_opens ?k - key ?r - room) ; key ?k opens room ?r
    (has_key ?k - key) ; agent has key ?k
    (has_item ?i - item) ; agent has item ?i
    (key_in_room ?k - key ?r - room) ; key ?k is in room ?r
    (trap_item_room ?r - room ?i - item) ; item ?i is needed for trap in room ?r
    (trap_active ?r - room) ; trap is active in room ?r
    (puzzle_in_room ?p - puzzle ?r - room) ; puzzle ?p is in room ?r
    (answer_known ?p - puzzle) ; answer to puzzle ?p is known
    (life1) ; agent has life 1
    (life2) ; agent has life 2
    (life3) ; agent has life 3
    (dead) ; agent is dead
  )
  (:action move
    :parameters (?from - room ?to - room ?dir - direction)
    :precondition (and (at ?from) (connected ?from ?to ?dir) (not (locked ?to)) (not (dead))) ; agent can move if not locked and not dead
    :effect (and (not (at ?from)) (at ?to)) ; agent moves from ?from to ?to
  )
  (:action unlock
    :parameters (?r - room ?k - key)
    :precondition (and (at ?r) (locked ?r) (key_opens ?k ?r) (has_key ?k)) ; agent can unlock if has the right key
    :effect (and (not (locked ?r))) ; room is unlocked
  )
  (:action use_item_trap
    :parameters (?r - room ?i - item)
    :precondition (and (at ?r) (trap_active ?r) (trap_item_room ?r ?i) (has_item ?i)) ; agent can use item if has it
    :effect (and (not (trap_active ?r))) ; trap is deactivated
  )
  (:action solve_puzzle
    :parameters (?r - room ?p - puzzle)
    :precondition (and (at ?r) (puzzle_in_room ?p ?r) (answer_known ?p)) ; agent can solve if knows the answer
    :effect (and (not (trap_active ?r))) ; puzzle solved deactivates trap
  )
  (:action pickup_key
    :parameters (?k - key ?r - room)
    :precondition (and (at ?r) (key_in_room ?k ?r) (not (has_key ?k))) ; agent can pick up key if it's there and not already owned
    :effect (and (has_key ?k) (not (key_in_room ?k ?r))) ; agent now has the key
  )
  (:action pickup_item
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (not (has_item ?i))) ; agent can pick up item if it's there and not already owned
    :effect (and (has_item ?i)) ; agent now has the item
  )
  (:action lose_life3
    :parameters ()
    :precondition (life3) ; agent has life 3
    :effect (and (not (life3))) ; agent loses life 3
  )
  (:action lose_life2
    :parameters ()
    :precondition (and (not (life3)) (life2)) ; agent has life 2 and not life 3
    :effect (and (not (life2))) ; agent loses life 2
  )
  (:action lose_life1
    :parameters ()
    :precondition (and (not (life3)) (not (life2)) (life1)) ; agent has life 1 and not life 2 or 3
    :effect (and (not (life1)) (dead)) ; agent loses life 1 and dies
  )
)