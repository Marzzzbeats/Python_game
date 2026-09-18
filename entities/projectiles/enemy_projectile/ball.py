import pygame
from entities.projectiles.projectile import Projectile



class BallProjectile(Projectile):

    def __init__(self, screen, pos, direction, speed, damage):
        image = pygame.image.load("assets/enemy_projectile/cinder_imp.png").convert_alpha()
        image = pygame.transform.scale_by(image, 2)
        super().__init__(screen, pos, direction, speed, damage, image)


    def scale_hitbox(self):
        self.hitbox.scale_by_ip(1)


    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center