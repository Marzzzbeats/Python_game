import pygame



class Enemy(pygame.sprite.Sprite):
    def __init__(self, gameplay, pos, image, speed, damage, max_hp, id):
        super().__init__()

        self.gameplay = gameplay
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

        self.id = id

    def die(self):
        self.kill()
        return self.id

    def take_damage(self, damage):
        res = -1
        self.hp -= damage

        if self.hp <= 0:
            res = self.die()
        return res

    def draw(self):
        self.gameplay.play_surface.blit(self.image, self.rect)
      
