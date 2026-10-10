import pygame
from core.asset_manager import AssetManager
from core.constants import WALL_TEXTURES
from entities.obstacles.obstacle import Obstacle


class Wall(Obstacle):
    """Mur dont la texture dépend des murs voisins."""

    def __init__(
        self,
        grid_x: int,
        grid_y: int,
        play_surface: pygame.Surface,
        layout: list[str],
        tile_size: float,
    ):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.layout = layout
        self.tile_size = tile_size

        self.connections = self.get_connection()
        self.is_fill = layout[grid_y][grid_x] == "F"

        if self.is_fill:
            filename = WALL_TEXTURES["fill"]
        else:
            filename = WALL_TEXTURES[self.connections]

        image = AssetManager.get_image(
            f"assets/rooms/obstacles/walls/{filename}",
            scale=self.get_wall_texture_size(),
        )
        super().__init__(grid_x, grid_y, image, play_surface)
        self.scale_hitbox(tile_size)

    def get_wall_texture_size(self) -> tuple[int, int]:
        size = max(1, round(self.tile_size))
        thickness = max(1, round(size * 0.4))

        if self.is_fill:
            return (size, size)

        north, east, south, west = self.connections

        if (east or west) and not (north or south):
            return (size, thickness)

        if (north or south) and not (east or west):
            return (thickness, size)

        return (size, size)


    def get_connection(self) -> tuple[bool, bool, bool, bool]:
        north = self.is_wall(self.grid_x, self.grid_y - 1)
        east = self.is_wall(self.grid_x + 1, self.grid_y)
        south = self.is_wall(self.grid_x, self.grid_y + 1)
        west = self.is_wall(self.grid_x - 1, self.grid_y)

        return (north, east, south, west)

    def is_wall(self, x: int, y: int) -> bool:
        if not 0 <= y < len(self.layout):
            return False

        if not 0 <= x < len(self.layout[y]):
            return False

        return self.layout[y][x] == "W"