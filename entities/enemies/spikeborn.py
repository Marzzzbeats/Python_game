import pygame
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy


class Spikeborn(Enemy):
    """Ennemi lourdement cuirassé, lent mais doté d'une forte résistance."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        speed: float = 85.0,
        damage: int = 2,
        max_hp: int = 12
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
