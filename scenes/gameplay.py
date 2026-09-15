import pygame
from scenes.scene import Scene
from entities.player import Player
from rooms import ROOMS


class Gameplay(Scene):
    def __init__(self, game):
        super().__init__(game)


        GAME_WIDTH = game.screen.get_width() * 0.975
        GAME_HEIGHT =  game.screen.get_height() * 0.75
        self.play_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        
        self.all_projectiles = pygame.sprite.Group()
        self.player = Player(self.play_surface, self.all_projectiles)

        self.health_bar_frame_height = 150
        self.health_bar_frame = pygame.image.load("assets/player/health_bar.png").convert_alpha()
        self.health_bar_frame = pygame.transform.scale(self.health_bar_frame, (self.health_bar_frame_height*3, self.health_bar_frame_height))

        self.room = ROOMS[1][0](self)


    def draw_health_bar(self, screen):
        offset = 50
        x = 10 + offset
        y = self.game.screen.get_height() - self.health_bar_frame_height - offset
        max_width = 200
        bar_height = 20
        health_ratio = self.player.hp / self.player.max_hp
        current_width = max_width * health_ratio
        screen.blit(self.health_bar_frame, (x, y))
        rect = pygame.Rect(x, y, current_width, bar_height)
        pygame.draw.rect(screen, "red", rect)
        rect.center = self.health_bar_frame.get_rect().center


    def handle_events(self, event):
        super().handle_events(event)


    def update(self, dt):
            self.player.update(dt)
            self.all_projectiles.update(dt)
            self.room.update(dt)

    
    def draw(self):
        self.game.screen.fill("black")
        self.play_surface.fill("black")

        pygame.draw.rect(
            self.play_surface,
            "white",
            self.play_surface.get_rect(),
            width=4
        )

        self.room.draw()
        self.player.draw()
        self.all_projectiles.draw(self.play_surface)

        self.game.screen.blit(self.play_surface, (self.game.screen.get_width() * 0.0125, self.game.screen.get_height() * 0.025))
    
        self.draw_health_bar(self.game.screen)
