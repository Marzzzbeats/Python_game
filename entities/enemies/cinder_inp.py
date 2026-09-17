import pygame
from entities.enemies.enemy import Enemy
from entities.projectiles.enemy_projectile.ball import BallProjectile


class CinderImp(Enemy):
    def __init__(self, gameplay, all_enemies_projectile, pos, image, speed, damage, max_life):
        self.gameplay = gameplay
        self.all_enemies_projectile = all_enemies_projectile
        image = pygame.image.load("assets/enemies/cinder_imp.png").convert_alpha()
        image = pygame.transform.scale_by(image, 0.6)

        super().__init__(gameplay, pos, image, speed, damage, max_life)


    def find_player_direction(self, player):
        direction = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )

        if direction.length() != 0:
            direction = direction.normalize()

        return direction


    def shoot(self):
        projectile = BallProjectile(
            screen=self.gameplay.play_surface,
            pos=self.rect.center,
            direction=self.find_player_direction(self.gameplay.player),
            speed=10,
            damage=1
        )

        self.gameplay.all_projectiles.add(projectile)
        self.enemy_projectiles.add(projectile)
        self.all_enemies_projectile.add(projectile)


    def update(self, dt):
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_cooldown
