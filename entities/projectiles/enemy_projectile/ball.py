import pygame
from entities.projectiles.projectile import Projectile



class BallProjectile(Projectile):

    def __init__(self, screen, pos, direction, speed, damage):
        image = pygame.image.load("assets/enemy_projectile/cinder_imp.png").convert_alpha()
        image = pygame.transform.scale_by(image, 2)
        super().__init__(screen, pos, direction, speed, damage, image)

    def move(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center