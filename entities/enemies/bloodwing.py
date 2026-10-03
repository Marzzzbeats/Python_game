import math
import pygame
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy


class Bloodwing(Enemy):
    """Créature volante virevoltante effectuant des piqués vers le joueur."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        speed: float = 170.0,
        damage: int = 1,
        max_hp: int = 5
    ):
        image = AssetManager.get_image("assets/enemies/bloodwing.png", scale_by=0.6)
        super().__init__(
            pos=pos,
            image=image,
            speed=speed,
            damage=damage,
            max_hp=max_hp,
            contact_damage=1,
            hitbox_scale=0.6
        )

        self.angle_offset = 0.0
        self.dive_timer = 2.0

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        super().update(dt, player, play_area, projectile_group)

        if player is None or player.dead or self.is_dead:
            return

        self.angle_offset += dt * 3.0
        direction = self.get_direction_to(player.rect.center)

        # Mouvement ondulant sinusoïdal
        tangent = pygame.Vector2(-direction.y, direction.x) * math.sin(self.angle_offset) * 0.7
        combined_dir = (direction + tangent).normalize()

        self.update_position(combined_dir * self.speed * dt, play_area)
