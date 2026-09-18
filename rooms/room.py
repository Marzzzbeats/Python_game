import pygame
import json


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
    def __init__(self, gameplay):
        self.gameplay = gameplay
        self.all_enemies = pygame.sprite.Group()
        self.all_enemies_projectile = pygame.sprite.Group()

        self.all_obstacles = pygame.sprite.Group()

        self.background = pygame.image.load("assets/rooms/default.png").convert_alpha()
        play_surface = self.gameplay.play_surface
        self.background = pygame.transform.scale(self.background, (play_surface.get_width(), play_surface.get_height()))

        self.room_json = self.load_room()
        self.room_enemies = self.load_from_room("enemies")
        # self.room_enemies = self.load_from_room("obstacles")
        print(self.room_enemies)


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
        obstacle.rect.center = (self.place_relative_play_area(new_x, new_y))
        obstacle.hitbox.center = obstacle.rect.center
        print(new_x, new_y)


    def place_relative_play_area(self, x, y):
        rel_x = self.gameplay.play_area.x + x
        rel_y = self.gameplay.play_area.y + y
        return rel_x, rel_y


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

        for obstacle in self.all_obstacles:
            # pygame.draw.rect(self.gameplay.play_surface,"cyan", obstacle.rect,2)
            pygame.draw.rect(self.gameplay.play_surface,"red", obstacle.hitbox,2)

        for enemy in self.all_enemies:
            # pygame.draw.rect(self.gameplay.play_surface,"yellow",enemy.rect,2)
            pygame.draw.rect(self.gameplay.play_surface,"red", enemy.hitbox,2)

            for proj in enemy.enemy_projectiles:
                # pygame.draw.rect(self.play_surface, "blue", proj.rect,2)
                pygame.draw.rect(self.gameplay.play_surface, "red", proj.hitbox,2)
