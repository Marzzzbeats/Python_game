import pygame




class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            self.handle_events()
            # self.update(dt)
            # self.draw()

            pygame.display.flip()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False