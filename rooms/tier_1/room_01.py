import pygame
from rooms.room import Room

from entities.enemies.cinder_inp import CinderImp


class RoomT1_01(Room):
    def __init__(self, gameplay):
        super().__init__(gameplay)


        image = pygame.image.load("assets/enemies/cinder_imp.png").convert_alpha()
        enemy1 = CinderImp(gameplay, (300,200), image, 10, 1, 5)
        self.all_enemies.add(enemy1)
