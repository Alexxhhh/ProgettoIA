# reflection_agent_gemini.py
import os, re, subprocess, textwrap
import google.generativeai as genai
key="AIzaSyCp4OfTizTzSXNq67wHepzVfq-7TRsxUaI"
# ------------------------------------------------------------------
# Configura la chiave Gemini
genai.configure(api_key=os.getenv(key))   # ← assicurati che la variabile esista

# ------------------------------------------------------------------
# Utilità file
def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).strip() + "\n")

# ------------------------------------------------------------------
# Chiamata a Gemini 1.5 Pro
def call_gemini(prompt: str, model="gemini-1.5-pro-latest") -> str:
    resp = genai.GenerativeModel(model).generate_content(prompt)
    return resp.text

# ------------------------------------------------------------------
# Genera domain/problem da lore con marker chiari
def generate_pddl_from_lore(lore: str) -> tuple[str, str]:
    prompt = f"""
You are a PDDL expert AI.

Given the following LORE, output only:

### DOMAIN START
<domain.pddl contents>
### DOMAIN END
### PROBLEM START
<problem.pddl contents>
### PROBLEM END

Constraints:
- STRIPS compliant
- :typing, :negative-preconditions
- Initial state & goal coherent
- Brief comments allowed

LORE:
{lore}
"""
    raw = call_gemini(prompt)
    dom = re.search(r"### DOMAIN START(.*?)### DOMAIN END", raw, re.S)
    prob = re.search(r"### PROBLEM START(.*?)### PROBLEM END", raw, re.S)
    if not (dom and prob):
        raise ValueError("Marker mancanti nella risposta Gemini.")
    return dom.group(1).strip(), prob.group(1).strip()

# ------------------------------------------------------------------
# Prompt di correzione
def correction_prompt(domain_txt: str, problem_txt: str) -> tuple[str,str]:
    prompt = f"""
You are a PDDL correction agent.

Planner failed to find a plan. Fix domain/problem.
Return ONLY content between the same markers.

--- DOMAIN ---
{domain_txt}

--- PROBLEM ---
{problem_txt}

### DOMAIN START
<fixed domain>
### DOMAIN END
### PROBLEM START
<fixed problem>
### PROBLEM END
"""
    raw = call_gemini(prompt)
    dom = re.search(r"### DOMAIN START(.*?)### DOMAIN END", raw, re.S)
    prob = re.search(r"### PROBLEM START(.*?)### PROBLEM END", raw, re.S)
    if not (dom and prob):
        raise ValueError("Marker mancanti nella risposta di correzione.")
    return dom.group(1).strip(), prob.group(1).strip()

# ------------------------------------------------------------------
# Valida con Fast Downward
def plan_exists(dom: str, prob: str) -> bool:
    write_file("domain.pddl", dom)
    write_file("problem.pddl", prob)
    try:
        out = subprocess.run(
            ["./fast-downward.py", "domain.pddl", "problem.pddl",
             "--search", "lazy_greedy([ff()], preferred=[ff()])"],
            capture_output=True, text=True, timeout=120
        )
        return "Solution found!" in out.stdout
    except FileNotFoundError:
        print("⚠️  Fast Downward non trovato.")
        return False

# ------------------------------------------------------------------
# MAIN
if __name__ == "__main__":
    lore = read_file("lore.txt")
    print("🎯 Generazione PDDL da lore con Gemini…")
    dom, prob = generate_pddl_from_lore(lore)

    if plan_exists(dom, prob):
        print("✅ Piano valido! File salvati.")
    else:
        print("❌ Nessun piano trovato. Avvio correzione…")
        dom_fix, prob_fix = correction_prompt(dom, prob)
        if plan_exists(dom_fix, prob_fix):
            print("✅ Piano valido dopo correzione! File aggiornati.")
        else:
            print("⚠️ Nemmeno la correzione produce un piano. Serve revisione manuale.")