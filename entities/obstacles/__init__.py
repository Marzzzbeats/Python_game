from .obstacle import Obstacle
from .pillar import Pillar
from .wall import Wall
from .container import Container
from .stone import Stone

# Dictionnaire de classes par nom
OBSTACLES_CLASS = {
    "Pillar": Pillar,
    "Wall": Wall,
    "Container": Container,
    "Stone": Stone,
}

# Mapping direct symbole de grille -> classe d'obstacle
OBSTACLE_SYMBOL_MAP = {
    "P": Pillar,
    "W": Wall,
    "F": Wall,
    "C": Container, # Crate
    "S": Stone,
    "B": Container,  # Baril
}


def create_obstacle(symbol_or_name: str, grid_x: int, grid_y: int, play_surface, layout: list[str], tile_size: int):
    """Fabrique un obstacle à partir de son symbole de grille ou de son nom de classe."""
    cls = OBSTACLE_SYMBOL_MAP.get(symbol_or_name) or OBSTACLES_CLASS.get(symbol_or_name)
    if cls is Wall:
        return cls(grid_x, grid_y, play_surface, layout, tile_size)
    if cls is not None:
        return cls(grid_x, grid_y, play_surface)
    return None


