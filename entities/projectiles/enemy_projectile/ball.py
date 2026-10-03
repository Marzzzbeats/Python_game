import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile


class BallProjectile(Projectile):
    """Boule de feu tirée par les ennemis (ex: CinderImp)."""

    def __init__(
        self,
        screen: pygame.Surface,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        speed: float = 450,
        damage: int = 1
    ):
        image = AssetManager.get_image("assets/enemy_projectile/cinder_imp.png", scale_by=2.0)

        super().__init__(
            play_surface=screen,
            pos=pos,
            direction=direction,
            speed=speed,
            damage=damage,
            image=image,
            hitbox_scale=0.7
        )