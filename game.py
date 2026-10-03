import pygame
from core.constants import FPS
from scenes.gameplay import Gameplay
from scenes.scene import Scene


class Game:
    """Moteur central du jeu : boucle principale, synchronisation temporelle et routage de scènes."""

    def __init__(self, monitor_width: int, monitor_height: int):
        screen_size = (int(monitor_width * 0.9), int(monitor_height * 0.9))
        self.screen = pygame.display.set_mode(size=screen_size)
        pygame.display.set_caption("Dungeon Crawler")

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene: Scene | None = None

        # Démarrage direct sur la scène de jeu
        self.change_scene(Gameplay(self))

    def change_scene(self, new_scene: Scene):
        """Permet de basculer proprement entre différentes scènes."""
        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = new_scene
        self.current_scene.on_enter()

    def run(self):
        """Boucle de jeu cadencée à 60 FPS."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

    def handle_events(self):
        """Délègue les événements pygame à la scène active."""
        for event in pygame.event.get():
            if self.current_scene is not None:
                self.current_scene.handle_events(event)

    def update(self, dt: float):
        """Délègue la logique à la scène active."""
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self):
        """Délègue le rendu à la scène active."""
        if self.current_scene is not None:
            self.current_scene.draw()
