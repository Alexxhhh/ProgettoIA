#!/usr/bin/env python3
"""reflection_agents3.py – genera DOMAIN / PROBLEM PDDL STRIPS da un file lore
   usando Gemini 1.5 Flash.

   Uso:
       python reflection_agents3.py path/to/lore.txt
"""

from __future__ import annotations
from pathlib import Path
import sys, textwrap
from typing import Dict, List, Union

import os, google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# ────────────────────────────────────────────────────────────────
# 1. API-KEY fissa (sostituiscila se serve)
# ────────────────────────────────────────────────────────────────
API_KEY = "AIzaSyBY_olFJtT0xm-_Vl3LiQ1IZ0JRvoLM7NY"
os.environ["GOOGLE_API_KEY"] = API_KEY
genai.configure(api_key=API_KEY)

# modello LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,
)

# directory di output PDDL
OUTPUT_DIR = Path("./pddl_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# 2. Skeleton PDDL minimale (STRIPS puro)
# ────────────────────────────────────────────────────────────────
DOMAIN_SKEL = """
(define (domain treasure_quest)
  (:requirements :strips :typing)
  (:types room key item puzzle direction)
  (:predicates
    (at ?r - room) (connected ?a - room ?b - room ?d - direction)
    (locked ?r - room) (key_opens ?k - key ?r - room)
    (has_key ?k - key) (has_item ?i - item)
    (key_in_room ?k - key ?r - room)
    (trap_item_room ?r - room ?i - item) (trap_active ?r - room)
    (puzzle_in_room ?p - puzzle ?r - room) (answer_known ?p - puzzle)
    (life1) (life2) (life3) (dead))
  (:action move
    :parameters (?f - room ?t - room ?d - direction)
    :precondition (and (at ?f) (connected ?f ?t ?d) (not (locked ?t)) (not dead))
    :effect (and (not (at ?f)) (at ?t)))
  (:action unlock
    :parameters (?f - room ?t - room ?k - key ?d - direction)
    :precondition (and (at ?f) (connected ?f ?t ?d) (locked ?t)
                       (has_key ?k) (key_opens ?k ?t) (not dead))
    :effect (and (not (locked ?t))))
  (:action use_item_trap
    :parameters (?i - item ?r - room)
    :precondition (and (at ?r) (trap_item_room ?r ?i) (has_item ?i)
                       (trap_active ?r) (not dead))
    :effect (and (not (trap_active ?r))))
  (:action solve_puzzle
    :parameters (?p - puzzle ?r - room)
    :precondition (and (at ?r) (puzzle_in_room ?p ?r) (answer_known ?p)
                       (trap_active ?r) (not dead))
    :effect (and (not (trap_active ?r))))
  (:action lose_life3 :parameters () :precondition (life3) :effect (not life3))
  (:action lose_life2 :parameters ()
    :precondition (and (not life3) life2) :effect (not life2))
  (:action lose_life1 :parameters ()
    :precondition (and (not life3) (not life2) life1)
    :effect (and (not life1) dead))
)
"""

PROBLEM_SKEL = """
(define (problem treasure_quest_problem)
  (:domain treasure_quest)
  (:objects
    n s e w - direction          ;; TODO: aggiungere chiavi, oggetti, puzzle, stanze
  )
  (:init
    (at entrance) (life1) (life2) (life3)   ;; TODO: fatti iniziali
  )
  (:goal (and (at treasure_room) (not dead)))
)
"""

# ────────────────────────────────────────────────────────────────
# 3. Prompt builder
# ────────────────────────────────────────────────────────────────
def build_prompt(lore: str) -> str:
    return textwrap.dedent(f"""
    Riempire SOLO `(:objects …)` e `(:init …)` marcate con TODO.
    Non introdurre tipi string/number né fluents numerici.
    Restituire testo ESATTAMENTE fra i marker.

    ### DOMAIN START
    {DOMAIN_SKEL.strip()}
    ### DOMAIN END
    ### PROBLEM START
    {PROBLEM_SKEL.strip()}
    ### PROBLEM END
    LORE:
    {lore}
    """)

extract = lambda txt,a,b: txt.split(a,1)[1].split(b,1)[0].strip() if a in txt and b in txt else None

def ask_with_markers(prompt: Union[str, List[dict]], tries: int = 3) -> str:
    raw = ""
    for i in range(tries):
        msg = prompt
        if i > 0:
            if isinstance(msg, str):
                msg += "\n⚠️  INCLUDE ALL MARKERS EXACTLY."
            else:
                msg[-1]["content"] += "\n⚠️  INCLUDE ALL MARKERS EXACTLY."
        raw = llm.invoke(msg).content
        if "### DOMAIN START" in raw and "### PROBLEM START" in raw:
            return raw
    Path("gemini_last_raw.txt").write_text(raw, encoding="utf-8")
    raise ValueError("Marker assenti – vedi gemini_last_raw.txt")

def auto_wrap(raw: str) -> str:
    if "### DOMAIN START" in raw:
        return raw
    if "- room" in raw and "connected" in raw:          # objects+init
        objs, init_body = raw.split("(", 1)
        problem = PROBLEM_SKEL.replace(
            "n s e w - direction",
            "n s e w - direction\n    " + objs.strip()
        ).replace(
            "(:init\n    (at entrance) (life1) (life2) (life3)",
            f"(:init\n    (at entrance) (life1) (life2) (life3)\n    ({init_body.strip()}"
        )
        return f"### DOMAIN START\n{DOMAIN_SKEL}\n### DOMAIN END\n### PROBLEM START\n{problem}\n### PROBLEM END"
    return raw

# ────────────────────────────────────────────────────────────────
# 4. Funzione principale
# ────────────────────────────────────────────────────────────────
def generate_pddl_from_lore(path: str) -> Dict[str, str]:
    lore = Path(path).expanduser().read_text(encoding="utf-8")
    prompt_sys = build_prompt("")
    messages = [
        {"role": "system", "content": prompt_sys},
        {"role": "user",   "content": lore}
    ]
    print("📤  Invio a Gemini…")
    raw = ask_with_markers(messages)
    raw = auto_wrap(raw)

    domain = extract(raw, "### DOMAIN START", "### DOMAIN END")
    problem = extract(raw, "### PROBLEM START", "### PROBLEM END")

    (OUTPUT_DIR / "domain.pddl").write_text(domain, encoding="utf-8")
    (OUTPUT_DIR / "problem.pddl").write_text(problem, encoding="utf-8")
    print("✅  Salvati domain.pddl e problem.pddl in", OUTPUT_DIR.resolve())
    return {"domain": domain, "problem": problem}

# ────────────────────────────────────────────────────────────────
# 5. CLI
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python reflection_agents3.py path/to/lore.txt")
    res = generate_pddl_from_lore(sys.argv[1])
    print("\n── DOMAIN preview ──\n", res["domain"][:600])
    print("\n── PROBLEM preview ─\n", res["problem"][:600])
