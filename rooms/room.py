import random
import pygame
<<<<<<< HEAD
import json
import random as rd
from entities.enemies import ENEMIES_CLASS
from entities.obstacles import OBSTACLES_CLASS


def collide_hitbox(a, b):
        if not a.hitbox.colliderect(b.hitbox):
            return False

        if hasattr(a, "mask") and hasattr(b, "mask"):
            offset = (b.rect.x - a.rect.x,b.rect.y - a.rect.y)
            return a.mask.overlap(b.mask, offset) is not None

        if hasattr(a, "mask"):
            rect_mask = pygame.Mask(b.hitbox.size, fill=True)
            offset = (b.hitbox.x - a.rect.x, b.hitbox.y - a.rect.y)
            return a.mask.overlap(rect_mask, offset) is not None

        if hasattr(b, "mask"):
            rect_mask = pygame.Mask(a.hitbox.size, fill=True)
            offset = (a.hitbox.x - b.rect.x,a.hitbox.y - b.rect.y)
            return b.mask.overlap(rect_mask, offset) is not None

        return True

=======
from core.asset_manager import AssetManager
from core.constants import COLOR_GRID, COLOR_HITBOX_DEBUG
from entities.enemies import create_enemy
from entities.obstacles import create_obstacle
>>>>>>> origin/dev_killian


class Room:
    """Représente une salle de donjon avec son décor, ses obstacles et ses ennemis."""

    def __init__(self, room_data: dict, play_surface: pygame.Surface, play_area: pygame.Rect):
        self.room_id = room_data.get("id", 0)
        self.play_surface = play_surface
        self.play_area = play_area

        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        # Fond de salle
        self.background = AssetManager.get_image(
            "assets/rooms/default.png",
            scale=(self.play_surface.get_width(), self.play_surface.get_height())
        )

        # Grille dynamique calculée selon le layout JSON
        layout = room_data.get("layout", [])
        self.rows = max(len(layout), 1)
        self.columns = max(len(layout[0]), 1) if layout else 1

        self.tile_size = min(self.play_area.width / self.columns, self.play_area.height / self.rows)
        self.grid_width = self.columns * self.tile_size
        self.grid_height = self.rows * self.tile_size
<<<<<<< HEAD
        self.grid_x = (self.gameplay.play_area.x + (self.gameplay.play_area.width - self.grid_width) / 2)
        self.grid_y = (self.gameplay.play_area.y + (self.gameplay.play_area.height - self.grid_height) / 2)
        
        self.current_enemy_count = 0
        self.current_enemies = []
        self.total_enemies_count = 0
        self.total_enemies = []
        self.max_enemies = 0
        self.id_enemies = 0
=======
        self.grid_x = self.play_area.x + (self.play_area.width - self.grid_width) / 2
        self.grid_y = self.play_area.y + (self.play_area.height - self.grid_height) / 2
>>>>>>> origin/dev_killian

        # Construction du décor et des ennemis
        self._spawn_obstacles(layout)
        self._spawn_enemies(room_data.get("enemies", []), layout)

    def grid_to_world(self, col: int, row: int) -> tuple[float, float]:
        """Convertit des coordonnées de grille en coordonnées pixels sur l'aire de jeu."""
        center_x = self.grid_x + (col + 0.5) * self.tile_size
        center_y = self.grid_y + (row + 0.5) * self.tile_size
        return center_x, center_y

<<<<<<< HEAD
        self.init_spawn_enemies()
        self.spawn_obstacles()
        self.place_all_obstacles()
=======
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
>>>>>>> origin/dev_killian

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

    def update(self, dt: float, player, global_projectiles: pygame.sprite.Group):
        """Met à jour l'ensemble des ennemis et projectiles ennemis."""
        for enemy in self.enemies:
            enemy.update(dt, player=player, play_area=self.play_area, projectile_group=global_projectiles)

        self.enemy_projectiles.update(dt)

