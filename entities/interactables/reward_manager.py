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

    def get_random_rewards(self, player_upgrades: dict[str, int], count: int = 3) -> list[str]:
        """Renvoie des upgrades différents qui ne sont pas au maximum."""
        available = [
            upgrade_id
            for upgrade_id, data in self.data.items()
            if upgrade_id != "heal" and player_upgrades.get(upgrade_id, 0) < data["max_stacks"]
        ]

        rewards = random.sample(available, min(count, len(available)))
        while len(rewards) < count:
            rewards.append("heal")

        return rewards