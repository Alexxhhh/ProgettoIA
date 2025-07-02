(define (domain questmaster)
  (:requirements :typing :strips :negative-preconditions)

  (:types
    player trap treasure - entity
    location
    strada
    key
  )

  (:predicates
    (at ?e - entity ?l - location)               ; dove si trova qualsiasi entità
    (connects ?s - strada ?from - location ?to - location)
    (unlocked ?s - strada)
    (locked ?s - strada)

    (has ?p - player ?k - key)
    (key-for ?k - key ?s - strada)

    (riddle-unanswered ?l - location)
    (has-treasure ?p - player)
    (dead ?p - player)
  )

  ;; Muovi il giocatore da una stanza all'altra tramite una strada sbloccata
  (:action move
    :parameters (?p - player ?from - location ?to - location ?s - strada)
    :precondition (and
      (at ?p ?from)
      (connects ?s ?from ?to)
      (unlocked ?s)
    )
    :effect (and
      (not (at ?p ?from))
      (at ?p ?to)
    )
  )

  ;; Risolvi l'indovinello in una stanza per ottenere una chiave
  (:action answer-riddle
    :parameters (?p - player ?l - location ?k - key)
    :precondition (and
      (at ?p ?l)
      (riddle-unanswered ?l)
    )
    :effect (and
      (not (riddle-unanswered ?l))
      (has ?p ?k)
    )
  )

  ;; Usa la chiave per sbloccare una strada
  (:action unlock
    :parameters (?p - player ?s - strada ?k - key)
    :precondition (and
      (has ?p ?k)
      (key-for ?k ?s)
      (locked ?s)
    )
    :effect (and
      (not (locked ?s))
      (unlocked ?s)
    )
  )

  ;; Morte per trappola: se entri in una stanza con trappola, muori
  (:action die-to-trap
    :parameters (?p - player ?l - location ?t - trap)
    :precondition (and
      (at ?p ?l)
      (at ?t ?l)
    )
    :effect (dead ?p)
  )

  ;; Raccogli il tesoro se sei nella stessa stanza
  (:action collect-treasure
    :parameters (?p - player ?t - treasure ?l - location)
    :precondition (and
      (at ?p ?l)
      (at ?t ?l)
    )
    :effect (has-treasure ?p)
  )
)
