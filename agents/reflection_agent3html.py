import os
from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = "AIzaSyC-JBjbsQtI66ybyMA-b6C0Zrey5bB9X5E"
os.environ["GOOGLE_API_KEY"] = API_KEY          # <── AGGIUNGI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.15,
    google_api_key=API_KEY,
)

# Percorsi ai file di input
lore_path = "/Users/andreadomenicogimbri/Desktop/ProgettoIA/lore/lore_2_s.txt"
domain_path = "/Users/andreadomenicogimbri/Desktop/ProgettoIA/agents/pddl_output/domain.pddl"
problem_path = "/Users/andreadomenicogimbri/Desktop/ProgettoIA/agents/pddl_output/problem.pddl"

# Carico i contenuti
with open(lore_path, "r", encoding="utf-8") as f:
    lore = f.read()
with open(domain_path, "r", encoding="utf-8") as f:
    domain = f.read()
with open(problem_path, "r", encoding="utf-8") as f:
    problem = f.read()

# Costruisco il prompt per GPT
prompt = f"""
You are an AI.
Generate one self-contained HTML file (all CSS & JavaScript inline) that delivers a playable dark-fantasy adventure built from:
 -a Lore document (setting, characters, quest);
 -a PDDL domain + problem file that lists every room, key, trap, puzzle, life predicate, locked door, and the final goal.
Layout:
-Use display:grid; grid-template-columns:260px 1fr; on the root container.
-Do not create a third column: the inventory belongs inside the left panel.
-All elements (buttons, media, overlays) appear only when needed (display:none/block) and must never cause horizontal scrolling at 1280 × 720 px.
Game logic requirements:
-the player starts in the entrance room with three lives (♥♥♥) and the inventory containing all the objects needed to surpass traps (except keys).
-for every room, display its image/video, description, and available directions as buttons.
-if a connection between rooms is locked, the direction button is disabled unless the player has the right key in the inventory
-Traps block movement until resolved
-the player must choose the correct object between the ones in the inventory to surpass traps, otherwise the player loses one life.
-Puzzles block movement until answered
-the player must type the correct answer to puzzles, otherwise the player loses one life.
-Life system: three hearts; reaching 0 hearts triggers a game-over screen.
-Entering the goal room triggers a victory screen.
-Victory or game-over disables all further input.
Visual / interaction requirements:
-Provide a fantasy-appropriate image (Unsplash) or short looping video (Pixabay) for every room.
-Hearts (♥) visually represent the remaining lives and update instantly.
-The inventory panel lists only the keys currently helda key disappears immediately after use.
-Use concise, meaningful IDs and class names; no external libraries or assets.
Output rules:
-Return only the raw HTML code — no Markdown, no explanations, no extra files.
-The file must run directly in any modern browser without additional resources.
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
