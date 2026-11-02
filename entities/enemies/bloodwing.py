import math
import pygame
import random
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy
from entities.projectiles.enemy_projectile import circle_projectile


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

        self.name = "bloodwing"

        self.fire_rate = 0.8  # tirs par seconde
        self.shoot_cooldown = 1.0 / self.fire_rate
        self.shoot_timer = 0

        self.radius = 200

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        super().update(dt, player, play_area, projectile_group)

        if player is None or player.dead or self.is_dead:
            return

        self.angle_offset += dt * 3.0
        direction = self.get_direction_to(player.rect.center)

        # Mouvement ondulant sinusoïdal
        tangent = pygame.Vector2(-direction.y, direction.x) * math.sin(self.angle_offset) * 0.7
        combined_dir = (direction + tangent).normalize()

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            if projectile_group is not None:
                self.shoot(player.play_surface, projectile_group)
                self.shoot_timer = self.shoot_cooldown

        self.update_position(combined_dir * self.speed * dt, play_area)

    def createCircle(self, r:float, center:tuple)->list:
        """Renvoie des coordonnées de points compris dans le permietre d'un cercle, on s'en servira pour l'attaque du cercle troué"""
        coordinates = []
        theta = 0
        cx = center[0]
        cy = center[1]
        x = 0
        y = 0
        for i in range(16):
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            coordinates.append((x,y))
            theta += (math.pi / 8)
        random.shuffle(coordinates)
        coordinates.pop() #J'enlève un des projectiles pour creer une ouverture dans l'onde
        return coordinates

    
    def shoot(self, screen, projectile_group : pygame.sprite.Group):
        """Tire l'attaque de l'nnemi"""
        coordinates = self.createCircle(self.radius, (self.pos[0] + self.radius + 1, self.pos[1]))
        print("ok")
        for i in range(len(coordinates)) :
            proj = pygame.Vector2(coordinates[i])
            next = pygame.Vector2(coordinates[(i+1)%len(coordinates)])
            direction = (next - proj).normalize()
            projectile = circle_projectile.CircleProjectile(screen, proj, direction, coordinates, self.name)
            if projectile_group is not None :
                projectile_group.add(projectile)
        return coordinates

        