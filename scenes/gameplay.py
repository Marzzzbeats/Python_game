import pygame
from scenes.scene import Scene
from entities.player import Player
from rooms import ROOMS


class Gameplay(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.all_projectiles = pygame.sprite.Group()
        self.player = Player(self.game.screen, self.all_projectiles)

        self.room = ROOMS[1][0](self)


    def handle_events(self, event):
        super().handle_events(event)


    def update(self, dt):
            self.player.update(dt)
            self.all_projectiles.update(dt)
            self.room.update(dt)

    
    def draw(self):
        self.game.screen.fill("black")

        self.player.draw()
        self.all_projectiles.draw(self.game.screen)
        self.room.draw()
    
