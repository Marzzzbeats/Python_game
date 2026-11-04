import pygame

class Circle():
    """Crée le cercle de base d'attaque"""

    def __init__(self,
                 screen: pygame.Surface,
                 center: tuple[float, float] | pygame.Vector2,
                 direction : pygame.Vector2,
                 circle_coordinates : list[tuple]):

        self.screen = screen
        self.circle_center = center
        self.circle_direction = direction
        self.circle_coordinates = circle_coordinates

        for i in range(len(self.circle_coordinates)):
            proj = pygame.Vector2(self.coordinates[i])
            next = pygame.Vector2(self.coordinates[(i+1)%len(self.coordinates)])
            direction = (next - proj).normalize()

    

    def update(self, dt):
        pass