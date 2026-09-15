import pygame



class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, pos, image, speed, damage, max_hp):
        super().__init__()

        self.game = game
        self.screen = game.screen
        self.enemy_projectiles = pygame.sprite.Group()

        self.speed = speed
        self.damage = damage
        self.hp = max_hp
        self.max_hp = max_hp
        self.fire_rate = 1

        self.shoot_cooldown = 1/self.fire_rate
        self.shoot_timer = 0

        self.image = image
        self.rect = self.image.get_rect(center=pos)
        
        self.hitbox = self.rect.copy()
        self.hitbox.scale_by_ip(0.6)


    def take_damage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            self.kill()


    def draw(self):
        self.screen.blit(self.image, self.rect)
