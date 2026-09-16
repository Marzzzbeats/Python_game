import pygame
import math
from entities.projectiles.projectile import Projectile



class StraightProjectile(Projectile):

    def __init__(self, screen, pos, direction, speed, damage):
        angle = -math.degrees(math.atan2(direction.y, direction.x))
        image = pygame.image.load("assets/player_projectile/base.png").convert_alpha()
        image = pygame.transform.scale_by(image, 0.1)
        image = pygame.transform.rotate(image, angle)
        super().__init__(screen, pos, direction, speed, damage, image)


    def scale_hitbox(self):
            self.hitbox.scale_by_ip(0.5)

    def move(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center