import pygame
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy


class Gorehound(Enemy):
    """Molosse démoniaque rapide fonçant sur le joueur au corps-à-corps."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        speed: float = 210.0,
        damage: int = 1,
        max_hp: int = 6
    ):
        image = AssetManager.get_image("assets/enemies/gorehound.png", scale_by=0.6)
        super().__init__(
            pos=pos,
            image=image,
            speed=speed,
            damage=damage,
            max_hp=max_hp,
            contact_damage=1,
            hitbox_scale=0.65
        )

        self.contact_cooldown = 0.8
        self.contact_timer = 0.0

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        super().update(dt, player, play_area, projectile_group)

        if self.contact_timer > 0:
            self.contact_timer -= dt

        if player is None or player.dead or self.is_dead:
            return

        # Poursuite directe et agressive du joueur
        direction = self.get_direction_to(player.rect.center)
        self.update_position(direction * self.speed * dt, play_area)
