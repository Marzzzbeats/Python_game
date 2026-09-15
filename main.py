import pygame
from game import Game






if __name__ == '__main__':
    pygame.init()
    pygame.joystick.init()

    monitor_width, monitor_height = pygame.display.get_desktop_sizes()[0]

    game = Game(monitor_width, monitor_height)
    game.run()

    pygame.quit()