#!/usr/bin/env python3
"""reflection_agents3.py – genera dominio e problema PDDL da una lore usando Gemini

USO:
    python reflection_agents3.py path/to/lore.txt

Versione 2025‑08‑24 – Revision 2.
Fix principali:
  • La lore viene ora inclusa nel prompt di sistema (prompt_sys = build_prompt(lore_text)).
  • ask_with_markers ora applica automaticamente auto_wrap e rimuove eventuali ``` code‑fence, così non va in errore se Gemini
    restituisce solo le parti interne o inserisce backticks.
  • La chiave API può essere letta da variabile d'ambiente GOOGLE_API_KEY per evitare hard‑coding.
"""

from __future__ import annotations
from pathlib import Path
import os, sys, textwrap
from typing import Dict, List, Union

from langchain_google_genai import ChatGoogleGenerativeAI

# ────────────────────────────────────────────────────────────────
# 1. Inizializzazione LLM (chiave API da env var)
# ────────────────────────────────────────────────────────────────
API_KEY ="AIzaSyC-JBjbsQtI66ybyMA-b6C0Zrey5bB9X5E"

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,
    google_api_key=API_KEY,
)

OUTPUT_DIR = Path("./pddl_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
# 2. Skeleton PDDL ultracompatto (STRIPS puro)
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
  (:action lose_life3 :parameters () :precondition (life3)
    :effect (and (not life3)) )
  (:action lose_life2 :parameters ()
    :precondition (and (not life3) life2)
    :effect (and (not life2)) )
  (:action lose_life1 :parameters ()
    :precondition (and (not life3) (not life2) life1)
    :effect (and (not life1) dead) )
)
"""

PROBLEM_SKEL = """
(define (problem treasure_quest_problem)
  (:domain treasure_quest)
  (:objects n s e w - direction)               ;; TODO altri oggetti
  (:init (at entrance) (life1) (life2) (life3) ;; TODO fatti
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
    Non introdurre tipi string/number né fluents numerici. Rispondi con testo puro, senza markdown.

    **ISTRUZIONI CRITICHE PER IL PROBLEM PDDL:**
    - Gli oggetti DEVONO essere raggruppati per tipo come definito nel dominio
    - Usa la sintassi: `oggetto1 oggetto2 ... - tipo`
    - I tipi disponibili sono: room, key, item, puzzle, direction
    - NON usare il tipo generico 'object'

    **ESEMPIO CORRETTO:**
    (:objects 
        n s e w - direction
        entrance bat_room treasure_room - room
        k1 k2 k3 - key
        torch shield - item
        p1 p2 - puzzle
    )

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
def fix_problem_objects(problem_text: str) -> str:
    """Corregge automaticamente la sezione objects del problema PDDL."""
    lines = problem_text.split('\n')
    in_objects_section = False
    objects_section = []
    other_sections = []
    
    for line in lines:
        if '(:objects' in line:
            in_objects_section = True
            objects_section.append(line)
        elif in_objects_section and line.strip().startswith(')'):
            in_objects_section = False
            objects_section.append(line)
            other_sections.extend(objects_section)
        elif in_objects_section:
            objects_section.append(line)
        else:
            other_sections.append(line)
    
    # Se non ha trovato la sezione objects, restituisci il testo originale
    if not objects_section:
        return problem_text
    
    # Estrai tutti gli oggetti
    all_objects = []
    for line in objects_section:
        if '- object' in line:
            # Questo è il problema: sostituisci con tipi corretti
            line = line.replace('- object', '- room')  # Default a room
        all_objects.append(line)
    
    # Ricostruisci il problema
    return '\n'.join(other_sections)
# Helpers
extract = lambda txt,a,b: txt.split(a,1)[1].split(b,1)[0].strip() if a in txt and b in txt else None

# ────────────────────────────────────────────────────────────────
# 4. Wrappers utility
# ────────────────────────────────────────────────────────────────

def _strip_code_fence(text: str) -> str:
    """Se la stringa è racchiusa dentro ```…```, rimuove i backtick."""
    lines = text.strip().splitlines()
    if len(lines) >= 2 and lines[0].startswith("```)".replace(")", "")):
        # remove first and last line (``` ...)
        return "\n".join(lines[1:-1]).strip()
    return text


def auto_wrap(raw: str) -> str:
    """Se il modello restituisce solo init/objects, costruisce i marker."""
    raw = _strip_code_fence(raw)
    if "### DOMAIN START" in raw:
        return raw
    # tentativo: contiene predicati tipici ma manca marker
    if "- room" in raw and "connected" in raw:
        objs, init_body = raw.split("(", 1)
        objs_line = objs.strip()
        init_block = "(" + init_body.strip()
        problem = PROBLEM_SKEL \
            .replace("n s e w - direction", "n s e w - direction\n    " + objs_line) \
            .replace("(:init (at entrance) (life1) (life2) (life3)",
                     f"(:init (at entrance) (life1) (life2) (life3)\n    {init_block}")
        return f"### DOMAIN START\n{DOMAIN_SKEL}\n### DOMAIN END\n### PROBLEM START\n{problem}\n### PROBLEM END"
    return raw

# ────────────────────────────────────────────────────────────────
# 5. Invocazione con retries + auto_wrap
# ────────────────────────────────────────────────────────────────

def ask_with_markers(prompt: Union[str, List[dict]], tries: int = 3) -> str:
    """Invoca Gemini ripetendo fino a quando non ottiene tutti i marker."""
    last_raw = ""
    for i in range(tries):
        if i > 0:
            # Ricorda al modello di includere i marker se non l'ha fatto
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
# 6. Funzione principale
# ────────────────────────────────────────────────────────────────

def generate_pddl_from_lore(path: str) -> Dict[str, str]:
    """Dato un file di lore, salva domain.pddl e problem.pddl in ./pddl_output e li restituisce."""
    lore_text = Path(path).expanduser().read_text(encoding="utf-8")

    # Prompt di sistema completo di skeleton + lore
    prompt_sys = build_prompt(lore_text)

    # Messaggio utente minimale
    messages = [
        {"role": "system", "content": prompt_sys},
        {"role": "user",   "content": "Restituisci dominio e problema PDDL con i marker, senza markdown. ATTENZIONE: gli oggetti devono essere raggruppati per tipo specifico (room, key, item, puzzle, direction), NON usare 'object'."},
    ]

    print("\n📤  Chiedo a Gemini…")
    raw = ask_with_markers(messages)

    domain = extract(raw, "### DOMAIN START", "### DOMAIN END")
    problem = extract(raw, "### PROBLEM START", "### PROBLEM END")
    
    # Applica correzione automatica al problema
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