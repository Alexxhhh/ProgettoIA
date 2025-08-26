#!/usr/bin/env python3
"""
reflection_agents3.py  ·  Genera domain.pddl e problem.pddl da un file di lore
senza usare skeleton PDDL: tutta la struttura è descritta nel prompt.

Uso:
    python3 reflection_agents3.py /percorso/alla/lore.txt
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict
import os, sys

from langchain_google_genai import ChatGoogleGenerativeAI

# ───────────────────────────────────
# 1.  Chiave API fissa (o da env-var)
# ───────────────────────────────────
# imposta l'API-key sia in variabile d'ambiente sia come parametro
API_KEY = "AIzaSyC-JBjbsQtI66ybyMA-b6C0Zrey5bB9X5E"
os.environ["GOOGLE_API_KEY"] = API_KEY          # <── AGGIUNGI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,
    google_api_key=API_KEY,
)
OUTPUT_DIR = Path("./pddl_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ───────────────────────────────────
# 2. Funzione principale
# ───────────────────────────────────
def generate_pddl_from_lore(file_path: str) -> Dict[str, str]:
    """Legge la lore e genera i file PDDL in OUTPUT_DIR."""
    lore = Path(file_path).expanduser().read_text(encoding="utf-8")

    prompt = f"""
You are an expert in classical AI Planning (STRIPS) and PDDL writing.

TASK → read the Treasure-Quest lore below and output two PDDL blocks,
in this exact order:

(define (domain treasure_quest) …)
(define (problem treasure_quest_problem) …)

Return plain text, no markdown.

DOMAIN constraints
- (:requirements :strips :typing :negative-preconditions)
- Types: room key item puzzle direction
- Predicates (exactly these):
    (at ?r - room)
    (connected ?a - room ?b - room ?d - direction)
    (locked ?r - room)
    (key_opens ?k - key ?r - room)
    (has_key ?k - key) (has_item ?i - item)
    (key_in_room ?k - key ?r - room)
    (trap_item_room ?r - room ?i - item) (trap_active ?r - room)
    (puzzle_in_room ?p - puzzle ?r - room) (answer_known ?p - puzzle)
    (life1) (life2) (life3) (dead)
- Actions to include (names fixed):
    move, unlock, use_item_trap, solve_puzzle,
    pickup_key, pickup_item,
    lose_life3, lose_life2, lose_life1
  * move needs (not (locked ?to)) & (not (dead))
  * unlock clears (locked ?to) if agent has right key
  * each lose_lifeX removes one life predicate; lose_life1 also sets (dead)

PROBLEM requirements
- List ALL rooms, keys, items, puzzles, directions in (:objects)
- (:init) must include:
    (at entrance)  (life1)(life2)(life3)
    starting items owned
    key locations, key_opens + locked doors
    EVERY connected fact (bidirectional)
    traps & puzzle facts with trap_active
    (answer_known ?p) true for every puzzle
- Goal: (and (at treasure_room) (not (dead)))

STYLE
- Use lowercase_with_underscores for every symbol.
- Add a short natural-language comment to each line.
- NO markdown fences.

LORE:
{lore}
"""

    print("⚙️  Invio a Gemini…")
    text = llm.invoke(prompt).content

    if "(define (problem" not in text:
        raise ValueError("⚠️  Il modello non ha restituito il blocco problem.")

    domain_part, problem_tail = text.split("(define (problem", 1)
    domain  = domain_part.strip()
    problem = "(define (problem " + problem_tail.strip()

    (OUTPUT_DIR / "domain.pddl").write_text(domain,   encoding="utf-8")
    (OUTPUT_DIR / "problem.pddl").write_text(problem, encoding="utf-8")
    print("✅  PDDL salvati in", OUTPUT_DIR.resolve())

    return {"domain": domain, "problem": problem}

# ───────────────────────────────────
# 3. CLI
# ───────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 reflection_agents3.py path/to/lore.txt")

    res = generate_pddl_from_lore(sys.argv[1])
    print("\n── DOMAIN preview ──\n", res["domain"][:600])
    print("\n── PROBLEM preview ─\n", res["problem"][:600])
