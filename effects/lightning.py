import math
import random
import pygame


class LightningEffect(pygame.sprite.Sprite):
    """Affiche brièvement un éclair entre deux positions fixes."""

    def __init__(
        self,
        start: tuple[float, float] | pygame.Vector2,
        end: tuple[float, float] | pygame.Vector2,
        duration: float = 0.18
    ):
        super().__init__()

        start = pygame.Vector2(start)
        end = pygame.Vector2(end)
        padding = 16
        self.rect = pygame.Rect(
            math.floor(min(start.x, end.x)) - padding,
            math.floor(min(start.y, end.y)) - padding,
            math.ceil(abs(end.x - start.x)) + padding * 2 + 1,
            math.ceil(abs(end.y - start.y)) + padding * 2 + 1
        )
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.duration = max(0.001, duration)
        self.elapsed_time = 0.0

        direction = end - start
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        if perpendicular.length_squared() > 0:
            perpendicular = perpendicular.normalize()

        local_start = start - pygame.Vector2(self.rect.topleft)
        local_end = end - pygame.Vector2(self.rect.topleft)
        segments = max(2, round(direction.length() / 20))
        points = [local_start]
        for index in range(1, segments):
            point = local_start.lerp(local_end, index / segments)
            point += perpendicular * random.uniform(-10, 10)
            points.append(point)
        points.append(local_end)

        pygame.draw.lines(self.image, (100, 160, 255, 100), False, points, 9)
        pygame.draw.lines(self.image, (150, 210, 255, 220), False, points, 5)
        pygame.draw.lines(self.image, (245, 250, 255, 255), False, points, 2)

    def update(self, dt: float) -> None:
        """Fait disparaître l'éclair puis le retire du groupe d'effets."""
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.kill()
            return

        self.image.set_alpha(round(255 * (1 - self.elapsed_time / self.duration)))
