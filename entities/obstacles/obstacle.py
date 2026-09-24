import pygame




class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, play_surface):
        super().__init__()

        self.x = x
        self.y = y
        self.play_surface = play_surface

        self.image = image
        self.rect = image.get_rect()
        self.hitbox = image.get_bounding_rect()


    def scale_rect(self, ratio):
        self.hitbox.scale_by_ip(ratio)
        self.hitbox.center = self.rect.center


    def draw(self):
        self.play_surface.blit(self.image, self.rect)


    
