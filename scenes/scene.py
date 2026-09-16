import pygame



class Scene:
    def __init__(self, game):
        self.game = game


    def handle_events(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.pos)

