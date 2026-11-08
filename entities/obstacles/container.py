import pygame
from core.asset_manager import AssetManager
from entities.obstacles.obstacle import Obstacle


class Container(Obstacle):
    """Caisse ou baril d'objets."""

    def __init__(self, grid_x: int, grid_y: int, play_surface: pygame.Surface):
        image = AssetManager.get_random_obstacle_image("containers", "container_")
        super().__init__(grid_x, grid_y, image, play_surface)
        self.scale_hitbox(0.75)
