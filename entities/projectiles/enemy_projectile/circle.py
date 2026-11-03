import pygame

class Circle():
    """Crée le cercle de base d'attaque"""

    def __init__(self,
                 screen: pygame.Surface,
                 center: tuple[float, float] | pygame.Vector2,
                 direction : pygame.Vector2,
                 circle_coordinates : list[pygame.Vector2]
                 ):

        self.screen = screen
        self.circle_center = center
        self.circle_direction = direction
        self.circle_coordinates = circle_coordinates

    def update(self, dt):
        