import pygame as pg
import beings
import attacks

class Player(beings.Beings):

    def __init__(self, name:str, x:float, y:float, sizex:float=26.25, sizey:float=80.5, hp:int=20):
        super().__init__(name, x, y, sizex, sizey, hp)
        self.speed = 300
        self.image = pg.image.load('./assets/simon.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (26.25, 80.5))
        self.shooting_rate = 20 #shoot par secondes
        self.shoot_timer = 1/self.shooting_rate
        self.touched = False
        self.touched_cooldown = 0.5
        self.touched_time = 0

    def moove(self, dt, dir:pg.Vector2):
        self.direction = dir
        if self.direction.length()>0:
              self.direction = self.direction.normalize()
        velocity = self.direction * self.speed
        self.position += velocity * dt
        self.rect.x = self.position.x
        self.rect.y = self.position.y
         
    def displayHp(self):
        font = pg.font.Font(None, 36)
        if self.alive:
            text = "HP :"
        if self.hp <= 5:
            text += " x "
        elif self.hp > 5 and self.hp <= 10 :
            text += " x x "
        elif self.hp > 10 and self.hp <= 15 :
                    text += " x x x "
        elif self.hp > 15 and self.hp <= 20 :
                    text += " x x x x "    

        text2 = font.render(text, True, (255,0,0))
        return text2

    def shoot(self, projectiles, dt):
        self.shoot_timer += dt
        if self.shoot_timer >= 1/self.shooting_rate:  
            projectile = attacks.Projectile(self.position.x, self.position.y, 3)
            projectiles.add(projectile)
            self.shoot_timer = 0

    def invulnerability(self):
        self.touched = True
        self.touched_time = 0

    def update(self, keys, projectiles_player, dt):
        self.touched_time += dt
        if self.touched and self.touched_time > self.touched_cooldown:
            self.touched = False
             
        self.direction = pg.Vector2(0,0)
      
        if keys[pg.K_RIGHT]:
            self.moove(dt, pg.Vector2(1,0))
        if keys[pg.K_LEFT]:
            self.moove(dt, pg.Vector2(-1,0))
        if keys[pg.K_DOWN]:
            self.moove(dt, pg.Vector2(0,1))  
        if keys[pg.K_UP]:
            self.moove(dt, pg.Vector2(0,-1))
        if keys[pg.K_SPACE]:
            self.shoot(projectiles_player, dt)
          
          
        #Mise en place des barières
        if self.rect.y < 0 :
            self.rect.y = 0
            self.position.y = 0
        if self.rect.y > 550:
            self.rect.y = 550
            self.position.y = 550
        if self.rect.x < 0 :
            self.rect.x = 0
            self.position.x = 0
        if self.rect.x > 750 :
            self.rect.x = 750
            self.position.x = 750
        

    
    

    