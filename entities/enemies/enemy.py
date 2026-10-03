import pygame
from core.asset_manager import AssetManager


class Enemy(pygame.sprite.Sprite):
    """Classe de base pour tous les ennemis avec gestion des PV, feedback de dégâts et IA modulaire."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        image: pygame.Surface,
        speed: float = 100.0,
        damage: int = 1,
        max_hp: int = 5,
        contact_damage: int = 1,
        hitbox_scale: float = 0.6
    ):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.damage = damage
        self.contact_damage = contact_damage
        self.max_hp = max_hp
        self.hp = max_hp

        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

        self.hitbox = self.rect.copy()
        self.hitbox.scale_by_ip(hitbox_scale)

        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.12

        self.is_dead = False

    def take_damage(self, amount: int):
        """Reçoit des dégâts avec déclenchement d'un flash visuel."""
        self.hp -= amount
        self.hit_flash_timer = self.hit_flash_duration

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.kill()

    def get_direction_to(self, target_pos: tuple[float, float] | pygame.Vector2) -> pygame.Vector2:
        """Calcule le vecteur directionnel unitaire vers une position cible."""
        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length_squared() > 0:
            return direction.normalize()
        return pygame.Vector2(0, 0)

    def distance_to(self, target_pos: tuple[float, float] | pygame.Vector2) -> float:
        """Calcule la distance avec une position cible."""
        return self.pos.distance_to(pygame.Vector2(target_pos))

    def update_position(self, delta: pygame.Vector2, play_area: pygame.Rect | None = None):
        """Déplace l'ennemi en restant dans l'aire de jeu."""
        new_pos = self.pos + delta
        new_rect = self.rect.copy()
        new_rect.center = (round(new_pos.x), round(new_pos.y))

        if play_area is None or play_area.contains(new_rect):
            self.pos = new_pos
            self.rect.center = (round(self.pos.x), round(self.pos.y))
            self.hitbox.center = self.rect.center

    def update_visuals(self, dt: float):
        """Gère le clignotement / flash lors des dégâts."""
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            # Effet de silhouette blanche / rouge lors de l'impact
            flash_surface = self.original_image.copy()
            flash_surface.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGB_ADD)
            self.image = flash_surface
        else:
            self.image = self.original_image

    def draw_health_bar(self, surface: pygame.Surface):
        """Affiche une petite jauge de vie au-dessus de l'ennemi s'il est blessé."""
        if self.hp < self.max_hp and not self.is_dead:
            bar_w = 40
            bar_h = 5
            x = self.rect.centerx - bar_w // 2
            y = self.rect.top - 8

            bg_rect = pygame.Rect(x, y, bar_w, bar_h)
            ratio = max(0, self.hp / self.max_hp)
            fg_rect = pygame.Rect(x, y, int(bar_w * ratio), bar_h)

            pygame.draw.rect(surface, (40, 40, 40), bg_rect)
            pygame.draw.rect(surface, (230, 40, 40), fg_rect)
            pygame.draw.rect(surface, (20, 20, 20), bg_rect, 1)

    def draw(self, surface: pygame.Surface):
        """Dessine l'ennemi et sa barre de vie."""
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

    def update(self, dt: float, player=None, play_area: pygame.Rect | None = None, projectile_group: pygame.sprite.Group | None = None):
        """Méthode de mise à jour générale à surcharger par les ennemis concrets."""
        self.update_visuals(dt)