<<<<<<< HEAD
    def place_relative_play_area(self, x, y):
        rel_x = self.gameplay.play_area.x + x
        rel_y = self.gameplay.play_area.y + y
        return rel_x, rel_y


    def place_from_layout(self, tile_x, tile_y):
        x = (min(tile_x, self.gameplay.play_area.width) + 1/2) * self.tile_size
        y = (min(tile_y, self.gameplay.play_area.height) + 1/2) *  self.tile_size 
        return self.place_relative_play_area(x,y)


    def check_player_projectiles_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.gameplay.player.player_projectiles,
            self.all_enemies,
            True,
            False,
            collide_hitbox
        )

        for projectile, enemies_hit in collisions.items():
            for enemy in enemies_hit:
                indice = enemy.take_damage(projectile.damage)
                if indice != -1 and self.current_enemy_count >0:
                    print("mort")
                    self.current_enemy_count -=1
                    for i in range(len(self.current_enemies)) :
                        print(i)
                        if self.current_enemies[i]["id"] == indice:
                            self.current_enemies.pop(i)


    def check_enemy_projectiles_collisions(self):
        collisions = pygame.sprite.spritecollide(
            self.gameplay.player,
            self.all_enemies_projectile,
            True,
            collide_hitbox
        )

        for projectile in collisions:
            self.gameplay.player.take_damage(projectile.damage)


    def check_projectiles_collisions_obstacle(self):
        pygame.sprite.groupcollide(
            self.gameplay.all_projectiles,
            self.all_obstacles,
            True,
            False,
            collide_hitbox
        )


    def init_spawn_enemies(self):
        self.total_enemies = self.load_from_room("enemies")
        print(self.total_enemies)
        self.max_enemies = self.load_from_room("max_enemies")


    def spawn_obstacles(self):
        layout = self.load_from_room("layout")

        for i,row in enumerate(layout):
            for j,tile in enumerate(row):
                match tile:
                    case "P":
                        pillar = OBSTACLES_CLASS["Pillar"](j, i, self.gameplay.play_surface)
                        self.all_obstacles.add(pillar)



    def draw_grid(self, surface):
=======
    def draw_grid_debug(self, surface: pygame.Surface):
        """Dessine la grille d'alignement pour le débug."""
>>>>>>> origin/dev_killian
        for col in range(self.columns + 1):
            x = self.grid_x + col * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (x, self.grid_y), (x, self.grid_y + self.grid_height), 1)

        for row in range(self.rows + 1):
            y = self.grid_y + row * self.tile_size
            pygame.draw.line(surface, COLOR_GRID, (self.grid_x, y), (self.grid_x + self.grid_width, y), 1)

<<<<<<< HEAD
        
    def update(self, dt):
        self.spawn_enemies()
        self.check_player_projectiles_collisions()
        self.check_enemy_projectiles_collisions()
        self.check_projectiles_collisions_obstacle()
        if not self.gameplay.player.dead:
            self.all_enemies.update(dt)

    def check_enemies_count(self)->bool:
        """Vérifie si le seuil d'ennemis de la salle a été atteint """
        return self.current_enemy_count >= self.max_enemies


    def spawn_enemies(self):
        if not self.check_enemies_count() and self.total_enemies != []:
            rd.shuffle(self.total_enemies)
            enemy_type = self.total_enemies[0]
            pos = self.place_relative_play_area(rd.randint(130,2000), rd.randint(100, 300))
            enemy = ENEMIES_CLASS[enemy_type["class"]](self.gameplay, self.all_enemies_projectile, pos, 10, 1, 5, self.id_enemies)
            self.all_enemies.add(enemy)
            if enemy_type["count"] == 1 :
                self.total_enemies.pop(0)
            else:
                enemy_type["count"] -= 1
            self.current_enemies.append({"id": self.id_enemies, "classe": enemy_type["class"]})
            self.current_enemy_count +=1
            self.id_enemies +=1


=======
    def draw(self, surface: pygame.Surface, debug: bool = False):
        """Affiche le décor, les obstacles, les ennemis et les éléments de débug si activés."""
        surface.blit(self.background, (0, 0))

        # Obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)
            if debug:
                pygame.draw.rect(surface, COLOR_HITBOX_DEBUG, obstacle.hitbox, 1)
>>>>>>> origin/dev_killian

        # Ennemis
        for enemy in self.enemies:
            enemy.draw(surface)
            if debug:
                pygame.draw.rect(surface, COLOR_HITBOX_DEBUG, enemy.hitbox, 1)

        # Grille de débug
        if debug:
            self.draw_grid_debug(surface)
