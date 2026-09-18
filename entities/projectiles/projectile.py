import pygame


class Projectile(pygame.sprite.Sprite):

    def __init__(self, play_surface, pos, direction, speed, damage, image):
        super().__init__()

        self.screen = play_surface

        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction).normalize()

        self.speed = speed
        self.damage = damage

        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = self.rect.copy()
        self.scale_hitbox()


    def update(self, dt):
        self.move()

        if not self.rect.colliderect(self.screen.get_rect()):
            self.kill()

        

