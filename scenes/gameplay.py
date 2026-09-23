import pygame
import random

from scenes.scene import Scene
from entities.player import Player
from rooms.room import Room

class Gameplay(Scene):
    def __init__(self, game):
        super().__init__(game)


        GAME_WIDTH = game.screen.get_width() * 0.975
        GAME_HEIGHT =  game.screen.get_height() * 0.85
        self.play_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.offset_x = self.game.screen.get_width() * 0.0125
        self.offset_y = self.game.screen.get_height() * 0.025
        
        PLAY_AREA_X, PLAY_AREA_Y = 0.0449688, 0.1834696
        PLAY_AREA_W, PLAY_AREA_H = 0.9105076, 0.6993642

        self.play_area = pygame.Rect(
            self.play_surface.get_width() * PLAY_AREA_X,
            self.play_surface.get_height() * PLAY_AREA_Y,
            self.play_surface.get_width() * PLAY_AREA_W,
            self.play_surface.get_height() * PLAY_AREA_H
        )
        
        self.all_projectiles = pygame.sprite.Group()

        self.health_bar_frame_height = 150
        self.health_bar_frame = pygame.image.load("assets/player/health_bar.png").convert_alpha()
        self.health_bar_frame = pygame.transform.scale(self.health_bar_frame, (self.health_bar_frame_height*3, self.health_bar_frame_height))
        self.health_font = pygame.font.Font(None, 28)

        self.attack_image = pygame.image.load("assets/misc/attack.png").convert_alpha()
        self.attack_image = pygame.transform.scale(self.attack_image, (200, 200))
        self.alpha_layer_attack = pygame.Surface(self.attack_image.get_size(), pygame.SRCALPHA)

        self.game_over_alpha = 0
        self.game_over_speed = 100
        self.game_over_image = pygame.image.load("assets/scenes/game_over.png").convert_alpha()
        self.game_over_image = pygame.transform.scale(self.game_over_image,self.game.screen.get_size())

        self.death_timer = 0
        self.death_fade_delay = 0.8

        self.tier = 0
        self.room_id = random.randint(0,0)
        self.room = Room(self, self.tier, self.room_id)

        self.player = Player(self)

    def draw_attack_cooldown(self, screen):
        attack_image_width = self.attack_image.get_width()
        attack_image_height = self.attack_image.get_height()
        x = (screen.get_width() - attack_image_width) // 2
        y = screen.get_height() - attack_image_height - 30
        screen.blit(self.attack_image, (x, y))
        self.alpha_layer_attack.fill((0, 0, 0, 0))
        square_x = 45
        square_y = 38
        square_size = attack_image_width - 90
        ratio = self.player.shoot_timer / self.player.shoot_cooldown
        current_height = int(square_size * ratio)
        current_y = square_y + square_size - current_height
        attack_cool_rect = pygame.Rect(square_x,current_y,square_size,current_height)
        pygame.draw.rect(self.alpha_layer_attack,(200, 200, 200, 120),attack_cool_rect)
        screen.blit(self.alpha_layer_attack, (x, y))


    def draw_health_bar(self, screen):
        offset = 50
        x = 0 + offset
        y = screen.get_height() - self.health_bar_frame_height - offset
        frame_rect = self.health_bar_frame.get_rect(topleft=(x, y))
        bar_x = frame_rect.x + 90
        bar_y = frame_rect.y + 50
        max_width = 320
        bar_height = 40
        health_ratio = self.player.hp / self.player.max_hp
        current_width = max_width * health_ratio
        health_rect = pygame.Rect(bar_x,bar_y,current_width,bar_height)

        full_bar_rect = pygame.Rect(bar_x, bar_y, max_width, bar_height)
        text = self.health_font.render(f"{self.player.hp}/{self.player.max_hp}", True, "white")
        text_rect = text.get_rect(center=full_bar_rect.center)
        self.health_font = pygame.font.Font(None, 28)

        pygame.draw.rect(screen, "red", health_rect)
        screen.blit(text, text_rect)
        screen.blit(self.health_bar_frame, frame_rect)


    def update_death_transition(self, dt):
        self.game_over_alpha += (300 + self.game_over_alpha * 0.08) * dt
        if self.game_over_alpha >= 255:
            self.game_over_alpha = 255


    def handle_events(self, event):
        super().handle_events(event)


    def update(self, dt):
            if self.player.dead:
                self.death_timer += dt
                self.player.update(dt)
                if self.death_timer >= self.death_fade_delay:
                    self.update_death_transition(dt)
                return
                
            self.player.update(dt)
            self.all_projectiles.update(dt)
            self.room.update(dt)

    
    def draw(self):
        self.game.screen.fill(pygame.Color("#0f0e1f"))
        # self.play_surface.fill("black")

        self.room.draw()
        self.player.draw()
        self.all_projectiles.draw(self.play_surface)

        pygame.draw.rect(self.play_surface, "pink", self.play_area, 2)
        self.game.screen.blit(self.play_surface, (self.offset_x, self.offset_y))
        self.draw_health_bar(self.game.screen)
        self.draw_attack_cooldown(self.game.screen)

        if self.player.dead:
            self.game_over_image.set_alpha(int(self.game_over_alpha))
            self.game.screen.blit(self.game_over_image, (0, 0))