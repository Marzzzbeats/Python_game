import pygame
import random
from entities.obstacles.obstacle import Obstacle



class Pillar(Obstacle):
    def __init__(self, x, y, play_surface):

        image = pygame.image.load(f"assets/rooms/obstacles/pillars/pillar_0{random.randint(0,9)}.png").convert_alpha()
        super().__init__(x, y, image, play_surface)

