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
projectiles_player = pg.sprite.Group() #crée un groupe pour les projectiles
projectiles_ennemy = pg.sprite.Group()


def handle_events() -> list:
    """Récupère les différents evenements (boutons pressés etc...)"""
    keys = pg.key.get_pressed()
    return keys

def update(dt:float, keys:list, player1:player.Player, ennemies, projectiles_player = projectiles_player, projectiles_ennemy = projectiles_ennemy):
    """Update l'état du jeu en fonction des évenements"""
        

    collision = pg.sprite.spritecollide(player1, ennemies, False)

    for ennemy in collision:
        ennemy.attack()
        player1.hpLoss(ennemy.dammage)
        player1.invulnerability()
        print(player1.hp)
        player1.isDead()

    collision_player_projectile = pg.sprite.spritecollide(player1, projectiles_ennemy, False)

    for proj in collision_player_projectile :
        if not player1.touched :
            player1.hpLoss(proj.dammage)
            player1.invulnerability()
            print(player1.hp)
            player1.isDead()

    collisions = pg.sprite.groupcollide(projectiles_player,ennemies,False,False)

    for projectile, hit_enemies in collisions.items():
        for enemy in hit_enemies:
            enemy.hpLoss(projectile.dammage)
            enemy.isDead()
            projectile.ttl -=1

    player1.update(keys, projectiles_player, dt)

    ennemies.update(dt, projectiles_ennemy)
    projectiles_ennemy.update(dt)
    


def draw(player1:player.Player, projectiles_player = projectiles_player, ennemies = ennemies, projectiles_ennemy = projectiles_ennemy):
    """Gère l'affichage des modifications à l'écran """
    screen.fill('purple')
    ennemies.draw(screen)
    projectiles_ennemy.draw(screen)
    if player1.alive:
        screen.blit(player1.image, player1.rect)
        screen.blit(player1.displayHp(), (20,20))
        projectiles_player.draw(screen)
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
    projectiles_player.update(dt)

    draw(player1)

pg.quit()

