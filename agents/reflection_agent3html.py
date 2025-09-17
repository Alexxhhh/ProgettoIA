import os
from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = "AIzaSyC7YS7f5c1oePz7lMSF8SdZ1DOdQAwMX68"
os.environ["GOOGLE_API_KEY"] = API_KEY          # <── AGGIUNGI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=1.00,
    google_api_key=API_KEY,
)

# Percorsi ai file di input
lore_path = "../ProgettoIA/lore/lore_2_s.txt"
domain_path = "../ProgettoIA/agents/pddl_output/domain.pddl"
problem_path = "../ProgettoIA/agents/pddl_output/problem.pddl"

# Carico i contenuti
with open(lore_path, "r", encoding="utf-8") as f:
    lore = f.read()
with open(domain_path, "r", encoding="utf-8") as f:
    domain = f.read()
with open(problem_path, "r", encoding="utf-8") as f:
    problem = f.read()

# Costruisco il prompt per GPT
prompt = f"""
Generate a standalone HTML file (all CSS and JavaScript inline) that provides a playable dark fantasy adventure, consisting of:
- a Lore document (setting, characters, mission);
- a PDDL domain + problem file that lists each room, key, trap, puzzle, life predicate, locked , and the final objective.
Layout:
- the room name at the top (generate it based on the riddle or choose a random one based on the theme)
- lives on the top right
- inventory on the left
- the room image on the center of the page 
-the button which are used to move in the room (nswe) at the bottom center
-the text fiel and riddle (if any) in the center below the image
Game logic:
- by default, the directions (nswe) are in the under the image, which are buttons that can be pressed when the connection are available and not locked.
- if the room is a trap or contain a riddle, hide the buttons and in their place write the riddle with a text field where the user enters an answer and a button to submit the answer.
- if an answer is required, the player cannot move in any direction until the answer is given.
- if the answer is correct to a riddle or a trap, you can move freely in the room and the movement buttons reappear.
- If the answer is incorrect to a riddle or a trap, you lose a life. In any case, it permanently unlocks the room and makes the movement buttons reappear.
- The player starts in the entrance room with three lives (♥♥♥).
- If the number of lives drops to 0, it leads to a page that simply says "Game Over."
- Each connection between rooms must be created according to the PDDL files.
- At the start, the inventory contains all the items needed to overcome the traps
- at the start, the player has no keys in the inventory
- For each room, display its image (use Pexels or Pixabay for fantasy images) and a brief description of the room based on the lore.
- If a connection between rooms is blocked, the directional button is disabled unless the player has the correct key in the inventory.
- if the player enter in a room with a key, the key is added to the inventory and a message appears saying "You found a key!".
- Entering the objective room leads to a screen that says "Victory."
- Victory or a game over disables any further input.
Visual/Interaction Requirements:
- Provide an appropriate fantasy image (Pexels or Pixabay) for each room.
- Hearts (♥) visually represent remaining lives and update instantly.
- The inventory panel lists all items the player can use, including keys.
- Use concise and meaningful IDs and class names; no external libraries or resources.
- Return only raw HTML code: no Markdown, no explanations, no extra files.
- The file must run directly in any modern browser without additional resources.
- Clicking on the NSWE buttons must take you to the designated room.
- From the user view, everything must be in Italian.
- The HTML page must be complete and functional you have no limitation; generate everything and test it, fixing any errors.

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
