import math
import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile
from effects.explosion import ExplosionEffect


class Radiation(Projectile):
    """Projectile de base du joueur tiré en ligne droite avec rotation selon l'angle."""

    def __init__(
        self,
        area: pygame.Rect,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        owner: str,
        speed: float,
        damage: int,
        source_player
    ):
        dir_vec = pygame.Vector2(direction)
        angle = -math.degrees(math.atan2(dir_vec.y, dir_vec.x)) if dir_vec.length_squared() > 0 else 0

        # Récupération et transformation de l'image via l'AssetManager
        image = AssetManager.get_image("assets/player_projectile/radiation.png", scale_by=0.07, rotate=angle)

        super().__init__(
            play_area=area,
            pos=pos,
            direction=dir_vec,
            speed=speed,
            damage=damage,
            image=image,
            owner=owner,
            hitbox_scale=0.4,
            source_player=source_player
        )

        self.explosion_radius = 150
        self.explosion_damage = damage * 0.5


    def on_hit(self, enemy, enemies: pygame.sprite.Group, effects: pygame.sprite.Group) -> None:
        """Inflige des dégâts autour du point d'impact."""
        impact_pos = pygame.Vector2(self.rect.center)

        effects.add(
            ExplosionEffect(
                pos=impact_pos,
                radius=self.explosion_radius,
                color=(100, 255, 60),
                duration=0.25
            )
        )

        for target in list(enemies):
            if target.is_dead:
                continue

            distance = impact_pos.distance_to(target.rect.center)

            if distance <= self.explosion_radius:
                target.take_damage(self.explosion_damage)