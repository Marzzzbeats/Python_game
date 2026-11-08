import pygame


class Scene:
    """Classe de base pour toutes les scènes de jeu (Menus, Gameplay, etc.)."""

    def __init__(self, game):
        self.game = game

    def handle_events(self, event: pygame.event.Event):
        """Gestion des événements généraux."""
        if event.type == pygame.QUIT:
            self.game.running = False

    def update(self, dt: float):
        """Mise à jour logique par frame."""
        pass

    def draw(self):
        """Rendu graphique par frame."""
        pass

    def on_enter(self):
        """Appelé lors de l'activation de la scène."""
        pass

    def on_exit(self):
        """Appelé lors de la sortie de la scène."""
        pass
