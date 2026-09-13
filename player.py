import pygame as pg
import beings
import attacks

class Player(beings.Beings):

    def __init__(self, name:str, x:float, y:float, sizex:float=26.25, sizey:float=80.5, hp:int=20):
        super().__init__(name, x, y, sizex, sizey, hp)
        self.speed = 300
        self.image = pg.image.load('./assets/simon.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (26.25, 80.5))

    def moove(self, dt, dir:pg.Vector2):
        self.direction = dir
        if self.direction.length()>0:
              self.direction.normalize()
        velocity = self.direction * self.speed
        self.position += velocity * dt
        self.rec.x = self.position.x
        self.rec.y = self.position.y
         
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

    def shoot(self, projectiles):
        projectile = attacks.Projectile(self.position.x, self.position.y, 3)
        projectiles.add(projectile)

    
    

    