import pygame


class Projectile(pygame.sprite.Sprite):
    """Classe de base complète et extensible pour tous les projectiles (joueur et ennemis)."""

    def __init__(
        self,
        play_surface: pygame.Surface,
        pos: tuple[float, float] | pygame.Vector2,
        direction: tuple[float, float] | pygame.Vector2,
        speed: float,
        damage: int,
        image: pygame.Surface,
        lifetime: float = 5.0,
        hitbox_scale: float = 1.0
    ):
        super().__init__()

        self.screen = play_surface
        self.pos = pygame.Vector2(pos)

        dir_vec = pygame.Vector2(direction)
        if dir_vec.length_squared() > 0:
            self.direction = dir_vec.normalize()
        else:
            self.direction = pygame.Vector2(1, 0)

        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self.elapsed_time = 0.0

        self.image = image
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self.hitbox = self.rect.copy()

        self.scale_hitbox(hitbox_scale)
        self.mask = pygame.mask.from_surface(self.image)

    def scale_hitbox(self, scale_ratio: float = 1.0):
        """Redimensionne la hitbox relative à l'image."""
        if scale_ratio != 1.0:
            self.hitbox.scale_by_ip(scale_ratio)
            self.hitbox.center = self.rect.center

    def move(self, dt: float):
        """Met à jour la position et synchronise rect et hitbox."""
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

    def update(self, dt: float):
        """Mise à jour à chaque frame."""
        self.elapsed_time += dt
        if self.elapsed_time >= self.lifetime:
            self.kill()
            return

        self.move(dt)

        # Si le projectile quitte la zone de jeu
        if not self.rect.colliderect(self.screen.get_rect()):
            self.kill()
