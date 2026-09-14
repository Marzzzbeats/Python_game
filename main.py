import pygame as pg
import player
import ennemy
import attacks

pg.init()
screen = pg.display.set_mode((800, 600))
pg.display.set_caption('Test')
clock = pg.time.Clock()
running = True

player1 = player.Player("Simon", 100, 100)
ennemies = pg.sprite.Group()
ennemy1 = ennemy.Ennemy("Mechant", 450, 300, 30, 30, 30)
ennemies.add(ennemy1)
projectiles = pg.sprite.Group() #crée un groupe pour les projectiles


def handle_events() -> list:
    """Récupère les différents evenements (boutons pressés etc...)"""
    keys = pg.key.get_pressed()
    return keys

def update(dt:float, keys:list, player1:player.Player, ennemies, projectiles = projectiles):
    """Update l'état du jeu en fonction des évenements"""
    player1.direction = pg.Vector2(0,0)

    if keys[pg.K_RIGHT]:
        player1.moove(dt, pg.Vector2(1,0))
    if keys[pg.K_LEFT]:
        player1.moove(dt, pg.Vector2(-1,0))
    if keys[pg.K_DOWN]:
        player1.moove(dt, pg.Vector2(0,1))  
    if keys[pg.K_UP]:
        player1.moove(dt, pg.Vector2(0,-1))
    if keys[pg.K_SPACE]:
        player1.shoot(projectiles, dt)


    #Mise en place des barières
    if player1.rect.y < 0 :
        player1.rect.y = 0
    if player1.rect.y > 550:
        player1.rect.y = 550
    if player1.rect.x < 0 :
        player1.rect.x = 0
    if player1.rect.x > 750 :
        player1.rect.x = 750  

    collision = pg.sprite.spritecollide(player1, ennemies, False)

    for ennemy in collision:
        ennemy.attack()
        player1.hpLoss(ennemy.dammage)
        print(player1.hp)
        player1.isDead()

    collisions = pg.sprite.groupcollide(projectiles,ennemies,False,False)

    for projectile, hit_enemies in collisions.items():
        for enemy in hit_enemies:
            enemy.hpLoss(projectile.dammage)
            enemy.isDead()
            projectile.ttl -=1

    ennemies.update()
    


def draw(player1:player.Player, projectiles = projectiles, ennemies = ennemies):
    """Gère l'affichage des modifications à l'écran """
    screen.fill('purple')
    ennemies.draw(screen)
    if player1.alive:
        screen.blit(player1.image, player1.rect)
        screen.blit(player1.displayHp(), (20,20))
        projectiles.draw(screen)
    else :
        font = pg.font.Font(None, 36)
        text = font.render("GAME OVER", True, (255,0,0))
        screen.blit(text, (20,20))
    pg.display.flip()

    
while running :

    dt = clock.tick(60) / 1000 #Temps entre chaque frame (60 fps / 1000)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    keys = handle_events()

    update(dt, keys, player1, ennemies)
    projectiles.update(dt)

    draw(player1)

pg.quit()