"""Éditeur visuel de salles (Room Editor).

Conçu pour être épuré, rapide et agréable à utiliser au clavier, à la souris
ou entièrement à la manette.
"""

import json
import os
import sys
import pygame

# Racine du projet pour charger les assets et modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.constants import (
    PLAY_AREA_X_RATIO,
    PLAY_AREA_Y_RATIO,
    PLAY_AREA_W_RATIO,
    PLAY_AREA_H_RATIO,
)

# --- Configuration & Palette épurée ---
WIDTH, HEIGHT = 1360, 780
FPS = 60

BG_COLOR = pygame.Color("#13131a")
PANEL_COLOR = pygame.Color("#1c1c27")
PANEL_BORDER = pygame.Color("#2a2a3b")
TEXT_COLOR = pygame.Color("#e6e6f0")
MUTED_COLOR = pygame.Color("#7b7b93")
ACCENT_COLOR = pygame.Color("#5c67f2")
ACCENT_HOVER = pygame.Color("#707bf8")
GREEN_COLOR = pygame.Color("#2ecc71")
RED_COLOR = pygame.Color("#e74c3c")
CYAN_COLOR = pygame.Color("#00d2d3")

# Obstacles disponibles dans le jeu
TOOLS = [
    {"sym": "W", "name": "Mur", "key": pygame.K_1, "img": "assets/rooms/obstacles/walls/wall_01.png", "color": "#7f8c8d"},
    {"sym": "P", "name": "Pilier", "key": pygame.K_2, "img": "assets/rooms/obstacles/pillars/pillar_00.png", "color": "#e67e22"},
    {"sym": "C", "name": "Caisse", "key": pygame.K_3, "img": "assets/rooms/obstacles/containers/container_01.png", "color": "#f1c40f"},
    {"sym": "B", "name": "Baril", "key": pygame.K_4, "img": "assets/rooms/obstacles/containers/container_02.png", "color": "#d35400"},
    {"sym": "S", "name": "Pierre", "key": pygame.K_5, "img": "assets/rooms/obstacles/stones/stone_01.png", "color": "#95a5a6"},
    {"sym": ".", "name": "Gomme", "key": pygame.K_0, "img": None, "color": "#2c3e50"},
]

ENEMIES = [
    {"class": "CinderImp", "name": "Cinder Imp", "icon": "assets/enemies/cinder_imp.png"},
    {"class": "Gorehound", "name": "Gorehound", "icon": "assets/enemies/gorehound.png"},
    {"class": "Bloodwing", "name": "Bloodwing", "icon": "assets/enemies/bloodwing.png"},
    {"class": "Spikeborn", "name": "Spikeborn", "icon": "assets/enemies/spikeborn.png"},
]


class Button:
    """Bouton minimaliste et réactif."""

    def __init__(self, rect, text, callback=None, bg=PANEL_COLOR, fg=TEXT_COLOR, font_size=13):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.fg = fg
        self.font_size = font_size
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface, font, highlight=False):
        color = ACCENT_HOVER if (self.hovered or highlight) else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, width=1, border_radius=4)

        txt_surf = font.render(self.text, True, self.fg)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))


