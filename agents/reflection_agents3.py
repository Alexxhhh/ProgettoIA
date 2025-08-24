#!/usr/bin/env python3
"""gemini_pddl_generator.py  —  Generate STRIPS‑compatible PDDL (domain + problem)
from a lore text using Google Gemini 1.5 Flash.

Highlights
==========
* Skeleton DOMAIN/PROBLEM già puro‑STRIPS (nessun string/number, niente numeric‑fluents).
* Prompt compatto + retry automatico se Gemini omette i marker.
* Salva risposta grezza per debug (`gemini_last_raw.txt`).
* File generati in ./pddl_output/domain.pddl e problem.pddl.

Usage
-----
    python gemini_pddl_generator.py  path/to/lore.txt
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict
import textwrap

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# ────────────────────────────────────────────────────────────────
# 1  Fixed API‑Key  (💡 sostituisci con la tua se diversa)
# ────────────────────────────────────────────────────────────────
API_KEY = "AIzaSyBY_olFJtT0xm-_Vl3LiQ1IZ0JRvoLM7NY"

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,               # leggermente >0 per creatività minima
    google_api_key=API_KEY,
)

OUTPUT_DIR = Path("./pddl_output"); OUTPUT_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# 2  Skeleton PDDL (solo linee essenziali, tag TODO)
# ────────────────────────────────────────────────────────────────
DOMAIN_SKEL = """
(define (domain treasure_quest)
  (:requirements :strips :typing)
  (:types room key item puzzle direction)

  (:predicates
    (at ?r - room) (connected ?a - room ?b - room ?d - direction)
    (locked ?r - room) (key_opens ?k - key ?r - room) (has_key ?k - key)
    (has_item ?i - item) (key_in_room ?k - key ?r - room)
    (trap_item_room ?r - room ?i - item) (trap_active ?r - room)
    (puzzle_in_room ?p - puzzle ?r - room) (answer_known ?p - puzzle)
    (dead)
  )

  ;; ACTIONS  (non toccare i nomi) ---------------------------------
  (:action move
    :parameters (?from - room ?to - room ?d - direction)
    :precondition (and (at ?from) (connected ?from ?to ?d) (not (locked ?to)) (not dead))
    :effect       (and (not (at ?from)) (at ?to)) )

  (:action unlock
    :parameters (?from - room ?to - room ?k - key ?d - direction)
    :precondition (and (at ?from) (connected ?from ?to ?d) (locked ?to)
                       (has_key ?k) (key_opens ?k ?to) (not dead))
    :effect       (and (not (locked ?to))) )

  (:action use_item_trap
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (has_item ?i) (trap_active ?r) (not dead))
    :effect       (and (not (trap_active ?r))) )

  (:action solve_puzzle
    :parameters (?p - puzzle ?r - room)
    :precondition (and (at ?r) (puzzle_in_room ?p ?r) (answer_known ?p) (trap_active ?r) (not dead))
    :effect       (and (not (trap_active ?r))) )

  (:action die
    :parameters (?r - room)
    :precondition (and (at ?r) (trap_active ?r) (not dead))
    :effect       (dead) )
)
"""

PROBLEM_SKEL = """
(define (problem treasure_quest_problem)
  (:domain treasure_quest)

  (:objects
    ;; directions
    n s e w - direction
    ;; TODO other objects (keys items puzzles rooms)
  )

  (:init
    (at entrance)
    ;; TODO init facts (has_item, key_in_room, connected, locked, trap_active…)
  )

  (:goal (and (at treasure_room) (not dead)))
)
"""

# ────────────────────────────────────────────────────────────────
# 3  Prompt builder
# ────────────────────────────────────────────────────────────────

def build_prompt(lore: str) -> str:
    return textwrap.dedent(f"""
    You are a disciplined PDDL generator: fill ONLY the lines marked `TODO`.
    • Keep skeleton exactly.  • Use (locked room) + (key_opens key room).
    • Return raw PDDL between markers, no extra text.

    ### DOMAIN START
    {DOMAIN_SKEL.strip()}
    ### DOMAIN END
    ### PROBLEM START
    {PROBLEM_SKEL.strip()}
    ### PROBLEM END

    LORE:
    {lore}
    """)

# Helper extraction
extract = lambda txt, a, b: (txt.split(a, 1)[1].split(b, 1)[0].strip() if a in txt and b in txt else None)

# Ask Gemini with automatic retry if markers missing

def ask_with_markers(prompt: str, tries: int = 3) -> str:
    raw = ""
    for i in range(tries):
        raw = llm.invoke(prompt if i == 0 else prompt + "\n⚠️ RETURN EXACTLY THE MARKERS." ).content
        if "### DOMAIN START" in raw and "### PROBLEM START" in raw:
            return raw
    Path("gemini_last_raw.txt").write_text(raw, encoding="utf-8")
    raise ValueError("Gemini output privo di marker – vedi gemini_last_raw.txt")

# ────────────────────────────────────────────────────────────────
# 4  Tool function
# ────────────────────────────────────────────────────────────────

@tool
def generate_pddl_from_lore(file_path: str) -> Dict[str, str]:
    """Generate domain/problem PDDL from a lore txt file using Gemini."""
    p = Path(file_path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(p)

    prompt = build_prompt(p.read_text(encoding="utf-8"))
    print("\n📤  Prompting Gemini…")

    raw = ask_with_markers(prompt)
    domain = extract(raw, "### DOMAIN START", "### DOMAIN END")
    problem = extract(raw, "### PROBLEM START", "### PROBLEM END")

    (OUTPUT_DIR / "domain.pddl").write_text(domain, encoding="utf-8")
    (OUTPUT_DIR / "problem.pddl").write_text(problem, encoding="utf-8")
    print("✅  PDDL salvati in", OUTPUT_DIR.resolve())
    return {"domain": domain, "problem": problem}

# ────────────────────────────────────────────────────────────────
# 5  CLI
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python gemini_pddl_generator.py path/to/lore.txt")

    result = generate_pddl_from_lore.run(sys.argv[1])
    print("\n── DOMAIN preview ──\n", result["domain"][:800])
    print("\n── PROBLEM preview ─\n", result["problem"][:800])
