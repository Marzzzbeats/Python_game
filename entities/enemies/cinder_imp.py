import pygame
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy
from entities.projectiles.enemy_projectile.ball import BallProjectile


class CinderImp(Enemy):
    """Démon lanceur de boules de feu à distance."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        speed: float = 120.0,
        damage: int = 1,
        max_hp: int = 4,
    ):
        image = AssetManager.get_image("assets/enemies/cinder_imp.png", scale_by=0.6)
        super().__init__(
            pos=pos,
            image=image,
            speed=speed,
            damage=damage,
            max_hp=max_hp,
            contact_damage=1,
            hitbox_scale=0.6
        )

        self.fire_rate = 0.8  # tirs par seconde
        self.shoot_cooldown = 1.0 / self.fire_rate
        self.shoot_timer = self.shoot_cooldown * 0.5  # premier tir décalé

        # Comportement de distance
        self.preferred_distance = 320.0

    def shoot(self, target_pos: tuple[float, float] | pygame.Vector2, screen: pygame.Surface, projectile_group: pygame.sprite.Group):
        """Crée et projette une boule de feu vers la cible."""
        direction = self.get_direction_to(target_pos)
        projectile = BallProjectile(
            screen=screen,
            pos=self.rect.center,
            direction=direction,
            owner="enemy",
            speed=400,
            damage=self.damage
        )
        projectile_group.add(projectile)

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        super().update(dt, player, play_area, projectile_group)

        if player is None or player.dead or self.is_dead:
            return

        # IA de déplacement : garde ses distances
        dist = self.distance_to(player.rect.center)
        direction = self.get_direction_to(player.rect.center)

        if dist < self.preferred_distance - 60:
            # S'éloigne du joueur
            self.update_position(-direction * self.speed * dt, play_area)
        elif dist > self.preferred_distance + 60:
            # Se rapproche prudemment
            self.update_position(direction * (self.speed * 0.8) * dt, play_area)

        # Rechargement et tir
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            if projectile_group is not None and hasattr(player, "play_surface"):
                self.shoot(player.rect.center, player.play_surface, projectile_group)
            self.shoot_timer = self.shoot_cooldown
