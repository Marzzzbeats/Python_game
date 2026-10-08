import json
import os
import pygame
from rooms.room import Room


class RoomManager:
    """Gère le chargement des salles depuis rooms.json et la progression du joueur."""

    def __init__(self, json_path: str = "rooms.json"):
        self.json_path = json_path
        self.data = self._load_data()
        self.current_tier = 0
        self.current_room_index = 0

    def _load_data(self) -> dict:
        """Charge le fichier JSON des salles une seule fois."""
        if not os.path.exists(self.json_path):
            return {"tiers": {"0": {"rooms": []}}}

        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_room_count(self, tier: int = 0) -> int:
        """Nombre de salles disponibles pour le palier donné."""
        tier_data = self.data.get("tiers", {}).get(str(tier), {})
        return len(tier_data.get("rooms", []))

    def create_room(self, tier: int, room_index: int, play_surface: pygame.Surface, play_area: pygame.Rect, reward_manager, player_upgrades: dict) -> Room:
        """Instancie la salle correspondant au tier et à l'index donnés."""
        tier_data = self.data.get("tiers", {}).get(str(tier), {})
        rooms = tier_data.get("rooms", [])

        if not rooms:
            # Salle vide par défaut en cas d'absence de données
            fallback_data = {"id": 0, "enemies": [], "layout": ["." * 16] * 6}
            return Room(fallback_data, play_surface, play_area, reward_manager, player_upgrades)

        # Index sécurisé avec modulo
        safe_index = room_index % len(rooms)
        room_data = rooms[safe_index]
        return Room(room_data, play_surface, play_area, reward_manager, player_upgrades)

    def next_room(self, play_surface: pygame.Surface, play_area: pygame.Rect, reward_manager, player_upgrades: dict) -> Room:
        """Passe à la salle suivante."""
        self.current_room_index += 1
        max_rooms = self.get_room_count(self.current_tier)
        if self.current_room_index >= max_rooms:
            # Si toutes les salles du tier sont finies, recommence ou passe au tier suivant
            self.current_room_index = 0

        return self.create_room(self.current_tier, self.current_room_index, play_surface, play_area, reward_manager, player_upgrades)

    def reset(self, play_surface: pygame.Surface, play_area: pygame.Rect, reward_manager, player_upgrades: dict) -> Room:
        """Réinitialise la progression à la première salle."""
        self.current_room_index = 0
        return self.create_room(self.current_tier, self.current_room_index, play_surface, play_area, reward_manager, player_upgrades)
