import math
import pygame
from core.asset_manager import AssetManager
from entities.projectiles.projectile import Projectile
from effects.lightning import LightningEffect


class Lightning(Projectile):
    """Projectile qui déclenche un éclair vers un ennemi proche à l'impact."""

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
        image = AssetManager.get_image("assets/player_projectile/lightning.png", scale_by=0.07, rotate=angle)

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

        self.chain_count = 3
        self.chain_radius = 200
        self.chain_damage = damage * 0.5

    def on_hit(self, enemy, enemies, effects) -> None:
        origin = pygame.Vector2(enemy.rect.center)
        self.hit_enemies.add(enemy)

        for _ in range(self.chain_count):
            target = None
            nearest_distance = self.chain_radius

            for candidate in enemies:
                if candidate.is_dead or candidate in self.hit_enemies:
                    continue

                distance = origin.distance_to(candidate.rect.center)

                if distance <= nearest_distance:
                    target = candidate
                    nearest_distance = distance

            if target is None:
                break

            self.hit_enemies.add(target)
            effects.add(LightningEffect(origin, target.rect.center))
            target.take_damage(self.chain_damage)

            origin = pygame.Vector2(target.rect.center)
