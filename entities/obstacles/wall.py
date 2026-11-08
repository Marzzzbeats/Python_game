import pygame
from core.asset_manager import AssetManager
from entities.obstacles.obstacle import Obstacle


class Wall(Obstacle):
    """Mur ou bloc de fortification."""

    def __init__(self, grid_x: int, grid_y: int, play_surface: pygame.Surface):
        image = AssetManager.get_random_obstacle_image("walls", "wall_")
        super().__init__(grid_x, grid_y, image, play_surface)
        self.scale_hitbox(0.85)
