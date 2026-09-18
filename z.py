from PIL import Image
from pathlib import Path

# -------------------------
# CONFIG
# -------------------------

SPRITESHEET = "obstacles3.png"
OUTPUT_DIR = Path("assets/rooms/obstacles")

COLS = 10
ROWS = 5

# -------------------------
# LOAD IMAGE
# -------------------------

sheet = Image.open(SPRITESHEET)

width, height = sheet.size

print(f"Spritesheet : {width}x{height}")

# On ne fait volontairement PAS width // COLS
# car l'image fait une taille qui ne tombe pas forcément pile.
# On calcule donc chaque bord proportionnellement.

x_edges = [round(i * width / COLS) for i in range(COLS + 1)]
y_edges = [round(i * height / ROWS) for i in range(ROWS + 1)]

# -------------------------
# DOSSIERS
# -------------------------

folders = {
    "walls": OUTPUT_DIR / "walls",
    "pillars": OUTPUT_DIR / "pillars",
    "containers": OUTPUT_DIR / "containers",
    "stones": OUTPUT_DIR / "stones",
}

for folder in folders.values():
    folder.mkdir(parents=True, exist_ok=True)

# -------------------------
# DECOUPE
# -------------------------

wall_id = 1
pillar_id = 1
container_id = 1
stone_id = 1

for row in range(ROWS):
    for col in range(COLS):

        left = x_edges[col]
        right = x_edges[col + 1]

        top = y_edges[row]
        bottom = y_edges[row + 1]

        sprite = sheet.crop((left, top, right, bottom))

        # Deux premières lignes = walls
        if row <= 1:
            filename = folders["walls"] / f"wall_{wall_id:02}.png"
            wall_id += 1

        # Troisième ligne = pillars
        elif row == 2:
            filename = folders["pillars"] / f"pillar_{pillar_id:02}.png"
            pillar_id += 1

        # Quatrième ligne = crates / barrels
        elif row == 3:
            filename = folders["containers"] / f"container_{container_id:02}.png"
            container_id += 1

        # Cinquième ligne = stones
        else:
            filename = folders["stones"] / f"stone_{stone_id:02}.png"
            stone_id += 1

        sprite.save(filename)

        print("Créé :", filename)

print("\nDécoupage terminé.")