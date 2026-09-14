import pygame as pg
import beings
import attacks
import random as rd

class Ennemy(beings.Beings, pg.sprite.Sprite):

    def __init__(self, name, x, y, sizex=15, sizey=15, hp=30):
        beings.Beings.__init__(self, name, x, y, sizex, sizey, hp)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((sizex, sizey))
        self.image.fill("red")
        self.rect = self.image.get_rect(center = (x,y))
        self.dammage = 1
        self.moove_rate = 0.5 #changement de directions par secondes
        self.moove_counter = 1/self.moove_rate
        self.shooting_rate = 0.5
        self.shoot_timer = 1/self.shooting_rate

    def attack(self):
        """Lance une attaque"""
        print("Attaque!")

    def randomMoove(self, dt):
        """Bouge l'ennemi dans une direction aléatoire"""
        self.moove_counter += dt
        print(self.moove_counter)
        speed = 300
        if self.moove_counter >= self.moove_rate:
            posx = rd.randint(-1, 1)
            posy = rd.randint(-1, 1)
            self.direction.x = posx
            self.direction.y = posy
            self.moove_counter = 0
        velocity = self.direction * speed
        self.position += velocity * dt
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def spikeAttack(self, dt, projectiles_ennemy):
        self.shoot_timer += dt
        if self.shoot_timer >= 1/self.shooting_rate:
            pos = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
            for position in pos:
                projectile = attacks.Spike(self.position.x, self.position.y, position[0], position[1], 3)
                projectiles_ennemy.add(projectile)
                print("ok")
            self.shoot_timer = 0
        print(self.shoot_timer)
        
    def update(self, dt, projectiles_ennemy):

        if self.rect.y < 0 :
            self.rect.y = 0
            self.position.y = 0
        if self.rect.y > 550:
            self.rect.y = 550
            self.position.y = 550
        if self.rect.x < 0 :
            self.rect.x = 0
            self.position.x = 0
        if self.rect.x > 750 :
            self.rect.x = 750
            self.position.x = 750

        if not self.alive:
            self.kill()
        self.randomMoove(dt)
        self.spikeAttack(dt, projectiles_ennemy)
        