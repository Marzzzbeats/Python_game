import pygame
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy
from core.constants import ENEMY_BASE_PROJECTILE_DAMAGE, ENEMY_BASE_PROJECTILE_SPEED, ENEMY_BASE_MAX_HP, ENEMY_BASE_SPEED, ENEMY_BASE_CONTACT_DAMAGE


class Spikeborn(Enemy):
    """Ennemi lourdement cuirassé, lent mais doté d'une forte résistance."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        speed: float = ENEMY_BASE_SPEED*0.9,
        damage: int = ENEMY_BASE_PROJECTILE_DAMAGE*1.2,
        max_hp: int = ENEMY_BASE_MAX_HP*1.2,
    ):
        image = AssetManager.get_image("assets/enemies/spikeborn.png", scale_by=0.65)
        super().__init__(
            pos=pos,
            image=image,
            speed=speed,
            damage=damage,
            max_hp=max_hp,
            contact_damage=2,
            hitbox_scale=0.7
        )

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        super().update(dt, player, play_area, projectile_group)

        if player is None or player.dead or self.is_dead:
            return

        direction = self.get_direction_to(player.rect.center)
        self.update_position(direction * self.speed * dt, play_area)
