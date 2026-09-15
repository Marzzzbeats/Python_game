import pygame

from scenes.gameplay import Gameplay


class Game:
    def __init__(self, monitor_width, monitor_height):
        self.screen = pygame.display.set_mode(size=(monitor_width*0.9, monitor_height*0.9), display=0)
        self.clock = pygame.time.Clock()

        self.running = True
        self.current_scene = Gameplay(self)


    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()


    def handle_events(self):
        for event in pygame.event.get():
            self.current_scene.handle_events(event)


    def update(self, dt):
        self.current_scene.update(dt)


    def draw(self):
        self.current_scene.draw()
