import pygame as pg
import beings

class Ennemy(beings.Beings, pg.sprite.Sprite):

    def __init__(self, name, x, y, sizex=15, sizey=15, hp=30):
        beings.Beings.__init__(self, name, x, y, sizex, sizey, hp)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((sizex, sizey))
        self.image.fill("red")
        self.rect = self.image.get_rect(center = (x,y))
        self.dammage = 1

    def attack(self):
        """Lance une attaque"""
        print("Attaque!")

    def update(self):
        if not self.alive:
            self.kill()