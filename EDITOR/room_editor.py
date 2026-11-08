"""Éditeur visuel de salles (Room Editor) pour le jeu de donjon.

Fonctionnalités :
- Modification visuelle du layout de la salle en temps réel (clic gauche / glisser pour poser, clic droit pour effacer).
- Affichage du décor réel du jeu (fond, délimitation de l'aire de jeu, indicateur de zone de spawn du joueur).
- Palette d'obstacles complète : Mur (W), Pilier (P), Caisse/Coffre (C), Baril (B), Pierre (S), Gomme/Sol vide (.).
- Configuration des ennemis de la salle (CinderImp, Gorehound, Bloodwing, Spikeborn) et de max_enemies.
- Gestion des salles : changement de salle, ajout de salle, duplication, suppression, gestion des paliers (tiers).
- Redimensionnement dynamique de la grille (colonnes et lignes).
- Outils rapides : Vider la salle, Générer bordures de murs, Historique Annuler (Ctrl+Z).
- Sauvegarde et chargement direct au format exact du fichier rooms.json avec sauvegarde automatique (.bak).
"""

import copy
import json
import os
import sys
import pygame

# S'assurer que la racine du projet est dans sys.path pour accéder aux assets et modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.constants import (
    PLAY_AREA_X_RATIO,
    PLAY_AREA_Y_RATIO,
    PLAY_AREA_W_RATIO,
    PLAY_AREA_H_RATIO,
)

# --- Configuration de la fenêtre et couleurs ---
WINDOW_WIDTH = 1380
WINDOW_HEIGHT = 800
FPS = 60

# Palette moderne sombre
COLOR_BG = pygame.Color("#0c0b16")
COLOR_PANEL_BG = pygame.Color("#161526")
COLOR_PANEL_BORDER = pygame.Color("#2a2845")
COLOR_TEXT_PRIMARY = pygame.Color("#f0f0f5")
COLOR_TEXT_SECONDARY = pygame.Color("#9593b2")
COLOR_ACCENT = pygame.Color("#6c5ce7")
COLOR_ACCENT_HOVER = pygame.Color("#8075e8")
COLOR_DANGER = pygame.Color("#e84118")
COLOR_SUCCESS = pygame.Color("#4cd137")
COLOR_WARNING = pygame.Color("#e1b12c")
COLOR_GRID_LINE = pygame.Color(255, 255, 255, 40)
COLOR_GRID_HOVER = pygame.Color(255, 255, 255, 90)
COLOR_SPAWN_AREA = pygame.Color(0, 168, 255, 60)

# Définition des types d'obstacles disponibles
OBSTACLE_TYPES = [
    {
        "symbol": "W",
        "name": "Mur",
        "sub": "Wall",
        "color": pygame.Color("#7f8c8d"),
        "image_path": "assets/rooms/obstacles/walls/wall_01.png",
        "key": pygame.K_1,
        "key_label": "1",
    },
    {
        "symbol": "P",
        "name": "Pilier",
        "sub": "Pillar",
        "color": pygame.Color("#e67e22"),
        "image_path": "assets/rooms/obstacles/pillars/pillar_00.png",
        "key": pygame.K_2,
        "key_label": "2",
    },
    {
        "symbol": "C",
        "name": "Caisse",
        "sub": "Container",
        "color": pygame.Color("#f1c40f"),
        "image_path": "assets/rooms/obstacles/containers/container_01.png",
        "key": pygame.K_3,
        "key_label": "3",
    },
    {
        "symbol": "B",
        "name": "Baril",
        "sub": "Barrel",
        "color": pygame.Color("#d35400"),
        "image_path": "assets/rooms/obstacles/containers/container_02.png",
        "key": pygame.K_4,
        "key_label": "4",
    },
    {
        "symbol": "S",
        "name": "Pierre",
        "sub": "Stone",
        "color": pygame.Color("#95a5a6"),
        "image_path": "assets/rooms/obstacles/stones/stone_01.png",
        "key": pygame.K_5,
        "key_label": "5",
    },
    {
        "symbol": ".",
        "name": "Gomme",
        "sub": "Sol vide",
        "color": pygame.Color("#34495e"),
        "image_path": None,
        "key": pygame.K_0,
        "key_label": "0 / E",
    },
]

AVAILABLE_ENEMIES = [
    {"class": "CinderImp", "name": "Cinder Imp", "icon": "assets/enemies/cinder_imp.png"},
    {"class": "Gorehound", "name": "Gorehound", "icon": "assets/enemies/gorehound.png"},
    {"class": "Bloodwing", "name": "Bloodwing", "icon": "assets/enemies/bloodwing.png"},
    {"class": "Spikeborn", "name": "Spikeborn", "icon": "assets/enemies/spikeborn.png"},
]


class FontManager:
    """Gestionnaire de polices avec mise en cache."""
    _fonts = {}

    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in cls._fonts:
            try:
                font = pygame.font.SysFont("Segoe UI", size, bold=bold)
            except Exception:
                font = pygame.font.Font(None, size)
            cls._fonts[key] = font
        return cls._fonts[key]


