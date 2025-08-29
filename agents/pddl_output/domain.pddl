(define (domain treasure_quest)
  (:requirements :strips :typing :negative-preconditions)
  (:types room key item puzzle direction)
  (:predicates
    (at ?r - room) ; agent is at room ?r
    (connected ?a - room ?b - room ?d - direction) ; room ?a is connected to room ?b in direction ?d
    (locked ?r - room) ; room ?r is locked
    (key_opens ?k - key ?r - room) ; key ?k opens room ?r
    (has_key ?k - key) ; agent has key ?k
    (has_item ?i - item) ; agent has item ?i
    (key_in_room ?k - key ?r - room) ; key ?k is in room ?r
    (trap_item_room ?r - room ?i - item) ; item ?i is needed for trap in room ?r
    (trap_active ?r - room) ; trap is active in room ?r
    (puzzle_in_room ?p - puzzle ?r - room) ; puzzle ?p is in room ?r
    (answer_known ?p - puzzle) ; agent knows the answer to puzzle ?p
    (life1) ; agent has life1
    (life2) ; agent has life2
    (life3) ; agent has life3
    (dead) ; agent is dead
  )
  (:action move
    :parameters (?from - room ?to - room ?dir - direction)
    :precondition (and (at ?from) (connected ?from ?to ?dir) (not (locked ?to)) (not (dead))) ; agent is at ?from, connected to ?to, ?to is not locked, agent is not dead
    :effect (and (at ?to) (not (at ?from))) ; agent moves from ?from to ?to
  )
  (:action unlock
    :parameters (?r - room ?k - key)
    :precondition (and (at ?r) (locked ?r) (has_key ?k) (key_opens ?k ?r)) ; agent is at ?r, ?r is locked, agent has key ?k, ?k opens ?r
    :effect (and (not (locked ?r))) ; ?r is unlocked
  )
  (:action use_item_trap
    :parameters (?r - room ?i - item)
    :precondition (and (at ?r) (trap_active ?r) (has_item ?i) (trap_item_room ?r ?i)) ; agent is at ?r, trap is active, agent has item ?i, ?i is needed for trap in ?r
    :effect (and (not (trap_active ?r))) ; trap is deactivated
  )
  (:action solve_puzzle
    :parameters (?r - room ?p - puzzle)
    :precondition (and (at ?r) (puzzle_in_room ?p ?r) (trap_active ?r) (answer_known ?p)) ; agent is at ?r, puzzle ?p is in ?r, trap is active, answer is known
    :effect (and (not (trap_active ?r))) ; trap is deactivated
  )
  (:action pickup_key
    :parameters (?k - key ?r - room)
    :precondition (and (at ?r) (key_in_room ?k ?r) (not (has_key ?k))) ; agent is at ?r, key ?k is in ?r, agent doesn't have ?k
    :effect (and (has_key ?k) (not (key_in_room ?k ?r))) ; agent picks up key ?k
  )
  (:action pickup_item
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (not (has_item ?i))) ; agent is at ?r, item ?i is in ?r, agent doesn't have ?i
    :effect (and (has_item ?i)) ; agent picks up item ?i
  )
  (:action lose_life3
  :parameters ()                               ; nessun parametro
  :precondition (and (life3))                  ; richiede di avere life3
  :effect       (and (not (life3)))            ; toglie life3
  )
  (:action lose_life2
    :parameters ()                              
    :precondition (and (not (life3)) (life2)) ; agent doesn't have life3, but has life2
    :effect (and (not (life2))) ; agent loses life2
  )
  (:action lose_life1
    :parameters () 
    :precondition (and (not (life3)) (not (life2)) (life1)) ; agent doesn't have life3 or life2, but has life1
    :effect (and (not (life1)) (dead)) ; agent loses life1 and dies
  )
)