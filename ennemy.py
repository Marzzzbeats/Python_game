import pygame as pg
import beings

class Ennemy(beings.Beings):

    def __init__(self, name, x, y, sizex=15, sizey=15, hp=30):
        super().__init__(name, x, y, sizex, sizey, hp)

    def attack(self):
        """Lance une attaque"""
        print("Attaque!")