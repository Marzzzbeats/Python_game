import pygame
from entities.obstacles.obstacle import Obstacle



class Pillar(Obstacle):
    def __init__(self, x, y, play_surface):

        image = pygame.image.load("assets/rooms/obstacles/pillars/pillar_01.png").convert_alpha()
        super().__init__(x, y, image, play_surface)

