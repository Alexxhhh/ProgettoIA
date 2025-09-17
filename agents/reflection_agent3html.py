import os
from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = "AIzaSyAwX8CohVzXyslpR5Wn1l37ZGSRTExfAiY"
os.environ["GOOGLE_API_KEY"] = API_KEY          # <── AGGIUNGI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.00,
    google_api_key=API_KEY,
)

# Percorsi ai file di input
lore_path = "../ProgettoIA/lore/lore_2_s.txt"
domain_path = "../ProgettoIA/agents/pddl_output/domain.pddl"
problem_path = "../ProgettoIA/agents/pddl_output/problem.pddl"
images_path = "../ProgettoIA/jpeg/"
# Carico i contenuti
with open(lore_path, "r", encoding="utf-8") as f:
    lore = f.read()
with open(domain_path, "r", encoding="utf-8") as f:
    domain = f.read()
with open(problem_path, "r", encoding="utf-8") as f:
    problem = f.read()

# Costruisco il prompt per GPT
prompt = f"""
Generate a standalone HTML file (all CSS and JavaScript inline) that provides a playable dark-fantasy adventure, strictly based on the following lore and constraints.

LORE (from PDDL + lore_2_s.txt)
────────────────────────────────
- You are an adventurer inside an ancient labyrinthine temple. You start in room 1 (entrance) and must reach room 17 (treasure_room) without losing all your lives.
- Lives system: start with ♥♥♥ (life1, life2, life3). Losing a trap removes lives in order. If all lives are gone → Game Over.
- Inventory starts with: Torcia, Panno_bagnato, Scudo, Asta_di_ferro (used to overcome traps). No keys initially.
- Keys (collectable **once**; remain forever in inventory):  
  k1 in room 11 → unlocks rooms 4↔5 and 5↔15  
  k2 in room 14 → unlocks rooms 9↔15  
  k3 in room  8 → unlocks rooms 7↔15  
  k4 in room  3 → unlocks rooms 9↔10
- Puzzle / traps (room – expected answer / object):  
  2 Torcia   (object = Torcia)  
  4 Tempo    (answer = Tempo)  
  5 Panno_bagnato (object = Panno_bagnato)  
  7 Stagioni  (answer = Stagioni)  
10 Scudo    (object = Scudo)  
 12 Statua   (answer = Statua)  
 13 Oscurità   (answer = Oscurità)  
 15 Asta_di_ferro (object = Asta_di_ferro)  
 16 Uomo (single try)
- Goal: reach treasure_room (room 17) alive.

MANDATORY ANSWER RULE
─────────────────────
Upon entering a room containing a riddle or trap:
1. **All movement buttons (N S E W) are hidden.**  
2. The interface shows **only a text field** where the player types the required answer (for riddles) **or** the exact name of the correct inventory item (for traps), plus a “Submit” button.  
3. • **Correct answer / object** → the room is permanently unlocked, movement buttons reappear, no life lost, and subsequent visits to this room never ask the puzzle again.  
   • **Wrong answer / object** → one life is lost **and movement buttons remain hidden**; the player must try again (if any lives remain).  
4. If lives reach 0 → immediate Game Over page.

KEY RULES
──────────
- Entering a room with a key automatically collects it once; show “Hai trovato una chiave!”.  
- A movement button that leads through a key-locked connection is **enabled only if the key is already in inventory**; otherwise it appears disabled.

LAYOUT
──────
- Room name at top; lives (♥ icons) top-right (update instantly).  
- Inventory panel on the left (items + keys).  
- **Each room shows an image that you must take from the directory jpg whose path is contain in variable images_path remeber the name of the file contained in the directory jpg correspond to the number of the room.**  
- Room image centered; description immediately below.  
- Movement buttons (N S E W) below description when available.  
- Puzzle/trap interface replaces movement buttons while active.  
- Message area for key pickups and other events.
- Victory page (upon reaching treasure_room alive): “Congratulazioni! Hai trovato il tesoro!”
- Game Over page (upon losing all lives): “Game Over! Sei rimasto senza vite.
- Restart button on Victory and Game Over pages to reload the game. 



VISUAL / INTERACTION REQUIREMENTS
──────────────────────────────────
- Interface entirely in **Italian**.  
- Disable directional buttons when their connection is locked by a missing key.  
- No external libraries/resources; concise IDs/class names.  
- After Victory (treasure_room reached with lives > 0) or Game Over, disable all inputs.

OUTPUT
──────
Return **only raw HTML code** (no Markdown, no explanations, no external files).  
The file must run directly in any modern browser without additional resources.



=== LORE ===
{lore}

=== DOMAIN.PDDL ===
{domain}

=== PROBLEM.PDDL ===
{problem}
"""

print("Generazione HTML in corso con geminiAi.")
response = llm.invoke(prompt)

# Salva l’output in un file HTML
html_output = response.content
with open("interactive_story.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("HTML salvato come 'interactive_story.html'. ")
