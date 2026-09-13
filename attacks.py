import pygame as pg

class Projectile(pg.sprite.Sprite):

    def __init__(self, x, y, dammage):
        super().__init__()
        self.position = pg.Vector2(x,y)
        self.speed = 500
        self.direction = pg.Vector2(0,-1)
        self.ttl = 1
        self.image = pg.Surface((3,10))
        self.image.fill("red")
        self.rect = self.image.get_rect(center = (x,y))
        self.velocity = self.direction * self.speed
        self.dammage = dammage

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position 
        print("ok")

        if self.rect.y < 0 :
            self.kill()

    