import pygame



def collide_hitbox( a, b):
    return a.hitbox.colliderect(b.hitbox)



class Room:
    def __init__(self, gameplay):
        self.gameplay = gameplay
        self.all_enemies = pygame.sprite.Group()


    def check_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.gameplay.player.player_projectiles,
            self.all_enemies,
            True,
            False,
            collide_hitbox
        )

        for projectile, enemies_hit in collisions.items():
            for enemy in enemies_hit:
                enemy.take_damage(projectile.damage)


    def update(self, dt):
        self.check_collisions()
        self.all_enemies.update(dt)


    def draw(self):
        self.all_enemies.draw(self.gameplay.game.screen)

        for enemy in self.all_enemies:
            pygame.draw.rect(
                self.gameplay.game.screen,
                "yellow",
                enemy.rect,
                2
            )
            pygame.draw.rect(
                self.gameplay.game.screen,
                "red",
                enemy.hitbox,
                2
            )