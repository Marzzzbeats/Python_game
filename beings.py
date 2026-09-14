import pygame as pg

class Beings():

    def __init__(self, name:str, x:float, y:float, sizex:float, sizey:float, hp:int):
        self.position = pg.Vector2(x,y)
        self.direction = pg.Vector2(0,0)
        self.rect = pg.Rect(self.position.x, self.position.y, sizex, sizey)
        self.name = name
        self.alive = True
        self.hp = hp

    def hpLoss(self, damage:int):
            """Perte de vie"""
            self.hp -= damage
    
    def isDead(self):
        """Vérifie si les hp sont à 0, et agit sur le statut en conséquence"""
        if self.hp <= 0 and self.alive:
            self.alive = False

    