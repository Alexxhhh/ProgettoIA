(define (domain treasure_quest)
  (:requirements :strips :typing)
  (:types room item key puzzle - object)
  (:predicates
    (at ?x - room)
    (has_key ?k - key)
    (has_item ?i - item)
    (key_in_room ?k - key ?r - room)
    (trap_item_room ?r - room ?i - item)
    (trap_active ?r - room)
    (puzzle_in_room ?p - puzzle ?r - room)
    (answer_known ?p - puzzle)
    (key_opens ?k - key ?r1 - room ?r2 - room)
    (connected ?r1 - room ?r2 - room ?dir - string)
    (door_locked ?r1 - room ?r2 - room)
    (safe_life_room ?r - room)
    (lives_gt ?n - number)
    (lives_inc)
    (lives_dec)
    (lives_max)
  )

  (:action move
    :parameters (?from - room ?to - room ?dir - string)
    :precondition (and (at ?from) (connected ?from ?to ?dir) (not (door_locked ?from ?to)))
    :effect (and (not (at ?from)) (at ?to))
  )

  (:action unlock_door
    :parameters (?from - room ?to - room ?key - key)
    :precondition (and (at ?from) (door_locked ?from ?to) (has_key ?key) (key_opens ?key ?from ?to))
    :effect (and (not (door_locked ?from ?to)))
  )

  (:action take_key
    :parameters (?key - key ?room - room)
    :precondition (and (at ?room) (key_in_room ?key ?room))
    :effect (and (has_key ?key) (not (key_in_room ?key ?room)))
  )

  (:action use_item_trap
    :parameters (?item - item ?room - room)
    :precondition (and (at ?room) (trap_item_room ?room ?item) (has_item ?item) (trap_active ?room))
    :effect (and (not (trap_active ?room)))
  )

  (:action solve_puzzle
    :parameters (?puzzle - puzzle ?room - room)
    :precondition (and (at ?room) (puzzle_in_room ?puzzle ?room) (answer_known ?puzzle) (trap_active ?room))
    :effect (and (not (trap_active ?room)))
  )

  (:action gain_life
    :parameters (?room - room)
    :precondition (and (at ?room) (safe_life_room ?room) (lives_gt 0))
    :effect (and (lives_inc))
  )

  (:action lose_life
    :parameters ()
    :precondition (true)
    :effect (and (lives_dec))
  )
)