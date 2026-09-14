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

        if self.rect.y < 0 or self.ttl <= 0:
            self.kill()

class Spike(pg.sprite.Sprite):

    def __init__(self, x, y, dirx, diry, dammage):
        super().__init__()
        self.position = pg.Vector2(x, y)
        self.direction = pg.Vector2(dirx, diry)
        self.dammage = dammage
        self.image = pg.image.load('./assets/spike.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (10, 20))
        self.angle = self.direction.angle_to(pg.Vector2(0,-1))
        self.image = pg.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center = (x,y))
        self.speed = 700
        self.velocity = self.direction * self.speed
        

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position

        if self.rect.y < 0 or self.rect.y > 590 or self.rect.x < 0 or self.rect.x > 790 :
            self.kill()