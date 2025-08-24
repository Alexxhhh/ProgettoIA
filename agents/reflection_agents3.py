#!/usr/bin/env python3
"""reflection_agents3.py – genera dominio e problema PDDL da una lore usando Gemini

USO:
    python reflection_agents3.py path/to/lore.txt

Versione 2025‑08‑24 – Revision 3.
Fixed: bilanciamento parentesi in DOMAIN_SKEL (mancava una parentesi di chiusura per (define)).
"""

from __future__ import annotations
from pathlib import Path
import os, sys, textwrap
from typing import Dict, List, Union

from langchain_google_genai import ChatGoogleGenerativeAI

# ────────────────────────────────────────────────────────────────
# 1. Inizializzazione LLM (chiave API da env var)
# ────────────────────────────────────────────────────────────────
API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not API_KEY:
    sys.exit("Errore: imposta la variabile d'ambiente GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,
    google_api_key=API_KEY,
)

OUTPUT_DIR = Path("./pddl_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# 2. Skeleton PDDL (STRIPS + typing + negative-preconditions)
# ────────────────────────────────────────────────────────────────
DOMAIN_SKEL = """
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

  ;; —————————————————— actions ——————————————————
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
                       (not dead))
    :effect       (and (answer_known ?p)))

  (:action pickup_key
    :parameters (?k - key ?r - room)
    :precondition (and (at ?r) (key_in_room ?k ?r) (not dead))
    :effect       (and (has_key ?k) (not (key_in_room ?k ?r))))

  (:action pickup_item
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (not dead))
    :effect       (and (has_item ?i)))

  (:action lose_life3
    :parameters ()
    :precondition (life3)
    :effect (not (life3)))

  (:action lose_life2
    :parameters ()
    :precondition (and (not (life3)) (life2))
    :effect (not (life2)))

  (:action lose_life1
    :parameters ()
    :precondition (and (not (life3)) (not (life2)) (life1))
    :effect (and (not (life1)) (dead)))

  ;; goal placeholder — verrà sovrascritto
  (:goal (and (at treasure_room) (not dead)))
)
"""

PROBLEM_SKEL = """
(define (problem treasure_quest_problem)
  (:domain treasure_quest)
  (:objects n s e w - direction)               ;; TODO altri oggetti
  (:init (at entrance) (life1) (life2) (life3) ;; TODO fatti iniziali
  )
  (:goal (and (at treasure_room) (not dead)))
)
"""

# ────────────────────────────────────────────────────────────────
# 3. Prompt builder
# ────────────────────────────────────────────────────────────────

def build_prompt(lore: str) -> str:
    """Costruisce il prompt di sistema: skeleton + lore."""
    return textwrap.dedent(f"""
    Compila SOLO le sezioni contrassegnate con TODO.
    Mantieni i marker ### DOMAIN/PROBLEM START/END esattamente come sono.
    Non introdurre tipi stringa extra né markdown.

    ### DOMAIN START
    {DOMAIN_SKEL}
    ### DOMAIN END

    ### PROBLEM START
    {PROBLEM_SKEL}
    ### PROBLEM END

    Lore di riferimento:
    ---
    {lore}
    ---
    """)

# ────────────────────────────────────────────────────────────────
# 4. Funzioni di supporto
# ────────────────────────────────────────────────────────────────

def auto_wrap(raw: str) -> str:
    """Assicura che il testo sia dentro ### DOMAIN/PROBLEM START/END."""
    if "### DOMAIN START" not in raw:
        raw = "### DOMAIN START\n" + raw
    if "### DOMAIN END" not in raw:
        raw += "\n### DOMAIN END"
    if "### PROBLEM START" not in raw:
        raw += "\n### PROBLEM START\n"
    if "### PROBLEM END" not in raw:
        raw += "\n### PROBLEM END"
    return raw


def extract(txt: str, a: str, b: str) -> str:
    try:
        return txt.split(a)[1].split(b)[0].strip()
    except IndexError:
        raise ValueError(f"Marker {a} o {b} assente")


def fix_problem_objects(problem_text: str) -> str:
    """Placeholder: aggiunge automaticamente oggetti mancanti se necessario."""
    # Implementazione minimale: nessuna modifica
    return problem_text

# ────────────────────────────────────────────────────────────────
# 5. Chiamata a Gemini (con retry sui marker)
# ────────────────────────────────────────────────────────────────

def ask_with_markers(prompt: Union[str, List[dict]], tries: int = 3) -> str:
    """Invoca Gemini ripetendo fino a quando non ottiene tutti i marker."""
    last_raw = ""
    for i in range(tries):
        if i > 0:
            reminder = "\n⚠️  INCLUDE EXACTLY: ### DOMAIN START/END e ### PROBLEM START/END. Nessun markdown."
            if isinstance(prompt, str):
                prompt += reminder
            else:
                prompt[-1]["content"] += reminder
        last_raw = llm.invoke(prompt).content  # type: ignore
        wrapped = auto_wrap(last_raw)
        if all(m in wrapped for m in ("### DOMAIN START", "### DOMAIN END", "### PROBLEM START", "### PROBLEM END")):
            return wrapped
    Path("gemini_last_raw.txt").write_text(last_raw, encoding="utf-8")
    raise ValueError("Marker ancora assenti – vedi gemini_last_raw.txt")

# ────────────────────────────────────────────────────────────────
# 6. Orchestrazione
# ────────────────────────────────────────────────────────────────

def generate_pddl_from_lore(lore_path: str) -> Dict[str, str]:
    lore_text = Path(lore_path).read_text(encoding="utf-8")
    prompt_sys = build_prompt(lore_text)
    messages = [
        {"role": "system", "content": prompt_sys},
        {"role": "user", "content": "Genera dominio e problema"},
    ]

    print("⚙️  Interrogo Gemini…")
    raw = ask_with_markers(messages)

    domain = extract(raw, "### DOMAIN START", "### DOMAIN END")
    problem = extract(raw, "### PROBLEM START", "### PROBLEM END")

    problem = fix_problem_objects(problem)

    OUTPUT_DIR.joinpath("domain.pddl").write_text(domain, encoding="utf-8")
    OUTPUT_DIR.joinpath("problem.pddl").write_text(problem, encoding="utf-8")
    print("PDDL salvati in", OUTPUT_DIR.resolve())
    return {"domain": domain, "problem": problem}

# ────────────────────────────────────────────────────────────────
# 7. CLI
# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python reflection_agents3.py path/to/lore.txt")

    result = generate_pddl_from_lore(sys.argv[1])

    print("\n── DOMAIN preview ──\n", result["domain"][:600])
    print("\n── PROBLEM preview ─\n", result["problem"][:600])
