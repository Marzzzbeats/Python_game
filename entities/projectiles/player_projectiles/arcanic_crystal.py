import math
import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile


class ArcanicCrystal(Projectile):
    """Projectile de base du joueur tiré en ligne droite avec rotation selon l'angle."""

    def __init__(
        self,
        area: pygame.Rect,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        angle: float,
        owner: str,
        speed: float,
        damage: int,
        img_scale: float,
        source_player
    ):
        dir_vec = pygame.Vector2(direction)
        angle_img = -math.degrees(math.atan2(dir_vec.y, dir_vec.x)) if dir_vec.length_squared() > 0 else 0

        # Récupération et transformation de l'image via l'AssetManager
        self.base_image = AssetManager.get_image("assets/player_projectile/arcanic_crystal.png", scale_by=0.07 * img_scale)
        image = self.base_image

        super().__init__(
            play_area=area,
            pos=pos,
            direction=dir_vec,
            speed=speed*1.2,
            damage=damage,
            image=image,
            owner=owner,
            remaining_pierces=2,
            hitbox_scale=0.4,
            source_player=source_player
        )

        self.persistent = True
        self.hit_cooldown = 1.0
        self.hit_timers = {}
        self.angle = angle
        self.rayon = 150

    
    def on_hit(self, enemy, enemies: pygame.sprite.Group, effects: pygame.sprite.Group) -> None:
        """Applique les effets du projectile à l'impact."""
        self._reset_hit_enemies()


    def move(self, dt: float):
        """Fait tourner l'objet autour du joueur."""

        self.angle += self.speed * dt * 0.1
        angle_rad = math.radians(self.angle)

        self.pos.x = self.source_player.rect.centerx + self.rayon * math.cos(angle_rad)
        self.pos.y = self.source_player.rect.centery + self.rayon * math.sin(angle_rad)

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

    def update(self, dt: float):
        """Mise à jour à chaque frame."""
        self.move(dt)

        center = self.rect.center
        self.image = pygame.transform.rotate(self.base_image, -self.angle + 90)
        self.rect = self.image.get_rect(center=center)

        for enemy in list(self.hit_timers):
            self.hit_timers[enemy] -= dt
            if self.hit_timers[enemy] <= 0:
                del self.hit_timers[enemy]