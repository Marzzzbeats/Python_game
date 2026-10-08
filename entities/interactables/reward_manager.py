import json
import os
import random


class RewardManager:
    """Gère le chargement des upgrades et le choix des récompenses."""

    def __init__(self, json_path: str = "upgrades.json"):
        self.json_path = json_path
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Charge le fichier JSON des upgrades une seule fois."""
        if not os.path.exists(self.json_path):
            return {}

        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_random_reward(self) -> str | None:
        """Renvoie l'identifiant d'un upgrade aléatoire."""
        if not self.data:
            return None

        return random.choice(list(self.data))