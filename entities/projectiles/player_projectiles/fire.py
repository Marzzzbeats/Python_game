import math
import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile


class Fire(Projectile):
    """Projectile de base du joueur tiré en ligne droite avec rotation selon l'angle."""

    def __init__(
        self,
        area: pygame.Rect,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        owner: str,
        speed: float = 550,
        damage: int = 1
    ):
        dir_vec = pygame.Vector2(direction)
        angle = -math.degrees(math.atan2(dir_vec.y, dir_vec.x)) if dir_vec.length_squared() > 0 else 0

        # Récupération et transformation de l'image via l'AssetManager
        image = AssetManager.get_image("assets/player_projectile/fire.png", scale_by=0.07, rotate=angle)

        super().__init__(
            play_area=area,
            pos=pos,
            direction=dir_vec,
            speed=speed,
            damage=damage,
            image=image,
            owner=owner,
            hitbox_scale=0.4
        )