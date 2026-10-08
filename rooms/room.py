import random
import pygame
from core.asset_manager import AssetManager
from core.constants import COLOR_GRID, COLOR_HITBOX_DEBUG
from entities.enemies import create_enemy
from entities.obstacles import create_obstacle
from entities.interactables.door import Door


class Room:
    """Représente une salle de donjon avec son décor, ses obstacles et ses ennemis."""

    def __init__(self, room_data: dict, play_surface: pygame.Surface, play_area: pygame.Rect, reward_manager, player_upgrades: dict):
        self.room_id = room_data.get("id", 0)
        self.play_surface = play_surface
        self.play_area = play_area
        self.reward_manager = reward_manager

        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        # Fond de salle
        self.background = AssetManager.get_image(
            "assets/rooms/default.png",
            scale=(self.play_surface.get_width(), self.play_surface.get_height())
        )

        # Portes des améliorations
        self.doors: list[Door] =  self._create_doors(player_upgrades)
        self.selected_door: Door | None = None

        # Grille dynamique calculée selon le layout JSON
        layout = room_data.get("layout", [])
        self.rows = max(len(layout), 1)
        self.columns = max(len(layout[0]), 1) if layout else 1

        self.tile_size = min(self.play_area.width / self.columns, self.play_area.height / self.rows)
        self.grid_width = self.columns * self.tile_size
        self.grid_height = self.rows * self.tile_size
        self.grid_x = self.play_area.x + (self.play_area.width - self.grid_width) / 2
        self.grid_y = self.play_area.y + (self.play_area.height - self.grid_height) / 2

        # Construction du décor et des ennemis
        self._spawn_obstacles(layout)
        self._spawn_enemies(room_data.get("enemies", []), layout)

    def grid_to_world(self, col: int, row: int) -> tuple[float, float]:
        """Convertit des coordonnées de grille en coordonnées pixels sur l'aire de jeu."""
        center_x = self.grid_x + (col + 0.5) * self.tile_size
        center_y = self.grid_y + (row + 0.5) * self.tile_size
        return center_x, center_y

    def _create_doors(self, player_upgrades: dict) -> list[Door]:
        """Crée et positionne les trois portes."""
        height = max(1, self.play_area.top)
        width = round(height * 1)
        rdn_upgrades = self.reward_manager.get_random_rewards(player_upgrades)

        return [
            Door(
                size=(width, height),
                centerx=self.background.get_width() * x_rel,
                bottom=self.play_area.top,
                reward=rdn_upgrades[i]
            )
            for i,x_rel in enumerate([0.23, 0.5, 0.77])
        ]

    def _spawn_obstacles(self, layout: list[str]):
        """Génère tous les obstacles en fonction des symboles du layout (P, W, C, S)."""
        for r, row in enumerate(layout):
            for c, tile in enumerate(row):
                if tile != ".":
                    obstacle = create_obstacle(tile, c, r, self.play_surface)
                    if obstacle is not None:
                        center_pos = self.grid_to_world(c, r)
                        obstacle.set_position(center_pos)
                        self.obstacles.add(obstacle)

    def _spawn_enemies(self, enemy_configs: list[dict], layout: list[str]):
        """Place les ennemis sur des cases libres de la grille."""
        # Liste des cases libres (sans obstacles)
        free_tiles = []
        for r in range(self.rows):
            for c in range(self.columns):
                # Évite les cases trop proches du centre (zone d'apparition du joueur), faudra surement adapter
                is_near_center = (abs(c - self.columns // 2) <= 1 and abs(r - self.rows // 2) <= 1)
                tile_char = layout[r][c] if r < len(layout) and c < len(layout[r]) else "."
                if tile_char == "." and not is_near_center:
                    free_tiles.append((c, r))

        random.shuffle(free_tiles)

        for enemy_cfg in enemy_configs:
            cls_name = enemy_cfg.get("class", "CinderImp")
            count = enemy_cfg.get("count", 1)

            for _ in range(count):
                if free_tiles:
                    col, row = free_tiles.pop()
                    pos = self.grid_to_world(col, row)
                else:
                    # Coordonnées de secours si aucune case libre n'est disponible
                    pos = (self.grid_x + random.randint(50, int(self.grid_width - 50)),
                           self.grid_y + random.randint(50, int(self.grid_height - 50)))

                enemy = create_enemy(cls_name, pos=pos)
                if enemy is not None:
                    self.enemies.add(enemy)

    def is_cleared(self) -> bool:
        """Indique si tous les ennemis de la salle ont été éliminés."""
        return len(self.enemies) == 0

    def choose_door(self, player) -> None:
        if self.is_cleared() and self.selected_door is None:
            for door in self.doors:
                if door.can_enter(player.hitbox):
                    self.selected_door = door
                    break

    def update(self, dt: float, player, global_projectiles: pygame.sprite.Group):
        """Met à jour l'ensemble des ennemis et projectiles ennemis."""
        for enemy in self.enemies:
            enemy.update(dt, player=player, play_area=self.play_area, projectile_group=self.enemy_projectiles)

        for door in self.doors:
            door.update(dt, player.hitbox, self.is_cleared())
        self.choose_door(player)

        self.enemy_projectiles.update(dt)

    def draw_grid_debug(self, surface: pygame.Surface):
        """Dessine la grille d'alignement pour le débug."""
        for col in range(self.columns + 1):
            x = self.grid_x + col * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (x, self.grid_y), (x, self.grid_y + self.grid_height), 1)

        for row in range(self.rows + 1):
            y = self.grid_y + row * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (self.grid_x, y), (self.grid_x + self.grid_width, y), 1)

    def _draw_doors(self, surface: pygame.Surface, debug: bool) -> None:
        """Dessine les portes"""
        for door in self.doors:
            door.draw(surface, debug=debug)

    def draw(self, surface: pygame.Surface, debug: bool = False):
        """Affiche le décor, les obstacles, les ennemis et les éléments de débug si activés."""
        surface.blit(self.background, (0, 0))
        self._draw_doors(surface, debug)

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
