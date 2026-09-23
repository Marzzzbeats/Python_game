import pygame
import json
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



class Room:
    def __init__(self, gameplay, tier, room_id):
        self.tier = tier
        self.room_id = room_id
        self.gameplay = gameplay

        self.all_enemies = pygame.sprite.Group()
        self.all_enemies_projectile = pygame.sprite.Group()

        self.all_obstacles = pygame.sprite.Group()

        self.background = pygame.image.load("assets/rooms/default.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (self.gameplay.play_surface.get_width(), self.gameplay.play_surface.get_height()))

        self.columns = 16
        self.tile_size = gameplay.play_area.width / self.columns    
        self.rows = int(gameplay.play_area.height / self.tile_size)
        # pour l'instant c du 16x6

        self.room_json = self.load_room()

        self.spawn_enemies()
        self.spawn_obstacles()
        self.place_all_obstacles()


    def load_room(self):
        with open("rooms.json", "r") as f:
            data = json.load(f)
        return data
    

    def load_from_room(self, key):
        return self.room_json["tiers"][str(self.gameplay.tier)]["rooms"][self.gameplay.room_id][key]


    def place_all_obstacles(self):
        for obstacle in self.all_obstacles:
            self.place_obstacle(obstacle)


    def place_obstacle(self, obstacle):
        new_x = obstacle.x
        new_y = obstacle.y
        if obstacle.x < 0:
            new_x = max(0, self.gameplay.play_area.width + obstacle.x)
        if obstacle.y < 0:
            new_y = max(0, self.gameplay.play_area.height + obstacle.y)
        obstacle.rect.center = (self.place_from_layout(new_x, new_y))
        obstacle.hitbox.center = obstacle.rect.center
        print(f"{type(obstacle)} at pos : x={obstacle.hitbox.center[0]}   y={obstacle.hitbox.center[1]}")


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
                enemy.take_damage(projectile.damage)


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


    def spawn_enemies(self):
        room_enemies = self.load_from_room("enemies")
        for room_enemy in room_enemies:
            for _ in range(room_enemy["count"]):
                pos = self.place_relative_play_area(50, 100)
                enemy = ENEMIES_CLASS[room_enemy["class"]](self.gameplay, self.all_enemies_projectile, pos, 10, 1, 5)
                self.all_enemies.add(enemy)


    def spawn_obstacles(self):
        layout = self.load_from_room("layout")

        for i,row in enumerate(layout):
            for j,tile in enumerate(row):
                match tile:
                    case "P":
                        pillar = OBSTACLES_CLASS["Pillar"](j, i, self.gameplay.play_surface)
                        self.all_obstacles.add(pillar)



    def draw_grid(self, surface):
        grid_width = self.gameplay.play_area.width
        grid_height = self.gameplay.play_area.height
        grid_x = self.gameplay.play_area.x
        grid_y = self.gameplay.play_area.y

        for col in range(self.columns + 1):
            x = grid_x + col * self.tile_size
            pygame.draw.line(surface,"lime",(x, grid_y),(x, grid_y + grid_height),2)

        for row in range(self.rows + 1):
            y = grid_y + row * self.tile_size
            pygame.draw.line(surface,"lime",(grid_x, y),(grid_x + grid_width, y),2)

        
    def update(self, dt):
        self.check_player_projectiles_collisions()
        self.check_enemy_projectiles_collisions()
        self.check_projectiles_collisions_obstacle()
        if not self.gameplay.player.dead:
            self.all_enemies.update(dt)



    def draw(self):
        self.gameplay.play_surface.blit(self.background, (0,0))
        self.all_enemies.draw(self.gameplay.play_surface)
        self.all_obstacles.draw(self.gameplay.play_surface)

        self.draw_grid(self.gameplay.play_surface)

        for obstacle in self.all_obstacles:
            # pygame.draw.rect(self.gameplay.play_surface,"cyan", obstacle.rect,2)
            pygame.draw.rect(self.gameplay.play_surface,"red", obstacle.hitbox,2)

        for enemy in self.all_enemies:
            # pygame.draw.rect(self.gameplay.play_surface,"yellow",enemy.rect,2)
            pygame.draw.rect(self.gameplay.play_surface,"red", enemy.hitbox,2)

            for proj in enemy.enemy_projectiles:
                # pygame.draw.rect(self.play_surface, "blue", proj.rect,2)
                pygame.draw.rect(self.gameplay.play_surface, "red", proj.hitbox,2)
