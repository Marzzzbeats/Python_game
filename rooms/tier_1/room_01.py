import pygame
from rooms.room import Room

from entities.enemies.cinder_inp import CinderImp
from entities.obstacles.pillar import Pillar


class RoomT1_01(Room):
    def __init__(self, gameplay):
        super().__init__(gameplay)


        enemy1 = CinderImp(gameplay, self.all_enemies_projectile, self.place_relative_play_area(50, 100), 10, 1, 5)
        self.all_enemies.add(enemy1)

        pillar1 = Pillar(-100, -100, gameplay.play_surface)
        self.all_obstacles.add(pillar1)

        self.place_all_obstacles()

        
