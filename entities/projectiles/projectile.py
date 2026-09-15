import pygame


class Projectile(pygame.sprite.Sprite):

    def __init__(self, screen, pos, direction, speed, damage, image):
        super().__init__()

        self.screen = screen

        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction).normalize()

        self.speed = speed
        self.damage = damage

        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = self.rect.copy()
        self.hitbox.scale_by_ip(0.5)



    def update(self, dt):
        self.move()

        if not self.rect.colliderect(self.screen.get_rect()):
            self.kill()

        

