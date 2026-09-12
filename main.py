import pygame as pg

pg.init()
screen = pg.display.set_mode((800, 600))
pg.display.set_caption('Test')
clock = pg.time.Clock()
dt = clock.tick(60) / 1000 #Temps entre chaque frame (60 fps / 1000)
running = True
player_x = 100
player_y = 100
speed = 75 #Gère la vitesse / célocité du perso


def handle_events(running:bool) -> list:
    """Récupère les différents evenements (boutons pressés etc...)"""
    keys = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    return keys

def update(dt:float, keys:list):
    """Update l'état du jeu en fonction des évenements"""
    if keys[pg.K_RIGHT]:
        player_x += dt*speed
    if keys[pg.K_LEFT]:
        player_x-= dt*speed
    if keys[pg.K_DOWN]:
        player_y+= dt*speed
    if keys[pg.K_UP]:
        player_y-= dt*speed
    
    
    if player_y < 0 :
        player_y = 0
    if player_y > 550:
        player_y = 550
    if player_x < 0 :
        player_x = 0
    if player_x > 750 :
        player_x = 750  


def draw():
    """Gère l'affichage des modifications à l'écran """
    print((player_x, player_y))
    screen.fill('purple')
    pg.draw.rect(screen, (255,0,0), (player_x, player_y, 50, 50))
    pg.display.flip()

    
while running :

    keys = handle_events(running)

    update(dt, keys)

    draw()

pg.quit()