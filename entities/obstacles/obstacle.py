import pygame


class Obstacle(pygame.sprite.Sprite):
    """Classe de base pour tous les obstacles destructibles ou indestructibles du décor."""

    def __init__(self, grid_x: int, grid_y: int, image: pygame.Surface, play_surface: pygame.Surface):
        super().__init__()

        self.grid_x = grid_x
        self.grid_y = grid_y
        self.play_surface = play_surface

        self.image = image
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_bounding_rect()
        

    def scale_hitbox(self, size: tuple[int, int]):
        """Redimensionne la boîte de collision relative au centre du sprite."""
        self.hitbox.scale_by(size)
        self.hitbox.center = self.rect.center

    def set_position(self, center_pos: tuple[int, int]):
        """Positionne l'obstacle sur la surface de jeu."""
        self.rect.center = center_pos
        self.hitbox.center = center_pos

    def draw(self, surface: pygame.Surface | None = None):
        """Dessine l'obstacle sur la surface ciblée."""
        target = surface if surface is not None else self.play_surface
        target.blit(self.image, self.rect)