class RoomEditor:
    """Éditeur de niveau principal."""

    def __init__(self, json_filename="rooms.json"):
        pygame.init()
        pygame.joystick.init()
        pygame.display.set_caption("Éditeur de Salle - Donjon")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Polices
        self.font = pygame.font.SysFont("Segoe UI", 13)
        self.font_bold = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 11)

        # Fichier et données
        self.filepath = os.path.join(ROOT_DIR, json_filename)
        self.data = {"tiers": {}}
        self.tier = "0"
        self.room_idx = 0
        self.dirty = False

        # Outil actif & curseurs
        self.tool = "W"
        self.cursor = [8, 3]  # [col, row]
        self.mouse_painting = False
        self.mouse_button = 1
        self.show_grid = True

        # Historique d'annulation
        self.history = []

        # Notifications discrètes (toast)
        self.toast_text = ""
        self.toast_timer = 0.0

        # Manette
        self.joystick = None
        self._init_joystick()
        self.stick_timer = 0.0
        self.stick_dir = (0, 0)

        # Cache d'images
        self.images = {}
        self.tiles_cache = {}

        # Zones écran
        self.canvas_rect = pygame.Rect(16, 56, 990, 680)
        self.sidebar_rect = pygame.Rect(1020, 56, 324, 680)

        # Fond officiel de la salle
        self._init_room_bg()

        # Chargement et initialisation des boutons
        self.load()
        self._build_ui()

    def _init_joystick(self):
        """Initialise la première manette détectée."""
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            except pygame.error:
                self.joystick = None

    def _init_room_bg(self):
        """Charge le fond graphique du jeu adapté aux dimensions du canevas."""
        bg_file = os.path.join(ROOT_DIR, "assets", "rooms", "default.png")
        if os.path.exists(bg_file):
            try:
                raw = pygame.image.load(bg_file).convert()
                self.room_bg = pygame.transform.scale(raw, (self.canvas_rect.width, self.canvas_rect.height))
            except Exception:
                self.room_bg = None
        else:
            self.room_bg = None

        # Aire de jeu délimitée (Play Area)
        self.play_area = pygame.Rect(
            self.canvas_rect.x + self.canvas_rect.width * PLAY_AREA_X_RATIO,
            self.canvas_rect.y + self.canvas_rect.height * PLAY_AREA_Y_RATIO,
            self.canvas_rect.width * PLAY_AREA_W_RATIO,
            self.canvas_rect.height * PLAY_AREA_H_RATIO,
        )

    def load_image(self, rel_path):
        """Charge et met en cache une image PNG avec canal alpha."""
        if not rel_path:
            return None
        if rel_path not in self.images:
            full = os.path.join(ROOT_DIR, rel_path)
            if os.path.exists(full):
                try:
                    self.images[rel_path] = pygame.image.load(full).convert_alpha()
                except Exception:
                    self.images[rel_path] = None
            else:
                self.images[rel_path] = None
        return self.images[rel_path]

    # --- Gestion des données des salles ---
    def get_room(self):
        """Renvoie le dictionnaire de la salle en cours."""
        tiers = self.data.setdefault("tiers", {})
        if self.tier not in tiers:
            tiers[self.tier] = {"rooms": []}

        rooms = tiers[self.tier].setdefault("rooms", [])
        if not rooms:
            rooms.append({
                "id": 0,
                "enemies": [{"class": "CinderImp", "count": 1}],
                "layout": ["." * 16 for _ in range(6)],
                "max_enemies": 3,
            })
            self.room_idx = 0

        self.room_idx = max(0, min(self.room_idx, len(rooms) - 1))
        return rooms[self.room_idx]

    def load(self):
        """Charge le fichier JSON."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.show_toast("Fichier chargé")
            except Exception as e:
                self.show_toast(f"Erreur de lecture: {e}")
                self.data = {"tiers": {"0": {"rooms": []}}}
        else:
            self.data = {"tiers": {"0": {"rooms": []}}}

        tiers = sorted(list(self.data.get("tiers", {}).keys()))
        if tiers and self.tier not in tiers:
            self.tier = tiers[0]
        self.dirty = False

    def save(self):
        """Sauvegarde avec copie de secours automatique."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f_src:
                    content = f_src.read()
                with open(self.filepath + ".bak", "w", encoding="utf-8") as f_bak:
                    f_bak.write(content)

            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)

            self.dirty = False
            self.show_toast("Sauvegardé avec succès !")
        except Exception as e:
            self.show_toast(f"Erreur de sauvegarde: {e}")

    def show_toast(self, text):
        self.toast_text = text
        self.toast_timer = 2.2

    def push_undo(self):
        """Enregistre l'état du layout avant modification."""
        room = self.get_room()
        self.history.append({
            "tier": self.tier,
            "room_idx": self.room_idx,
            "layout": [row[:] for row in room.get("layout", [])],
        })
        if len(self.history) > 40:
            self.history.pop(0)
        self.dirty = True

    def undo(self):
        """Annule la dernière pose."""
        if not self.history:
            self.show_toast("Rien à annuler")
            return
        last = self.history.pop()
        self.tier = last["tier"]
        self.room_idx = last["room_idx"]
        self.get_room()["layout"] = last["layout"]
        self.show_toast("Action annulée")

    # --- Construction de l'interface utilisateur ---
    def _build_ui(self):
        self.buttons = []

        # 1. Barre supérieure (Header)
        y = 12
        # Tier: <, > et +
        self.buttons.append(Button((16, y, 28, 28), "<", self.prev_tier))
        self.buttons.append(Button((80, y, 28, 28), ">", self.next_tier))
        self.buttons.append(Button((114, y, 28, 28), "+", self.add_tier, bg=PANEL_BORDER))

        # Salle: <, > et actions
        self.buttons.append(Button((240, y, 28, 28), "<", self.prev_room))
        self.buttons.append(Button((380, y, 28, 28), ">", self.next_room))
        self.buttons.append(Button((416, y, 76, 28), "+ Salle", self.new_room))
        self.buttons.append(Button((498, y, 76, 28), "Dupliquer", self.dup_room))
        self.buttons.append(Button((580, y, 66, 28), "Suppr.", self.del_room, fg=RED_COLOR))

        # Outils rapides
        self.buttons.append(Button((660, y, 76, 28), "Annuler", self.undo))
        self.buttons.append(Button((742, y, 76, 28), "Murs Bord", self.toggle_borders))
        self.buttons.append(Button((824, y, 66, 28), "Vider", self.clear_room))

        # Sauvegarder
        self.buttons.append(Button((900, y, 106, 28), "Sauvegarder", self.save, bg=GREEN_COLOR, fg=pygame.Color("#ffffff")))

        # 2. Panneau latéral droit (Sidebar)
        bx = self.sidebar_rect.x + 14
        bw = self.sidebar_rect.width - 28

        # Outils / Palette (6 boutons)
        self.tool_buttons = []
        ty = self.sidebar_rect.y + 44
        tw = (bw - 8) // 2
        for i, t in enumerate(TOOLS):
            col = i % 2
            row = i // 2
            rx = bx + col * (tw + 8)
            ry = ty + row * 34

            def make_cb(sym=t["sym"]):
                return lambda: self.set_tool(sym)

            b = Button((rx, ry, tw, 30), f"{t['sym']} • {t['name']}", make_cb)
            self.tool_buttons.append((b, t["sym"]))
            self.buttons.append(b)

        # Dimensions de la grille
        dy = ty + 3 * 34 + 24
        self.buttons.append(Button((bx + 80, dy, 24, 22), "-", lambda: self.resize_grid(-1, 0)))
        self.buttons.append(Button((bx + 110, dy, 24, 22), "+", lambda: self.resize_grid(1, 0)))
        self.buttons.append(Button((bx + 215, dy, 24, 22), "-", lambda: self.resize_grid(0, -1)))
        self.buttons.append(Button((bx + 245, dy, 24, 22), "+", lambda: self.resize_grid(0, 1)))

        # Configuration Ennemis
        ey = dy + 54
        self.buttons.append(Button((bx + 215, ey, 24, 22), "-", lambda: self.adjust_max_enemies(-1)))
        self.buttons.append(Button((bx + 245, ey, 24, 22), "+", lambda: self.adjust_max_enemies(1)))

        # Ennemis individuels
        ey += 36
        self.enemy_rows = []
        for en in ENEMIES:
            cls_name = en["class"]

            def make_dec(c=cls_name):
                return lambda: self.adjust_enemy(c, -1)

            def make_inc(c=cls_name):
                return lambda: self.adjust_enemy(c, 1)

            btn_m = Button((bx + 215, ey, 24, 22), "-", make_dec)
            btn_p = Button((bx + 245, ey, 24, 22), "+", make_inc)
            self.buttons.extend([btn_m, btn_p])
            self.enemy_rows.append((cls_name, en["name"], btn_m, btn_p, ey, en["icon"]))
            ey += 30

    # --- Actions d'édition ---
    def set_tool(self, sym):
        self.tool = sym

    def cycle_tool(self, delta):
        symbols = [t["sym"] for t in TOOLS]
        idx = symbols.index(self.tool) if self.tool in symbols else 0
        self.tool = symbols[(idx + delta) % len(symbols)]

    def prev_room(self):
        rooms = self.data["tiers"].get(self.tier, {}).get("rooms", [])
        if rooms:
            self.room_idx = (self.room_idx - 1) % len(rooms)

    def next_room(self):
        rooms = self.data["tiers"].get(self.tier, {}).get("rooms", [])
        if rooms:
            self.room_idx = (self.room_idx + 1) % len(rooms)

    def new_room(self):
        self.push_undo()
        rooms = self.data["tiers"].setdefault(self.tier, {}).setdefault("rooms", [])
        new_id = max([r.get("id", 0) for r in rooms], default=-1) + 1
        rooms.append({
            "id": new_id,
            "enemies": [{"class": "CinderImp", "count": 1}],
            "layout": ["." * 16 for _ in range(6)],
            "max_enemies": 3,
        })
        self.room_idx = len(rooms) - 1
        self.show_toast(f"Salle #{new_id} créée")

    def dup_room(self):
        self.push_undo()
        rooms = self.data["tiers"].setdefault(self.tier, {}).setdefault("rooms", [])
        current = self.get_room()
        new_id = max([r.get("id", 0) for r in rooms], default=-1) + 1
        cloned = json.loads(json.dumps(current))
        cloned["id"] = new_id
        rooms.append(cloned)
        self.room_idx = len(rooms) - 1
        self.show_toast(f"Salle #{new_id} dupliquée")

    def del_room(self):
        rooms = self.data["tiers"].get(self.tier, {}).get("rooms", [])
        if len(rooms) <= 1:
            self.show_toast("Impossible de supprimer la seule salle")
            return
        self.push_undo()
        del rooms[self.room_idx]
        self.room_idx = max(0, self.room_idx - 1)
        self.show_toast("Salle supprimée")

    def prev_tier(self):
        tiers = sorted(list(self.data["tiers"].keys()), key=lambda x: int(x) if x.isdigit() else str(x))
        if tiers:
            idx = tiers.index(self.tier) if self.tier in tiers else 0
            self.tier = tiers[(idx - 1) % len(tiers)]
            self.room_idx = 0

    def next_tier(self):
        tiers = sorted(list(self.data["tiers"].keys()), key=lambda x: int(x) if x.isdigit() else str(x))
        if tiers:
            idx = tiers.index(self.tier) if self.tier in tiers else 0
            self.tier = tiers[(idx + 1) % len(tiers)]
            self.room_idx = 0

    def add_tier(self):
        self.push_undo()
        nums = [int(k) for k in self.data["tiers"].keys() if k.isdigit()]
        new_tier = str(max(nums) + 1 if nums else 0)
        self.data["tiers"][new_tier] = {
            "rooms": [{
                "id": 0,
                "enemies": [{"class": "CinderImp", "count": 1}],
                "layout": ["." * 16 for _ in range(6)],
                "max_enemies": 3,
            }]
        }
        self.tier = new_tier
        self.room_idx = 0
        self.show_toast(f"Palier {new_tier} créé")

    def resize_grid(self, dc, dr):
        room = self.get_room()
        layout = room.get("layout", [])
        rows = len(layout)
        cols = len(layout[0]) if rows > 0 else 16

        new_cols = max(8, min(24, cols + dc))
        new_rows = max(4, min(14, rows + dr))
        if new_cols == cols and new_rows == rows:
            return

        self.push_undo()
        new_layout = []
        for r in range(new_rows):
            if r < rows:
                row_str = layout[r]
                new_layout.append(row_str + "." * (new_cols - cols) if new_cols > cols else row_str[:new_cols])
            else:
                new_layout.append("." * new_cols)
        room["layout"] = new_layout

    def clear_room(self):
        self.push_undo()
        room = self.get_room()
        layout = room.get("layout", [])
        room["layout"] = ["." * len(layout[0]) for _ in range(len(layout))]
        self.show_toast("Salle vidée")

    def toggle_borders(self):
        self.push_undo()
        room = self.get_room()
        layout = [list(r) for r in room.get("layout", [])]
        rows = len(layout)
        cols = len(layout[0])

        all_w = all(layout[0][c] == "W" and layout[rows - 1][c] == "W" for c in range(cols))
        target = "." if all_w else "W"

        for c in range(cols):
            layout[0][c] = target
            layout[rows - 1][c] = target
        for r in range(rows):
            layout[r][0] = target
            layout[r][cols - 1] = target

        room["layout"] = ["".join(r) for r in layout]
        self.show_toast("Murs de bordure ajustés")

    def adjust_max_enemies(self, delta):
        room = self.get_room()
        room["max_enemies"] = max(1, min(25, room.get("max_enemies", 3) + delta))
        self.dirty = True

    def adjust_enemy(self, cls_name, delta):
        room = self.get_room()
        enemies = room.setdefault("enemies", [])
        target = next((e for e in enemies if e.get("class") == cls_name), None)

        if target is None and delta > 0:
            enemies.append({"class": cls_name, "count": delta})
        elif target is not None:
            new_cnt = target.get("count", 0) + delta
            if new_cnt <= 0:
                enemies.remove(target)
            else:
                target["count"] = new_cnt
        self.dirty = True

    # --- Grille et peinture ---
    def get_grid_rects(self):
        """Calcule la taille et la position des cases dans la zone de jeu."""
        room = self.get_room()
        layout = room.get("layout", [])
        rows = max(1, len(layout))
        cols = max(1, len(layout[0])) if layout else 1

        tile_size = min(self.play_area.width / cols, self.play_area.height / rows)
        grid_w = cols * tile_size
        grid_h = rows * tile_size

        gx = self.play_area.x + (self.play_area.width - grid_w) / 2
        gy = self.play_area.y + (self.play_area.height - grid_h) / 2
        return cols, rows, tile_size, gx, gy

    def set_tile(self, col, row, sym):
        room = self.get_room()
        layout = room.get("layout", [])
        if 0 <= row < len(layout) and 0 <= col < len(layout[row]):
            if layout[row][col] != sym:
                chars = list(layout[row])
                chars[col] = sym
                layout[row] = "".join(chars)
                self.dirty = True

    def pipette(self, col, row):
        room = self.get_room()
        layout = room.get("layout", [])
        if 0 <= row < len(layout) and 0 <= col < len(layout[row]):
            self.tool = layout[row][col]
            self.show_toast(f"Outil pipeté : {self.tool}")

    # --- Gestion de la manette ---
    def handle_gamepad(self, dt):
        if not self.joystick:
            return

        cols, rows, _, _, _ = self.get_grid_rects()

        # Direction (Stick gauche ou D-Pad)
        dx, dy = 0, 0
        if self.joystick.get_numhats() > 0:
            hx, hy = self.joystick.get_hat(0)
            dx, dy = hx, -hy

        if dx == 0 and dy == 0 and self.joystick.get_numaxes() >= 2:
            ax = self.joystick.get_axis(0)
            ay = self.joystick.get_axis(1)
            if abs(ax) > 0.25:
                dx = 1 if ax > 0 else -1
            if abs(ay) > 0.25:
                dy = 1 if ay > 0 else -1

        # Répétition fluide
        cur_dir = (dx, dy)
        step = (0, 0)
        if cur_dir != (0, 0):
            if cur_dir != self.stick_dir:
                self.stick_dir = cur_dir
                self.stick_timer = 0.0
                step = cur_dir
            else:
                self.stick_timer += dt
                if self.stick_timer > 0.22:
                    self.stick_timer -= 0.08
                    step = cur_dir
        else:
            self.stick_dir = (0, 0)
            self.stick_timer = 0.0

        if step != (0, 0):
            self.cursor[0] = max(0, min(cols - 1, self.cursor[0] + step[0]))
            self.cursor[1] = max(0, min(rows - 1, self.cursor[1] + step[1]))

        # Peinture continue au curseur manette
        if self.joystick.get_button(0):  # Bouton A (Poser)
            self.set_tile(self.cursor[0], self.cursor[1], self.tool)
        elif self.joystick.get_button(1):  # Bouton B (Gomme)
            self.set_tile(self.cursor[0], self.cursor[1], ".")

    # --- Rendu graphique ---
    def draw(self):
        self.screen.fill(BG_COLOR)

        # 1. En-tête (Header)
        tier_txt = f"Tier {self.tier}"
        self.screen.blit(self.font_bold.render(tier_txt, True, ACCENT_COLOR), (48, 16))

        room = self.get_room()
        rooms = self.data["tiers"].get(self.tier, {}).get("rooms", [])
        room_label = f"Salle #{room.get('id', self.room_idx)} ({self.room_idx + 1}/{len(rooms)})"
        r_surf = self.font_bold.render(room_label, True, TEXT_COLOR)
        self.screen.blit(r_surf, r_surf.get_rect(center=(310, 26)))

        # 2. Canevas de la salle
        pygame.draw.rect(self.screen, PANEL_COLOR, self.canvas_rect, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.canvas_rect, width=1, border_radius=6)

        if self.room_bg is not None:
            self.screen.blit(self.room_bg, self.canvas_rect.topleft)

        # Play Area délimitée
        pygame.draw.rect(self.screen, pygame.Color(255, 120, 180, 50), self.play_area, 1)

        cols, rows, tile_size, gx, gy = self.get_grid_rects()
        self.cursor[0] = max(0, min(cols - 1, self.cursor[0]))
        self.cursor[1] = max(0, min(rows - 1, self.cursor[1]))

        # Spawn joueur 3x3 au centre
        mid_c, mid_r = cols // 2, rows // 2
        for r in range(max(0, mid_r - 1), min(rows, mid_r + 2)):
            for c in range(max(0, mid_c - 1), min(cols, mid_c + 2)):
                rect = pygame.Rect(gx + c * tile_size, gy + r * tile_size, tile_size, tile_size)
                s = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                s.fill((0, 210, 211, 40))
                self.screen.blit(s, rect.topleft)

        # Rendu des cases
        layout = room.get("layout", [])
        for r in range(rows):
            row_str = layout[r] if r < len(layout) else "." * cols
            for c in range(cols):
                sym = row_str[c] if c < len(row_str) else "."
                rect = pygame.Rect(gx + c * tile_size, gy + r * tile_size, tile_size, tile_size)

                if self.show_grid:
                    pygame.draw.rect(self.screen, (255, 255, 255, 25), rect, 1)

                if sym != ".":
                    self._draw_tile(sym, rect)

        # Survol souris
        mx, my = pygame.mouse.get_pos()
        if self.canvas_rect.collidepoint((mx, my)) and gx <= mx < gx + cols * tile_size and gy <= my < gy + rows * tile_size:
            hc = int((mx - gx) / tile_size)
            hr = int((my - gy) / tile_size)
            h_rect = pygame.Rect(gx + hc * tile_size, gy + hr * tile_size, tile_size, tile_size)
            pygame.draw.rect(self.screen, (255, 255, 255, 120), h_rect, 2)

        # Curseur Manette
        cur_rect = pygame.Rect(gx + self.cursor[0] * tile_size, gy + self.cursor[1] * tile_size, tile_size, tile_size)
        pygame.draw.rect(self.screen, CYAN_COLOR, cur_rect, 2, border_radius=3)

        # 3. Panneau latéral (Sidebar)
        pygame.draw.rect(self.screen, PANEL_COLOR, self.sidebar_rect, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.sidebar_rect, width=1, border_radius=6)

        bx = self.sidebar_rect.x + 14
        self.screen.blit(self.font_bold.render("OUTILS", True, MUTED_COLOR), (bx, self.sidebar_rect.y + 16))

        # Outils actifs
        for b, sym in self.tool_buttons:
            b.draw(self.screen, self.font_bold if sym == self.tool else self.font, highlight=(sym == self.tool))

        # Dimensions
        dim_y = self.sidebar_rect.y + 166
        self.screen.blit(self.font_bold.render("GRILLE", True, MUTED_COLOR), (bx, dim_y))
        self.screen.blit(self.font.render(f"Colonnes: {cols}", True, TEXT_COLOR), (bx, dim_y + 26))
        self.screen.blit(self.font.render(f"Lignes: {rows}", True, TEXT_COLOR), (bx + 140, dim_y + 26))

        # Ennemis
        ey = dim_y + 60
        self.screen.blit(self.font_bold.render("ENNEMIS", True, MUTED_COLOR), (bx, ey))
        self.screen.blit(self.font.render(f"Max simultanés : {room.get('max_enemies', 3)}", True, TEXT_COLOR), (bx, ey + 24))

        room_enemies = room.get("enemies", [])
        for cls_name, label, btn_m, btn_p, row_y, icon_path in self.enemy_rows:
            cnt = next((e.get("count", 0) for e in room_enemies if e.get("class") == cls_name), 0)
            col = TEXT_COLOR if cnt > 0 else MUTED_COLOR

            # Petite icône d'ennemi
            icon = self.load_image(icon_path)
            if icon:
                mini = pygame.transform.scale(icon, (20, 20))
                self.screen.blit(mini, (bx, row_y + 1))
            self.screen.blit(self.font.render(label, True, col), (bx + 26, row_y + 2))

            # Compteur
            c_surf = self.font_bold.render(str(cnt), True, ACCENT_COLOR if cnt > 0 else MUTED_COLOR)
            self.screen.blit(c_surf, (bx + 185, row_y + 2))

        # Boutons généraux
        for b in self.buttons:
            if b not in [tb[0] for tb in self.tool_buttons]:
                b.draw(self.screen, self.font)

        # 4. Barre d'état inférieure (Footer)
        status_y = HEIGHT - 32
        info_txt = f"Case : ({self.cursor[0] + 1}/{cols}, {self.cursor[1] + 1}/{rows}) • Outil sélectionné : {self.tool}"
        self.screen.blit(self.font_small.render(info_txt, True, MUTED_COLOR), (16, status_y))

        # Raccourcis manette / clavier
        gp_info = "🎮 (A) Poser  (B) Gomme  (X) Pipette  (LB/RB) Outils  (LT/RT) Salles  (Start) Sauvegarder  (Select) Annuler"
        lbl_gp = self.font_small.render(gp_info, True, CYAN_COLOR if self.joystick else MUTED_COLOR)
        self.screen.blit(lbl_gp, (WIDTH - lbl_gp.get_width() - 16, status_y))

        # Toast / Message éphémère
        if self.toast_timer > 0 and self.toast_text:
            t_surf = self.font_bold.render(self.toast_text, True, pygame.Color("#ffffff"))
            tw = t_surf.get_width() + 24
            th = 28
            t_rect = pygame.Rect((WIDTH - tw) // 2, HEIGHT - 52, tw, th)
            pygame.draw.rect(self.screen, ACCENT_COLOR, t_rect, border_radius=6)
            self.screen.blit(t_surf, t_surf.get_rect(center=t_rect.center))

        pygame.display.flip()

    def _draw_tile(self, sym, rect):
        """Affiche le sprite ou le symbole de l'obstacle."""
        tool = next((t for t in TOOLS if t["sym"] == sym), None)
        img = self.load_image(tool["img"] if tool else None)

        if img is not None:
            size = int(rect.width * 0.92)
            key = (tool["img"], size)
            if key not in self.tiles_cache:
                self.tiles_cache[key] = pygame.transform.scale(img, (size, size))
            scaled = self.tiles_cache[key]
            self.screen.blit(scaled, scaled.get_rect(center=rect.center))
        else:
            col = pygame.Color(tool["color"] if tool else "gray")
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, col, inner, border_radius=3)
            txt = self.font_bold.render(sym, True, pygame.Color("#ffffff"))
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    # --- Boucle d'événements ---
    def handle_events(self):
        cols, rows, tile_size, gx, gy = self.get_grid_rects()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Clics sur les boutons
            handled = False
            for b in self.buttons:
                if b.handle_event(event):
                    handled = True
                    break
            if handled:
                continue

            # Manette : boutons instantanés
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:  # X = Pipette
                    self.pipette(self.cursor[0], self.cursor[1])
                elif event.button == 4:  # LB = Outil précédent
                    self.cycle_tool(-1)
                elif event.button == 5:  # RB = Outil suivant
                    self.cycle_tool(1)
                elif event.button == 6:  # Select = Annuler
                    self.undo()
                elif event.button == 7:  # Start = Sauvegarder
                    self.save()

            elif event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                self._init_joystick()
                self.show_toast("Manette connectée" if self.joystick else "Manette déconnectée")

            # Clavier
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    self.save()
                elif event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                    self.undo()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_LEFT:
                    self.prev_room()
                elif event.key == pygame.K_RIGHT:
                    self.next_room()
                elif event.key == pygame.K_UP:
                    self.prev_tier()
                elif event.key == pygame.K_DOWN:
                    self.next_tier()
                elif event.key == pygame.K_e:
                    self.set_tool(".")
                else:
                    for t in TOOLS:
                        if event.key == t["key"] or (t["sym"] != "." and event.unicode.upper() == t["sym"]):
                            self.set_tool(t["sym"])
                            break

            # Souris
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if gx <= event.pos[0] < gx + cols * tile_size and gy <= event.pos[1] < gy + rows * tile_size:
                    c = int((event.pos[0] - gx) / tile_size)
                    r = int((event.pos[1] - gy) / tile_size)
                    self.cursor = [c, r]

                    if event.button == 1:
                        self.push_undo()
                        self.set_tile(c, r, self.tool)
                        self.mouse_painting = True
                        self.mouse_button = 1
                    elif event.button == 3:
                        self.push_undo()
                        self.set_tile(c, r, ".")
                        self.mouse_painting = True
                        self.mouse_button = 3
                    elif event.button == 2:
                        self.pipette(c, r)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    self.mouse_painting = False

            elif event.type == pygame.MOUSEMOTION and self.mouse_painting:
                if gx <= event.pos[0] < gx + cols * tile_size and gy <= event.pos[1] < gy + rows * tile_size:
                    c = int((event.pos[0] - gx) / tile_size)
                    r = int((event.pos[1] - gy) / tile_size)
                    self.set_tile(c, r, self.tool if self.mouse_button == 1 else ".")

    def update(self, dt):
        if self.toast_timer > 0:
            self.toast_timer -= dt
        self.handle_gamepad(dt)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


def main():
    editor = RoomEditor("rooms.json")
    editor.run()


if __name__ == "__main__":
    main()
