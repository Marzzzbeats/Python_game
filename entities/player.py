import os
import pygame

from entities.projectiles.player_projectiles.base import StraightProjectile


class Player(pygame.sprite.Sprite):
    def __init__(self, screen, all_projectiles):
        super().__init__()

        self.screen = screen
        self.all_projectiles = all_projectiles
        self.player_projectiles = pygame.sprite.Group()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.joystick = None

        self.base_speed = 600
        self.speed = self.base_speed
        self.damage = 1
        self.max_hp = 10
        self.hp = self.max_hp
        self.fire_rate = 10  # /seconds

        self.sprites = self.load_sprites()
        self.state = "idle"
        self.sprite_direction = "right"
        self.frame = 0

        self.previous_state = self.state
        self.previous_direction = self.sprite_direction

        self.animation_timer = 0
        self.animation_speed = {
            "walk": 0.12,
            "cast": 0.06,
            "death": 0.15
        }

        self.look_direction = pygame.Vector2(1, 0)

        self.shoot_cooldown = 1/self.fire_rate
        self.shoot_timer = 0

        self.image = self.sprites[self.state][self.sprite_direction][self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self.screen.get_rect().center

        self.hitbox = self.rect.copy()
        self.hitbox.scale_by_ip(0.5)



    def normalize_sprite(self, image, target_height=90, canvas_size=256):
        bbox = image.get_bounding_rect()
        visible = image.subsurface(bbox).copy()

        ratio = target_height / visible.get_height()
        new_width = round(visible.get_width() * ratio)
        new_height = target_height

        visible = pygame.transform.scale(visible,(new_width, new_height))

        canvas = pygame.Surface((canvas_size, canvas_size),pygame.SRCALPHA)

        x = (canvas_size - new_width) // 2

        FOOT_Y = 190
        y = FOOT_Y - new_height

        canvas.blit(visible, (x, y))

        return canvas


    def load_sprites(self):
        player_sprites = {}

        states = [
            "idle",
            "walk",
            "cast",
            "death"
        ]

        directions = [
            "up",
            "up_right",
            "right",
            "down_right",
            "down",
            "down_left",
            "left",
            "up_left"
        ]

        target_heights = {
            "idle": 120,
            "walk": 90,
            "cast": 90,
            "death": 90
        }

        for state in states:
            player_sprites[state] = {}

            for direction in directions:
                player_sprites[state][direction] = []

                path = f"assets/player/{state}/{direction}"

                if not os.path.exists(path):
                    continue

                for filename in sorted(os.listdir(path)):
                    if filename.endswith(".png"):
                        image = pygame.image.load(f"{path}/{filename}").convert_alpha()
                        image = self.normalize_sprite(image, target_height=target_heights[state])
                        player_sprites[state][direction].append(image)

        return player_sprites



    def animate(self, dt):
        if (self.state != self.previous_state or self.sprite_direction != self.previous_direction):
            self.frame = 0
            self.animation_timer = 0

            self.previous_state = self.state
            self.previous_direction = self.sprite_direction

        frames = self.sprites[self.state][self.sprite_direction]

        if len(frames) <= 1:
            self.frame = 0
        else:
            self.animation_timer += dt

            if self.animation_timer >= self.animation_speed[self.state]:
                self.animation_timer = 0

                if self.state == "death":
                    self.frame = min(self.frame + 1, len(frames) - 1)

                else:
                    self.frame = (self.frame + 1) % len(frames)

        center = self.rect.center

        self.image = frames[self.frame]
        self.rect = self.image.get_rect(center=center)



    def in_screen(self, x, y):
        future_rect = self.rect.move(x, y)
        return self.screen.get_rect().contains(future_rect)


    def move(self, x, y):
        if self.in_screen(x, y):
            self.rect.move_ip(x, y)


    def shoot(self):
        self.state = "cast"

        projectile = StraightProjectile(
            screen=self.screen,
            pos=self.rect.center,
            direction=self.look_direction,
            speed=20,
            damage=1
        )

        self.all_projectiles.add(projectile)
        self.player_projectiles.add(projectile)


    def get_move_direction(self, keys):
        keyboard_dir = pygame.Vector2(0, 0)

        if keys[pygame.K_q]:
            keyboard_dir.x -= 1

        if keys[pygame.K_d]:
            keyboard_dir.x += 1

        if keys[pygame.K_z]:
            keyboard_dir.y -= 1

        if keys[pygame.K_s]:
            keyboard_dir.y += 1
        
        try:
            joystick_dir = pygame.Vector2(self.joystick.get_axis(0),self.joystick.get_axis(1))
        except AttributeError:
            joystick_dir = pygame.Vector2(0, 0)

        if abs(joystick_dir.x) < 0.30:
            joystick_dir.x = 0

        if abs(joystick_dir.y) < 0.30:
            joystick_dir.y = 0

        move_dir = keyboard_dir + joystick_dir

        if move_dir.length() > 0:
            move_dir = move_dir.normalize()

        return move_dir


    def update_direction(self, move_dir):
        self.look_direction = move_dir

        if move_dir.x > 0.3 and move_dir.y < -0.3:
            self.sprite_direction = "up_right"
        elif move_dir.x < -0.3 and move_dir.y < -0.3:
            self.sprite_direction = "up_left"
        elif move_dir.x > 0.3 and move_dir.y > 0.3:
            self.sprite_direction = "down_right"
        elif move_dir.x < -0.3 and move_dir.y > 0.3:
            self.sprite_direction = "down_left"
        elif abs(move_dir.x) > abs(move_dir.y):
            if move_dir.x > 0:
                self.sprite_direction = "right"
            else:
                self.sprite_direction = "left"
        else:
            if move_dir.y > 0:
                self.sprite_direction = "down"
            else:
                self.sprite_direction = "up"



    def handle_inputs(self, keys, dt):
        shoot_pressed = (keys[pygame.K_l] or self.joystick.get_button(0))
        move_dir = self.get_move_direction(keys)

        if shoot_pressed:
            self.speed = self.base_speed*0.8
        else:
            self.speed = self.base_speed

        if move_dir.length() > 0:
            self.move(move_dir.x * self.speed * dt, move_dir.y * self.speed * dt)
            self.hitbox.center = self.rect.center

            if not shoot_pressed:
                self.update_direction(move_dir)
                self.state = "walk"

        else:
            if not shoot_pressed:
                self.state = "idle"

        if shoot_pressed and self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_cooldown



    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.shoot_timer -= dt

        self.handle_inputs(keys, dt)
        self.animate(dt)


    def draw(self):
        pygame.draw.rect(self.screen,"green",self.rect,2)
        pygame.draw.rect(self.screen,"red",self.hitbox,2)
        for proj in self.player_projectiles:
            pygame.draw.rect(self.screen, "blue", proj.rect,2)
            pygame.draw.rect(self.screen,"red", proj.hitbox,2)
        self.screen.blit(self.image, self.rect)