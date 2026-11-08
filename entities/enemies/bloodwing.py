import math
import pygame
import random
from core.asset_manager import AssetManager
from entities.enemies.enemy import Enemy
from entities.projectiles.enemy_projectile import circle


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

        self.fire_rate = 0.5  # tirs par seconde
        self.shoot_cooldown = 1.0 / self.fire_rate
        self.shoot_timer = 0

        self.circles = []

        self.speed = 50.0

        self.radius = 200

    def update(self, dt: float, obstacles=None, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
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

        self.update_position(combined_dir * self.speed * dt, obstacles, play_area)

        indices_a_retirer = []

        for i in range(len(self.circles)):

            if self.circles[i].circle_coordinates == []:
                indices_a_retirer.append(i)
            else:
                self.circles[i].update(dt)

        for ind in indices_a_retirer :
            self.circles.pop(ind)


    def createCircle(self, r:float, center:tuple)->list:
        """Renvoie des coordonnées de points compris dans le permietre d'un cercle, on s'en servira pour l'attaque cercle"""
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
        return coordinates

    
    def shoot(self, screen, projectile_group):
        """Tire l'attaque de l'nnemi"""
        coordinates = self.createCircle(self.radius, self.pos)
        circle_proj = circle.Circle(screen, self.pos, pygame.Vector2(0,1), coordinates, projectile_group)
        self.circles.append(circle_proj)
        print("ok")
        

        