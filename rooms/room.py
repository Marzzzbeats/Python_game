import random
import pygame
from core.asset_manager import AssetManager
from core.constants import COLOR_GRID, COLOR_HITBOX_DEBUG
from entities.enemies import create_enemy
from entities.obstacles import create_obstacle


class Room:
    """Représente une salle de donjon avec son décor, ses obstacles et ses ennemis."""

    def __init__(self, room_data: dict, play_surface: pygame.Surface, play_area: pygame.Rect):
        self.room_id = room_data.get("id", 0)
        self.play_surface = play_surface
        self.play_area = play_area
        self.max_enemies = room_data["max_enemies"]

        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        # Fond de salle
        self.background = AssetManager.get_image(
            "assets/rooms/default.png",
            scale=(self.play_surface.get_width(), self.play_surface.get_height())
        )

        # Grille dynamique calculée selon le layout JSON
        self.layout = room_data.get("layout", [])
        self.rows = max(len(self.layout), 1)
        self.columns = max(len(self.layout[0]), 1) if self.layout else 1

        self.tile_size = min(self.play_area.width / self.columns, self.play_area.height / self.rows)
        self.grid_width = self.columns * self.tile_size
        self.grid_height = self.rows * self.tile_size
        self.grid_x = self.play_area.x + (self.play_area.width - self.grid_width) / 2
        self.grid_y = self.play_area.y + (self.play_area.height - self.grid_height) / 2
        self.enemies_config = room_data.get("enemies", [])

        print(room_data)

        # Construction du décor et des ennemis
        self.all_enemies = self.getEnemies()
        self._spawn_obstacles()
        self._spawn_enemies()

    def grid_to_world(self, col: int, row: int) -> tuple[float, float]:
        """Convertit des coordonnées de grille en coordonnées pixels sur l'aire de jeu."""
        center_x = self.grid_x + (col + 0.5) * self.tile_size
        center_y = self.grid_y + (row + 0.5) * self.tile_size
        return center_x, center_y

    def _spawn_obstacles(self):
        """Génère tous les obstacles en fonction des symboles du layout (P, W, C, S)."""
        for r, row in enumerate(self.layout):
            for c, tile in enumerate(row):
                if tile != ".":
                    obstacle = create_obstacle(tile, c, r, self.play_surface)
                    if obstacle is not None:
                        center_pos = self.grid_to_world(c, r)
                        obstacle.set_position(center_pos)
                        self.obstacles.add(obstacle)

    def getFreeTiles(self)->list:
        """Renvoie toutes les thuiles libres"""

        free_tiles = []

        for r in range(self.rows):
            for c in range(self.columns):
                # Évite les cases trop proches du centre (zone d'apparition du joueur), faudra surement adapter
                is_near_center = (abs(c - self.columns // 2) <= 1 and abs(r - self.rows // 2) <= 1)
                tile_char = self.layout[r][c] if r < len(self.layout) and c < len(self.layout[r]) else "."
                if tile_char == "." and not is_near_center:
                    free_tiles.append((c, r))
        
        random.shuffle(free_tiles)

        return free_tiles

    def spawnEnemy(self):
        """Fais apparaitre un ennemi"""
        if len(self.all_enemies) != 0 :
            enemy_info = self.all_enemies.pop()
            print(f"infos : {enemy_info}")
            free_tiles = self.getFreeTiles()

            if free_tiles:
                col, row = free_tiles.pop()
                pos = self.grid_to_world(col, row)
            else:
                # Coordonnées de secours si aucune case libre n'est disponible
                pos = (self.grid_x + random.randint(50, int(self.grid_width - 50)), self.grid_y + random.randint(50, int(self.grid_height - 50)))


            enemy_class = enemy_info['category']
            enemy = create_enemy(enemy_class, pos)
            if enemy is not None :
                self.enemies.add(enemy)

    def _spawn_enemies(self):
        """Place les premiers ennemis sur des cases libres de la grille."""
        # Liste des cases libres (sans obstacles

        for i in range(self.max_enemies):
            self.spawnEnemy()


    def is_cleared(self) -> bool:
        """Indique si tous les ennemis de la salle ont été éliminés."""
        return len(self.all_enemies) == 0

    def update(self, dt: float, player, global_projectiles: pygame.sprite.Group):
        """Met à jour l'ensemble des ennemis et projectiles ennemis."""
        for enemy in self.enemies:
            enemy.update(dt, self.obstacles ,player=player, play_area=self.play_area, projectile_group=self.enemy_projectiles)

        if len(self.enemies) < self.max_enemies :
            self.spawnEnemy() 

        self.enemy_projectiles.update(dt)

    def draw_grid_debug(self, surface: pygame.Surface):
        """Dessine la grille d'alignement pour le débug."""
        for col in range(self.columns + 1):
            x = self.grid_x + col * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (x, self.grid_y), (x, self.grid_y + self.grid_height), 1)

        for row in range(self.rows + 1):
            y = self.grid_y + row * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (self.grid_x, y), (self.grid_x + self.grid_width, y), 1)

    def draw(self, surface: pygame.Surface, debug: bool = False):
        """Affiche le décor, les obstacles, les ennemis et les éléments de débug si activés."""
        surface.blit(self.background, (0, 0))

        # Obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)
            if debug:
                pygame.draw.rect(surface, COLOR_HITBOX_DEBUG, obstacle.hitbox, 1)

        # Ennemis
        for enemy in self.enemies:
            enemy.draw(surface)
            if debug:
                pygame.draw.rect(surface, COLOR_HITBOX_DEBUG, enemy.hitbox, 1)

        # Grille de débug
        if debug:
            self.draw_grid_debug(surface)

    def getEnemies(self)->dict:
        all_enemies = []
        for cat in self.enemies_config :
            for i in range(0, cat['count']):
                all_enemies.append({"id": i, "category": cat['class']})
        random.shuffle(all_enemies)
        return all_enemies