class Button:
    """Composant bouton interactif."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback,
        bg_color=COLOR_PANEL_BORDER,
        hover_color=COLOR_ACCENT,
        text_color=COLOR_TEXT_PRIMARY,
        font_size=16,
        bold=False,
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.bold = bold
        self.is_hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        color = self.hover_color if (self.is_hovered and self.enabled) else self.bg_color
        if not self.enabled:
            color = pygame.Color(self.bg_color.r // 2, self.bg_color.g // 2, self.bg_color.b // 2)

        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=6)

        font = FontManager.get(self.font_size, bold=self.bold)
        txt_surf = font.render(self.text, True, self.text_color if self.enabled else COLOR_TEXT_SECONDARY)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class RoomEditor:
    """Application principale de l'éditeur visuel de salles."""

    def __init__(self, json_path: str = "rooms.json"):
        pygame.init()
        pygame.display.set_caption("Donjon - Éditeur Visuel de Salles")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.json_path = os.path.join(PROJECT_ROOT, json_path)
        self.data = {"tiers": {}}
        self.current_tier = "0"
        self.current_room_idx = 0

        # Outil sélectionné : symbole par défaut ('W')
        self.active_symbol = "W"
        self.is_mouse_painting = False
        self.paint_button = 1  # 1 = poser outil actif, 3 = effacer (.)

        # Historique d'annulation (Undo)
        self.undo_stack = []
        self.max_undo = 50

        # Notifications
        self.toast_message = ""
        self.toast_timer = 0.0
        self.toast_color = COLOR_SUCCESS

        # Affichage d'options
        self.show_grid = True
        self.show_spawn_zone = True

        # Mise en cache d'images
        self.cached_images = {}
        self.scaled_tile_cache = {}

        # Dimensions et surfaces
        self._init_layout_bounds()
        self.load_data()
        self._init_buttons()

    def _init_layout_bounds(self):
        """Définit les zones d'écran pour le canevas de jeu et le panneau latéral."""
        self.canvas_rect = pygame.Rect(20, 20, 940, 710)

        self.play_surface_rect = pygame.Rect(
            self.canvas_rect.x,
            self.canvas_rect.y,
            self.canvas_rect.width,
            self.canvas_rect.height
        )

        self.play_area = pygame.Rect(
            self.play_surface_rect.width * PLAY_AREA_X_RATIO,
            self.play_surface_rect.height * PLAY_AREA_Y_RATIO,
            self.play_surface_rect.width * PLAY_AREA_W_RATIO,
            self.play_surface_rect.height * PLAY_AREA_H_RATIO
        )

        self.sidebar_rect = pygame.Rect(980, 20, 380, 760)

        bg_path = os.path.join(PROJECT_ROOT, "assets", "rooms", "default.png")
        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                self.room_bg = pygame.transform.scale(
                    raw_bg,
                    (self.play_surface_rect.width, self.play_surface_rect.height)
                )
            except Exception:
                self.room_bg = None
        else:
            self.room_bg = None

    def _load_sprite(self, rel_path: str | None) -> pygame.Surface | None:
        """Charge une image d'obstacle ou d'ennemi."""
        if not rel_path:
            return None
        if rel_path in self.cached_images:
            return self.cached_images[rel_path]

        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path).convert_alpha()
                self.cached_images[rel_path] = img
                return img
            except Exception:
                pass
        return None

    def get_current_room(self) -> dict:
        """Récupère les données de la salle actuellement éditée."""
        tier_rooms = self.data.get("tiers", {}).get(self.current_tier, {}).get("rooms", [])
        if not tier_rooms:
            default_room = {
                "id": 0,
                "enemies": [{"class": "CinderImp", "count": 1}],
                "layout": ["." * 16 for _ in range(6)],
                "max_enemies": 3,
            }
            if self.current_tier not in self.data.setdefault("tiers", {}):
                self.data["tiers"][self.current_tier] = {"rooms": []}
            self.data["tiers"][self.current_tier]["rooms"].append(default_room)
            self.current_room_idx = 0
            return default_room

        self.current_room_idx = max(0, min(self.current_room_idx, len(tier_rooms) - 1))
        return tier_rooms[self.current_room_idx]

    def load_data(self):
        """Charge ou initialise les salles depuis le fichier JSON."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.show_toast(f"Chargé : {os.path.basename(self.json_path)}", COLOR_SUCCESS)
            except Exception as e:
                self.show_toast(f"Erreur lecture : {e}", COLOR_DANGER)
                self.data = {"tiers": {"0": {"rooms": []}}}
        else:
            self.data = {"tiers": {"0": {"rooms": []}}}
            self.show_toast("Nouveau fichier créé", COLOR_WARNING)

        if not self.data.get("tiers"):
            self.data["tiers"] = {"0": {"rooms": []}}

        available_tiers = sorted(list(self.data["tiers"].keys()))
        if self.current_tier not in available_tiers:
            self.current_tier = available_tiers[0]

        self.get_current_room()

    def save_data(self):
        """Sauvegarde les salles dans le fichier rooms.json avec formatage propre."""
        try:
            if os.path.exists(self.json_path):
                backup_path = self.json_path + ".bak"
                try:
                    with open(self.json_path, "r", encoding="utf-8") as f_src:
                        content = f_src.read()
                    with open(backup_path, "w", encoding="utf-8") as f_dst:
                        f_dst.write(content)
                except Exception:
                    pass

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)

            self.show_toast(f"Sauvegardé dans {os.path.basename(self.json_path)} !", COLOR_SUCCESS)
        except Exception as e:
            self.show_toast(f"Erreur sauvegarde : {e}", COLOR_DANGER)

    def show_toast(self, message: str, color=COLOR_SUCCESS, duration: float = 3.0):
        """Affiche un message temporaire en bas de l'écran."""
        self.toast_message = message
        self.toast_color = color
        self.toast_timer = duration

    def _push_undo(self):
        """Enregistre l'état actuel du layout pour permettre l'annulation."""
        room = self.get_current_room()
        layout_copy = [row[:] for row in room.get("layout", [])]
        self.undo_stack.append({
            "tier": self.current_tier,
            "room_idx": self.current_room_idx,
            "layout": layout_copy,
        })
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

    def undo(self):
        """Annule la dernière modification de layout."""
        if not self.undo_stack:
            self.show_toast("Rien à annuler", COLOR_WARNING, duration=1.5)
            return

        last_state = self.undo_stack.pop()
        self.current_tier = last_state["tier"]
        self.current_room_idx = last_state["room_idx"]
        room = self.get_current_room()
        room["layout"] = last_state["layout"]
        self.show_toast("Modification annulée", COLOR_SUCCESS, duration=1.2)

    # --- Actions sur les salles et paliers ---
    def prev_room(self):
        rooms = self.data["tiers"].get(self.current_tier, {}).get("rooms", [])
        if rooms:
            self.current_room_idx = (self.current_room_idx - 1) % len(rooms)

    def next_room(self):
        rooms = self.data["tiers"].get(self.current_tier, {}).get("rooms", [])
        if rooms:
            self.current_room_idx = (self.current_room_idx + 1) % len(rooms)

    def new_room(self):
        rooms = self.data["tiers"].setdefault(self.current_tier, {}).setdefault("rooms", [])
        new_id = max([r.get("id", 0) for r in rooms], default=-1) + 1
        new_room_data = {
            "id": new_id,
            "enemies": [{"class": "CinderImp", "count": 1}],
            "layout": ["." * 16 for _ in range(6)],
            "max_enemies": 3,
        }
        rooms.append(new_room_data)
        self.current_room_idx = len(rooms) - 1
        self.show_toast(f"Nouvelle salle #{new_id} créée", COLOR_SUCCESS)

    def duplicate_room(self):
        rooms = self.data["tiers"].setdefault(self.current_tier, {}).setdefault("rooms", [])
        current = self.get_current_room()
        new_id = max([r.get("id", 0) for r in rooms], default=-1) + 1
        cloned = copy.deepcopy(current)
        cloned["id"] = new_id
        rooms.append(cloned)
        self.current_room_idx = len(rooms) - 1
        self.show_toast(f"Salle dupliquée sous l'ID #{new_id}", COLOR_SUCCESS)

    def delete_room(self):
        rooms = self.data["tiers"].get(self.current_tier, {}).get("rooms", [])
        if len(rooms) <= 1:
            self.show_toast("Impossible de supprimer la dernière salle du palier", COLOR_DANGER)
            return
        del rooms[self.current_room_idx]
        self.current_room_idx = max(0, self.current_room_idx - 1)
        self.show_toast("Salle supprimée", COLOR_WARNING)

    def prev_tier(self):
        tiers = sorted(list(self.data["tiers"].keys()), key=lambda x: int(x) if x.isdigit() else x)
        idx = tiers.index(self.current_tier) if self.current_tier in tiers else 0
        self.current_tier = tiers[(idx - 1) % len(tiers)]
        self.current_room_idx = 0

    def next_tier(self):
        tiers = sorted(list(self.data["tiers"].keys()), key=lambda x: int(x) if x.isdigit() else x)
        idx = tiers.index(self.current_tier) if self.current_tier in tiers else 0
        self.current_tier = tiers[(idx + 1) % len(tiers)]
        self.current_room_idx = 0

    def add_tier(self):
        existing_numeric = [int(k) for k in self.data["tiers"].keys() if k.isdigit()]
        new_tier_idx = (max(existing_numeric) + 1) if existing_numeric else 0
        new_tier_key = str(new_tier_idx)
        self.data["tiers"][new_tier_key] = {
            "rooms": [
                {
                    "id": 0,
                    "enemies": [{"class": "CinderImp", "count": 1}],
                    "layout": ["." * 16 for _ in range(6)],
                    "max_enemies": 3,
                }
            ]
        }
        self.current_tier = new_tier_key
        self.current_room_idx = 0
        self.show_toast(f"Palier (Tier) {new_tier_key} créé !", COLOR_SUCCESS)

    # --- Actions sur la grille ---
    def resize_grid(self, delta_cols: int, delta_rows: int):
        room = self.get_current_room()
        layout = room.get("layout", [])
        cur_rows = len(layout)
        cur_cols = len(layout[0]) if cur_rows > 0 else 16

        new_rows = max(4, min(16, cur_rows + delta_rows))
        new_cols = max(8, min(24, cur_cols + delta_cols))

        if new_rows == cur_rows and new_cols == cur_cols:
            return

        self._push_undo()
        new_layout = []
        for r in range(new_rows):
            if r < cur_rows:
                old_row = layout[r]
                if new_cols > cur_cols:
                    new_row = old_row + "." * (new_cols - cur_cols)
                else:
                    new_row = old_row[:new_cols]
                new_layout.append(new_row)
            else:
                new_layout.append("." * new_cols)

        room["layout"] = new_layout

    def clear_room(self):
        room = self.get_current_room()
        layout = room.get("layout", [])
        if not layout:
            return
        self._push_undo()
        rows = len(layout)
        cols = len(layout[0])
        room["layout"] = ["." * cols for _ in range(rows)]
        self.show_toast("Salle vidée", COLOR_WARNING, duration=1.2)

    def border_walls(self):
        """Ajoute ou supprime une bordure de murs (W) tout autour de la pièce."""
        room = self.get_current_room()
        layout = room.get("layout", [])
        if not layout:
            return
        self._push_undo()
        rows = len(layout)
        cols = len(layout[0])

        grid = [list(row) for row in layout]
        all_walls = all(
            grid[0][c] == "W" and grid[rows - 1][c] == "W"
            for c in range(cols)
        ) and all(
            grid[r][0] == "W" and grid[r][cols - 1] == "W"
            for r in range(rows)
        )

        target_char = "." if all_walls else "W"
        for c in range(cols):
            grid[0][c] = target_char
            grid[rows - 1][c] = target_char
        for r in range(rows):
            grid[r][0] = target_char
            grid[r][cols - 1] = target_char

        room["layout"] = ["".join(row) for row in grid]
        msg = "Bordures retirées" if all_walls else "Bordures de murs ajoutées"
        self.show_toast(msg, COLOR_SUCCESS, duration=1.2)

    # --- Actions sur les ennemis ---
    def adjust_max_enemies(self, delta: int):
        room = self.get_current_room()
        val = max(1, min(20, room.get("max_enemies", 3) + delta))
        room["max_enemies"] = val

    def adjust_enemy_count(self, enemy_class: str, delta: int):
        room = self.get_current_room()
        enemies = room.setdefault("enemies", [])
        target = None
        for item in enemies:
            if item.get("class") == enemy_class:
                target = item
                break

        if target is None:
            if delta > 0:
                enemies.append({"class": enemy_class, "count": delta})
        else:
            new_count = target.get("count", 0) + delta
            if new_count <= 0:
                enemies.remove(target)
            else:
                target["count"] = new_count

    # --- Initialisation de l'interface des boutons ---
    def _init_buttons(self):
        """Construit les boutons du panneau de contrôle droit."""
        self.buttons = []
        bx = self.sidebar_rect.x + 15
        bw = self.sidebar_rect.width - 30

        # En-tête : Sauvegarde et Rechargement
        btn_y = 60
        half_w = (bw - 10) // 2
        self.btn_save = Button(
            pygame.Rect(bx, btn_y, half_w, 36),
            "Sauvegarder",
            self.save_data,
            bg_color=pygame.Color("#27ae60"),
            hover_color=pygame.Color("#2ecc71"),
            bold=True,
            font_size=15,
        )
        self.btn_reload = Button(
            pygame.Rect(bx + half_w + 10, btn_y, half_w, 36),
            "Recharger",
            self.load_data,
            bg_color=pygame.Color("#2c3e50"),
            hover_color=pygame.Color("#34495e"),
            font_size=14,
        )
        self.buttons.extend([self.btn_save, self.btn_reload])

        # Navigation Paliers (Tiers)
        btn_y += 50
        tier_btn_w = 34
        self.btn_prev_tier = Button(
            pygame.Rect(bx, btn_y, tier_btn_w, 30),
            "<",
            self.prev_tier,
            font_size=14,
        )
        self.btn_next_tier = Button(
            pygame.Rect(bx + bw - tier_btn_w * 2 - 10, btn_y, tier_btn_w, 30),
            ">",
            self.next_tier,
            font_size=14,
        )
        self.btn_add_tier = Button(
            pygame.Rect(bx + bw - tier_btn_w, btn_y, tier_btn_w, 30),
            "+",
            self.add_tier,
            bg_color=COLOR_ACCENT,
            font_size=14,
        )
        self.buttons.extend([self.btn_prev_tier, self.btn_next_tier, self.btn_add_tier])

        # Navigation Salles
        btn_y += 45
        room_nav_w = 40
        self.btn_prev_room = Button(
            pygame.Rect(bx, btn_y, room_nav_w, 32),
            "<",
            self.prev_room,
            font_size=16,
        )
        self.btn_next_room = Button(
            pygame.Rect(bx + bw - room_nav_w, btn_y, room_nav_w, 32),
            ">",
            self.next_room,
            font_size=16,
        )
        self.buttons.extend([self.btn_prev_room, self.btn_next_room])

        # Actions de salle : Ajouter, Dupliquer, Supprimer
        btn_y += 42
        action_w = (bw - 16) // 3
        self.btn_new_room = Button(
            pygame.Rect(bx, btn_y, action_w, 28),
            "+ Salle",
            self.new_room,
            font_size=13,
            bg_color=COLOR_ACCENT,
        )
        self.btn_dup_room = Button(
            pygame.Rect(bx + action_w + 8, btn_y, action_w, 28),
            "Dupliquer",
            self.duplicate_room,
            font_size=13,
        )
        self.btn_del_room = Button(
            pygame.Rect(bx + (action_w + 8) * 2, btn_y, action_w, 28),
            "Suppr.",
            self.delete_room,
            font_size=13,
            bg_color=COLOR_DANGER,
            hover_color=pygame.Color("#ff6b6b"),
        )
        self.buttons.extend([self.btn_new_room, self.btn_dup_room, self.btn_del_room])

        # Palette d'outils (2 colonnes)
        btn_y += 46
        self.tool_buttons = []
        tool_w = (bw - 10) // 2
        tool_h = 36
        for i, tool in enumerate(OBSTACLE_TYPES):
            col = i % 2
            row = i // 2
            tx = bx + col * (tool_w + 10)
            ty = btn_y + row * (tool_h + 8)

            def make_selector(sym=tool["symbol"]):
                return lambda: self.set_tool(sym)

            btn = Button(
                pygame.Rect(tx, ty, tool_w, tool_h),
                f"[{tool['key_label']}] {tool['symbol']} {tool['name']}",
                make_selector(),
                font_size=13,
                bold=True,
            )
            self.tool_buttons.append((btn, tool["symbol"]))
            self.buttons.append(btn)

        # Grille dimensions
        btn_y += (len(OBSTACLE_TYPES) + 1) // 2 * (tool_h + 8) + 12
        dim_btn_w = 28
        # Cols - / +
        self.btn_col_minus = Button(
            pygame.Rect(bx + 85, btn_y, dim_btn_w, 24),
            "-",
            lambda: self.resize_grid(-1, 0),
            font_size=14,
        )
        self.btn_col_plus = Button(
            pygame.Rect(bx + 145, btn_y, dim_btn_w, 24),
            "+",
            lambda: self.resize_grid(1, 0),
            font_size=14,
        )
        # Rows - / +
        self.btn_row_minus = Button(
            pygame.Rect(bx + 265, btn_y, dim_btn_w, 24),
            "-",
            lambda: self.resize_grid(0, -1),
            font_size=14,
        )
        self.btn_row_plus = Button(
            pygame.Rect(bx + 325, btn_y, dim_btn_w, 24),
            "+",
            lambda: self.resize_grid(0, 1),
            font_size=14,
        )
        self.buttons.extend([
            self.btn_col_minus,
            self.btn_col_plus,
            self.btn_row_minus,
            self.btn_row_plus,
        ])

        # Outils rapides de layout
        btn_y += 34
        quick_w = (bw - 16) // 3
        self.btn_undo = Button(
            pygame.Rect(bx, btn_y, quick_w, 28),
            "Annuler",
            self.undo,
            font_size=12,
        )
        self.btn_border = Button(
            pygame.Rect(bx + quick_w + 8, btn_y, quick_w, 28),
            "Murs Bord",
            self.border_walls,
            font_size=12,
        )
        self.btn_clear = Button(
            pygame.Rect(bx + (quick_w + 8) * 2, btn_y, quick_w, 28),
            "Vider",
            self.clear_room,
            font_size=12,
            bg_color=COLOR_PANEL_BORDER,
        )
        self.buttons.extend([self.btn_undo, self.btn_border, self.btn_clear])

        # Ennemis : max_enemies
        btn_y += 42
        self.btn_max_minus = Button(
            pygame.Rect(bx + 240, btn_y, 28, 24),
            "-",
            lambda: self.adjust_max_enemies(-1),
            font_size=14,
        )
        self.btn_max_plus = Button(
            pygame.Rect(bx + 300, btn_y, 28, 24),
            "+",
            lambda: self.adjust_max_enemies(1),
            font_size=14,
        )
        self.buttons.extend([self.btn_max_minus, self.btn_max_plus])

        # Ennemis : listes individuelles
        btn_y += 34
        self.enemy_buttons = []
        for en in AVAILABLE_ENEMIES:
            cls_name = en["class"]

            def make_dec(c=cls_name):
                return lambda: self.adjust_enemy_count(c, -1)

            def make_inc(c=cls_name):
                return lambda: self.adjust_enemy_count(c, 1)

            btn_m = Button(pygame.Rect(bx + 240, btn_y, 28, 22), "-", make_dec(), font_size=13)
            btn_p = Button(pygame.Rect(bx + 300, btn_y, 28, 22), "+", make_inc(), font_size=13)
            self.enemy_buttons.append((cls_name, btn_m, btn_p, btn_y))
            self.buttons.extend([btn_m, btn_p])
            btn_y += 28

    def set_tool(self, symbol: str):
        """Définit l'outil actif."""
        self.active_symbol = symbol

    # --- Gestion de la peinture sur la grille ---
    def get_grid_metrics(self):
        """Calcule les dimensions et la position de la grille dans l'aire de jeu."""
        room = self.get_current_room()
        layout = room.get("layout", [])
        rows = max(len(layout), 1)
        cols = max(len(layout[0]), 1) if layout else 1

        tile_size = min(self.play_area.width / cols, self.play_area.height / rows)
        grid_w = cols * tile_size
        grid_h = rows * tile_size

        grid_x = self.play_surface_rect.x + self.play_area.x + (self.play_area.width - grid_w) / 2
        grid_y = self.play_surface_rect.y + self.play_area.y + (self.play_area.height - grid_h) / 2

        return cols, rows, tile_size, grid_x, grid_y, grid_w, grid_h

    def screen_to_cell(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convertit les coordonnées pixels de la souris en index de case (col, row)."""
        cols, rows, tile_size, grid_x, grid_y, grid_w, grid_h = self.get_grid_metrics()

        if grid_x <= mx < grid_x + grid_w and grid_y <= my < grid_y + grid_h:
            col = int((mx - grid_x) / tile_size)
            row = int((my - grid_y) / tile_size)
            if 0 <= col < cols and 0 <= row < rows:
                return col, row
        return None

    def paint_tile_at(self, col: int, row: int, symbol: str):
        """Modifie le symbole d'une case de la grille."""
        room = self.get_current_room()
        layout = room.get("layout", [])
        if row < 0 or row >= len(layout):
            return
        row_str = layout[row]
        if col < 0 or col >= len(row_str):
            return

        if row_str[col] != symbol:
            row_list = list(row_str)
            row_list[col] = symbol
            layout[row] = "".join(row_list)

    # --- Rendu visuel ---
    def draw_canvas(self):
        """Affiche le décor de salle, l'aire de jeu, les cases et les obstacles."""
        # 1. Fond du canevas
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.canvas_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, self.canvas_rect, width=2, border_radius=10)

        # 2. Image de salle officielle (si disponible)
        if self.room_bg is not None:
            self.screen.blit(self.room_bg, self.play_surface_rect)
        else:
            pygame.draw.rect(self.screen, pygame.Color("#18162b"), self.play_surface_rect)

        # 3. Contour de l'aire de jeu (Play Area)
        play_area_abs = pygame.Rect(
            self.play_surface_rect.x + self.play_area.x,
            self.play_surface_rect.y + self.play_area.y,
            self.play_area.width,
            self.play_area.height
        )
        pygame.draw.rect(self.screen, pygame.Color(255, 105, 180, 80), play_area_abs, 1)

        # 4. Grille de la salle courante
        room = self.get_current_room()
        layout = room.get("layout", [])
        cols, rows, tile_size, grid_x, grid_y, grid_w, grid_h = self.get_grid_metrics()

        # Zone d'apparition du joueur (centre de la pièce)
        if self.show_spawn_zone:
            center_c = cols // 2
            center_r = rows // 2
            for r in range(max(0, center_r - 1), min(rows, center_r + 2)):
                for c in range(max(0, center_c - 1), min(cols, center_c + 2)):
                    cell_rect = pygame.Rect(grid_x + c * tile_size, grid_y + r * tile_size, tile_size, tile_size)
                    spawn_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    spawn_surf.fill(COLOR_SPAWN_AREA)
                    self.screen.blit(spawn_surf, cell_rect.topleft)

        # Rendu des cases et obstacles
        mx, my = pygame.mouse.get_pos()
        hovered_cell = self.screen_to_cell(mx, my)

        for r in range(rows):
            row_str = layout[r] if r < len(layout) else "." * cols
            for c in range(cols):
                tile_symbol = row_str[c] if c < len(row_str) else "."
                cell_rect = pygame.Rect(grid_x + c * tile_size, grid_y + r * tile_size, tile_size, tile_size)

                # Lignes de grille
                if self.show_grid:
                    pygame.draw.rect(self.screen, COLOR_GRID_LINE, cell_rect, 1)

                # Affichage de l'obstacle si présent
                if tile_symbol != ".":
                    self._draw_obstacle_tile(tile_symbol, cell_rect)

        # Surbrillance de la case survolée
        if hovered_cell is not None:
            hc, hr = hovered_cell
            hover_rect = pygame.Rect(grid_x + hc * tile_size, grid_y + hr * tile_size, tile_size, tile_size)
            pygame.draw.rect(self.screen, COLOR_GRID_HOVER, hover_rect, 2)

            # Aperçu translucide de l'outil sélectionné
            if self.active_symbol != ".":
                preview_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                preview_surf.fill((255, 255, 255, 35))
                self.screen.blit(preview_surf, hover_rect.topleft)

        # Label info de coordonnées en bas à gauche du canevas
        font = FontManager.get(14)
        if hovered_cell is not None:
            coord_text = f"Case : Colonne {hovered_cell[0] + 1}/{cols}, Ligne {hovered_cell[1] + 1}/{rows}"
        else:
            coord_text = f"Grille : {cols} x {rows} cases | Case : --"

        lbl_coord = font.render(coord_text, True, COLOR_TEXT_SECONDARY)
        self.screen.blit(lbl_coord, (self.canvas_rect.x + 15, self.canvas_rect.bottom - 28))

        # Raccourcis rappel
        help_text = "Clic Gche: Poser | Clic Drt: Gomme | Molette/Milieu: Pipette | Ctrl+S: Sauver | Ctrl+Z: Annuler | G: Grille"
        lbl_help = font.render(help_text, True, COLOR_TEXT_SECONDARY)
        self.screen.blit(lbl_help, (self.canvas_rect.x + 270, self.canvas_rect.bottom - 28))

    def _draw_obstacle_tile(self, symbol: str, cell_rect: pygame.Rect):
        """Dessine un obstacle spécifique dans la case donnée."""
        tool_info = next((t for t in OBSTACLE_TYPES if t["symbol"] == symbol), None)
        sprite = self._load_sprite(tool_info["image_path"] if tool_info else None)

        if sprite is not None:
            target_size = int(cell_rect.width * 0.95)
            cache_key = (tool_info["image_path"], target_size)

            if cache_key not in self.scaled_tile_cache:
                scaled = pygame.transform.scale(sprite, (target_size, target_size))
                self.scaled_tile_cache[cache_key] = scaled
            else:
                scaled = self.scaled_tile_cache[cache_key]

            sprite_rect = scaled.get_rect(center=cell_rect.center)
            self.screen.blit(scaled, sprite_rect)
        else:
            color = tool_info["color"] if tool_info else pygame.Color("gray")
            inner_rect = cell_rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, color, inner_rect, border_radius=4)
            font = FontManager.get(max(12, int(cell_rect.width * 0.5)), bold=True)
            txt = font.render(symbol, True, pygame.Color("white"))
            txt_rect = txt.get_rect(center=cell_rect.center)
            self.screen.blit(txt, txt_rect)

    def draw_sidebar(self):
        """Dessine le panneau latéral droit contenant toutes les commandes."""
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.sidebar_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, self.sidebar_rect, width=2, border_radius=10)

        bx = self.sidebar_rect.x + 15

        # Titre principal
        f_title = FontManager.get(20, bold=True)
        t_surf = f_title.render("ÉDITEUR DE SALLES", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(t_surf, (bx, 28))

        # Affichage du Palier (Tier) actuel
        f_sec = FontManager.get(15, bold=True)
        tier_label = f"PALIER (TIER) : {self.current_tier}"
        tier_surf = f_sec.render(tier_label, True, COLOR_ACCENT)
        self.screen.blit(tier_surf, (bx + 55, 114))

        # Affichage de la Salle courante
        room = self.get_current_room()
        rooms = self.data["tiers"].get(self.current_tier, {}).get("rooms", [])
        total_rooms = len(rooms)
        f_room = FontManager.get(16, bold=True)
        room_label = f"Salle #{room.get('id', self.current_room_idx)}  ({self.current_room_idx + 1} / {total_rooms})"
        r_surf = f_room.render(room_label, True, COLOR_TEXT_PRIMARY)
        r_rect = r_surf.get_rect(center=(self.sidebar_rect.centerx, 172))
        self.screen.blit(r_surf, r_rect)

        # Titre Outils
        tools_lbl = f_sec.render("OUTILS / PALETTE", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(tools_lbl, (bx, 252))

        # Mise à jour des styles de boutons d'outils
        for btn, sym in self.tool_buttons:
            if sym == self.active_symbol:
                btn.bg_color = COLOR_ACCENT
                btn.hover_color = COLOR_ACCENT_HOVER
                btn.text_color = COLOR_TEXT_PRIMARY
            else:
                btn.bg_color = COLOR_PANEL_BORDER
                btn.hover_color = pygame.Color("#3a3859")
                btn.text_color = COLOR_TEXT_PRIMARY

        # Dimensions de la grille
        cols, rows, _, _, _, _, _ = self.get_grid_metrics()
        dim_lbl = f_sec.render("DIMENSIONS GRILLE", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(dim_lbl, (bx, 420))

        f_txt = FontManager.get(14)
        c_txt = f_txt.render(f"Colonnes : {cols}", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(c_txt, (bx, 448))

        r_txt = f_txt.render(f"Lignes : {rows}", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(r_txt, (bx + 195, 448))

        # Configuration Ennemis
        en_title = f_sec.render("CONFIGURATION ENNEMIS", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(en_title, (bx, 514))

        max_e = room.get("max_enemies", 3)
        lbl_max = f_txt.render(f"Max ennemis simultanés : {max_e}", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(lbl_max, (bx, 542))

        # Liste des ennemis
        room_enemies = room.get("enemies", [])
        for cls_name, btn_m, btn_p, by in self.enemy_buttons:
            count = 0
            for item in room_enemies:
                if item.get("class") == cls_name:
                    count = item.get("count", 0)
                    break

            clr = COLOR_TEXT_PRIMARY if count > 0 else COLOR_TEXT_SECONDARY
            lbl_name = f_txt.render(cls_name, True, clr)
            self.screen.blit(lbl_name, (bx, by + 2))

            lbl_count = FontManager.get(14, bold=True).render(str(count), True, COLOR_ACCENT if count > 0 else COLOR_TEXT_SECONDARY)
            cnt_rect = lbl_count.get_rect(center=(bx + 285, by + 11))
            self.screen.blit(lbl_count, cnt_rect)

        # Total ennemis dans la configuration
        total_configured = sum(item.get("count", 0) for item in room_enemies)
        status_color = COLOR_WARNING if total_configured > max_e else COLOR_TEXT_SECONDARY
        lbl_total = FontManager.get(13).render(
            f"Total configuré : {total_configured} (Capacité max : {max_e})",
            True,
            status_color
        )
        self.screen.blit(lbl_total, (bx, 720))

        # Dessiner tous les boutons
        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_toast(self):
        """Affiche la notification toast en bas au centre."""
        if self.toast_timer > 0 and self.toast_message:
            font = FontManager.get(15, bold=True)
            txt_surf = font.render(self.toast_message, True, pygame.Color("#ffffff"))

            pad_x = 24
            pad_y = 10
            tw = txt_surf.get_width() + pad_x * 2
            th = txt_surf.get_height() + pad_y * 2
            toast_rect = pygame.Rect(
                (WINDOW_WIDTH - tw) // 2,
                WINDOW_HEIGHT - th - 16,
                tw,
                th
            )

            pygame.draw.rect(self.screen, self.toast_color, toast_rect, border_radius=8)
            pygame.draw.rect(self.screen, pygame.Color(255, 255, 255, 100), toast_rect, width=1, border_radius=8)

            txt_rect = txt_surf.get_rect(center=toast_rect.center)
            self.screen.blit(txt_surf, txt_rect)

    # --- Gestion des événements ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            btn_handled = False
            for btn in self.buttons:
                if btn.handle_event(event):
                    btn_handled = True
                    break

            if btn_handled:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.save_data()
                elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
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
                else:
                    for t in OBSTACLE_TYPES:
                        if event.key == t["key"] or (t["symbol"] != "." and event.unicode.upper() == t["symbol"]):
                            self.set_tool(t["symbol"])
                            break
                    if event.key == pygame.K_e:
                        self.set_tool(".")

            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = self.screen_to_cell(*event.pos)
                if cell is not None:
                    col, row = cell
                    if event.button == 1:
                        self._push_undo()
                        self.paint_tile_at(col, row, self.active_symbol)
                        self.is_mouse_painting = True
                        self.paint_button = 1
                    elif event.button == 3:
                        self._push_undo()
                        self.paint_tile_at(col, row, ".")
                        self.is_mouse_painting = True
                        self.paint_button = 3
                    elif event.button == 2:
                        room = self.get_current_room()
                        layout = room.get("layout", [])
                        if row < len(layout) and col < len(layout[row]):
                            sym = layout[row][col]
                            self.set_tool(sym)
                            self.show_toast(f"Outil sélectionné : {sym}", COLOR_ACCENT, duration=1.0)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    self.is_mouse_painting = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_mouse_painting:
                    cell = self.screen_to_cell(*event.pos)
                    if cell is not None:
                        col, row = cell
                        symbol = self.active_symbol if self.paint_button == 1 else "."
                        self.paint_tile_at(col, row, symbol)

    def update(self, dt: float):
        """Met à jour les temporisateurs et animations légères."""
        if self.toast_timer > 0:
            self.toast_timer -= dt

    def draw(self):
        """Rendu complet de la fenêtre de l'éditeur."""
        self.screen.fill(COLOR_BG)
        self.draw_canvas()
        self.draw_sidebar()
        self.draw_toast()
        pygame.display.flip()

    def run(self):
        """Boucle principale de l'éditeur."""
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
