import pygame

pygame.init()

screen = pygame.display.set_mode(size=(800, 600), display=0)
pygame.display.set_caption("Mon jeu")

clock = pygame.time.Clock()

running = True

while running:

    # 1. ÉVÉNEMENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. UPDATE
    # Plus tard : mouvements, collisions, ennemis...

    # 3. AFFICHAGE
    screen.fill((30, 30, 30))

    pygame.display.flip()

    # 4. LIMITATION DES FPS
    clock.tick(60)

pygame.quit()