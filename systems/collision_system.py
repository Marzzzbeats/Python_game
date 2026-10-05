import pygame
from core.constants import DEBUG_MODE


def collide_hitbox(a: pygame.sprite.Sprite, b: pygame.sprite.Sprite) -> bool:
    """Vérifie la collision entre deux sprites en se basant sur leurs hitboxes et masques éventuels."""
    hitbox_a = getattr(a, "hitbox", a.rect)
    hitbox_b = getattr(b, "hitbox", b.rect)

    if not hitbox_a.colliderect(hitbox_b):
        return False

    mask_a = getattr(a, "mask", None)
    mask_b = getattr(b, "mask", None)

    if mask_a is not None and mask_b is not None:
        offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
        return mask_a.overlap(mask_b, offset) is not None

    return True


class CollisionSystem:
    """Système dédié à la détection et résolution de toutes les collisions du jeu."""

    @staticmethod
    def handle_player_projectiles_vs_enemies(player_projectiles: pygame.sprite.Group, enemies: pygame.sprite.Group):
        """Gère l'impact des projectiles du joueur contre les ennemis."""
        hits = pygame.sprite.groupcollide(
            player_projectiles,
            enemies,
            dokilla=True,
            dokillb=False,
            collided=collide_hitbox
        )

        for projectile, enemies_hit in hits.items():
            for enemy in enemies_hit:
                enemy.take_damage(getattr(projectile, "damage", 1))

    @staticmethod
    def handle_enemy_projectiles_vs_player(enemy_projectiles: pygame.sprite.Group, player):
        """Gère l'impact des projectiles ennemis sur le joueur."""
        if player.dead or DEBUG_MODE:
            return

        hits = pygame.sprite.spritecollide(
            player,
            enemy_projectiles,
            dokill=True,
            collided=collide_hitbox
        )

        for projectile in hits:
            player.take_damage(getattr(projectile, "damage", 1))

    @staticmethod
    def handle_projectiles_vs_obstacles(projectiles: pygame.sprite.Group, obstacles: pygame.sprite.Group):
        """Détruit les projectiles qui heurtent un obstacle."""
        pygame.sprite.groupcollide(
            projectiles,
            obstacles,
            dokilla=True,
            dokillb=False,
            collided=collide_hitbox
        )

    @staticmethod
    def handle_player_vs_enemies_contact(player, enemies: pygame.sprite.Group):
        """Gère les dégâts de contact des ennemis au corps-à-corps."""
        if player.dead:
            return

        hits = pygame.sprite.spritecollide(
            player,
            enemies,
            dokill=False,
            collided=collide_hitbox
        )

        for enemy in hits:
            # Si l'ennemi inflige des dégâts de contact (ex: Gorehound)
            contact_damage = getattr(enemy, "contact_damage", 1)
            player.take_damage(contact_damage)

    @staticmethod
    def check_obstacle_collision(hitbox: pygame.Rect, obstacles: pygame.sprite.Group) -> bool:
        """Vérifie si une hitbox entre en collision avec un des obstacles."""
        for obstacle in obstacles:
            obs_hitbox = getattr(obstacle, "hitbox", obstacle.rect)
            if hitbox.colliderect(obs_hitbox):
                return True
        return False
