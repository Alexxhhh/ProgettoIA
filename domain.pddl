```pddl
(define (domain cartoon_quest)
  (:requirements :strips :typing :negative-preconditions)
  (:types room riddle_room trap_room key)
  (:predicates (at ?pos - room)
               (has_key ?k - key)
               (connected ?r1 - room ?r2 - room)
               (locked ?r1 - room ?r2 - room ?k - key)
               (solved_riddle ?r - riddle_room)
               (is_trap ?r - trap_room)
               (dead)
               (win)
  )

  (:action go
    :parameters (?from - room ?to - room)
    :precondition (and (at ?from) (connected ?from ?to) (not (dead)))
    :effect (and (not (at ?from)) (at ?to))
  )

  (:action solve_riddle
    :parameters (?r - riddle_room)
    :precondition (and (at ?r) (not (dead)) (not (solved_riddle ?r)))
    :effect (and (solved_riddle ?r) (has_key key1)) ;Fixed key generation.  Assumes key1 is generated from solving a riddle.  Add more keys as needed.
  )

  (:action unlock_door
    :parameters (?r1 - room ?r2 - room ?k - key)
    :precondition (and (at ?r1) (locked ?r1 ?r2 ?k) (has_key ?k) (not (dead)))
    :effect (not (locked ?r1 ?r2 ?k))
  )

  (:action die
    :parameters (?r - trap_room)
    :precondition (and (at ?r) (is_trap ?r) (not (dead)) )
    :effect (dead)
  )

  (:action win_game
    :precondition (and (at Unicorns_Vault) (not (dead)))
    :effect (win)
  )

)
```
