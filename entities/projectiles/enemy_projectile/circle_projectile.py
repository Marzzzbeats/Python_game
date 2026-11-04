import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile
from entities.projectiles.enemy_projectile.circle import Circle

class CircleProjectile(Circle, Projectile):
    """Cercle de boules de feu tirée par les ennemis (ex: bloodwing)."""

    def __init__(
        self,
        screen: pygame.Surface,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        owner: str,
        speed: float = 200,
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
            owner=owner,
            hitbox_scale=0.7
        )

    def update(self, dt):


        
        return

    def getPos(self)->tuple:
        """Renvoie la position du projectile"""
        return self.pos

    