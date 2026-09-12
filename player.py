import pygame as pg
import beings

class Player(beings.Beings):

    def __init__(self, name:str, x:float, y:float, sizex:float=26.25, sizey:float=80.5, hp:int=20):
        super().__init__(name, x, y, sizex, sizey, hp)
        self.speed = 300
        self.image = pg.image.load('./assets/simon.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (26.25, 80.5))

    def mooveUp(self, dt:float):
        """Bouge le player vers le haut"""
        self.rec.y -= dt*self.speed

    def mooveDown(self, dt:float):
        """Bouge le player vers le bas"""
        self.rec.y += dt*self.speed

    def mooveLeft(self, dt:float):
        """Bouge vers la gauche"""
        self.rec.x -= dt*self.speed

    def mooveRight(self, dt:float):
        """Bouge le player vers la droite"""
        self.rec.x += dt*self.speed

    def displayHp(self):
        font = pg.font.Font(None, 36)
        if self.alive:
            text = "HP :"
        if self.hp <= 5:
            text += " x "
        elif self.hp > 5 and self.hp <= 10 :
            text += " x x "
        elif self.hp > 10 and self.hp <= 15 :
                    text += " x x x "
        elif self.hp > 15 and self.hp <= 20 :
                    text += " x x x x "    

        text2 = font.render(text, True, (255,0,0))
        return text2


    
    

    