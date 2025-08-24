(define (domain treasure_quest)
  (:requirements :strips :typing :negative-preconditions)
  (:types room key item puzzle direction)
  (:predicates
    (at ?r - room) (connected ?a - room ?b - room ?d - direction)
    (locked ?r - room) (key_opens ?k - key ?r - room)
    (has_key ?k - key) (has_item ?i - item)
    (key_in_room ?k - key ?r - room)
    (trap_item_room ?r - room ?i - item) (trap_active ?r - room)
    (puzzle_in_room ?p - puzzle ?r - room) (answer_known ?p - puzzle)
    (life1) (life2) (life3) (dead) )
  (:action move
    :parameters (?f - room ?t - room ?d - direction)
    :precondition (and (at ?f) (connected ?f ?t ?d) (not (locked ?t)) (not dead))
    :effect       (and (not (at ?f)) (at ?t)) )
  (:action unlock
    :parameters (?f - room ?t - room ?k - key ?d - direction)
    :precondition (and (at ?f) (connected ?f ?t ?d) (locked ?t)
                       (has_key ?k) (key_opens ?k ?t) (not dead))
    :effect       (and (not (locked ?t))) )
  (:action use_item_trap
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (has_item ?i)
                       (trap_active ?r) (not dead))
    :effect       (and (not (trap_active ?r))) )
  (:action solve_puzzle
    :parameters (?p - puzzle ?r - room)
    :precondition (and (at ?r) (puzzle_in_room ?p ?r) (answer_known ?p)
                       (trap_active ?r) (not dead))
    :effect       (and (not (trap_active ?r))) )
(:action lose_life3
  :parameters ()
  :precondition (life3)
  :effect (not (life3))
)

(:action lose_life2
  :parameters ()
  :precondition (and (not (life3)) (life2))
  :effect (not (life2))
)

(:action lose_life1
  :parameters ()
  :precondition (and (not (life3)) (not (life2)) (life1))
  :effect (and (not (life1)) (dead))
)