import pygame


class ExplosionEffect(pygame.sprite.Sprite):
    """Affiche une explosion circulaire temporaire."""

    def __init__(
        self,
        pos: tuple[float, float] | pygame.Vector2,
        radius: int,
        color: tuple[int, int, int] = (100, 255, 60),
        duration: float = 0.25
    ):
        super().__init__()

        self.radius = max(1, radius)
        self.color = color
        self.duration = max(0.001, duration)
        self.elapsed_time = 0.0

        size = self.radius * 2 + 8
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(
            center=(round(pos[0]), round(pos[1]))
        )
        self._update_image()

    def _update_image(self) -> None:
        """Dessine l'anneau et le flash central."""
        self.image.fill((0, 0, 0, 0))

        progress = min(1.0, self.elapsed_time / self.duration)
        alpha = round(255 * (1.0 - progress))
        current_radius = max(1, round(self.radius * progress))
        center = self.image.get_rect().center

        pygame.draw.circle(
            self.image,
            (*self.color, alpha),
            center,
            current_radius,
            width=min(4, current_radius)
        )

        flash_strength = max(0.0, 1.0 - progress * 3)
        if flash_strength > 0:
            pygame.draw.circle(
                self.image,
                (220, 255, 180, round(200 * flash_strength)),
                center,
                max(1, round(self.radius * 0.15 * flash_strength))
            )

    def update(self, dt: float) -> None:
        """Fait avancer l'animation puis supprime l'effet."""
        self.elapsed_time += dt

        if self.elapsed_time >= self.duration:
            self.kill()
            return

        self._update_image()

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine l'explosion."""
        surface.blit(self.image, self.rect)