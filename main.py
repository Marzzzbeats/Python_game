import pygame
from core.constants import DEFAULT_SCREEN_HEIGHT, DEFAULT_SCREEN_WIDTH
from game import Game


def main():
    """Point d'entrée du jeu."""
    pygame.init()
    pygame.joystick.init()

    # Détection de la résolution écran avec repli sécurisé
    try:
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            monitor_width, monitor_height = sizes[0]
        else:
            monitor_width, monitor_height = DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT
    except (AttributeError, IndexError):
        monitor_width, monitor_height = DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

    game = Game(monitor_width, monitor_height)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()