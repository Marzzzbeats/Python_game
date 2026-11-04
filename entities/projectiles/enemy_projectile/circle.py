import pygame
from entities.projectiles.enemy_projectile import circle_projectile

class Circle():
    """Crée le cercle de base d'attaque"""

    def __init__(self,
                 screen: pygame.Surface,
                 center: tuple[float, float] | pygame.Vector2,
                 direction : pygame.Vector2,
                 circle_coordinates : list[tuple],
                 projectile_group : pygame.sprite.Group):
        
        self.screen = screen
        self.circle_center = center
        self.circle_direction = direction
        self.circle_coordinates = circle_coordinates
        self.all_proj = projectile_group
        self.circle_speed = 100

        for i in range(len(self.circle_coordinates)):
            proj = pygame.Vector2(self.circle_coordinates[i])
            next = pygame.Vector2(self.circle_coordinates[(i+1)%len(self.circle_coordinates)]) #Le prochain dans la liste (le modulo permet que le dernier de la liste suive le premier)
            direction = (next - proj).normalize() 
            projectile = circle_projectile.CircleProjectile(screen, proj, direction)
            self.all_proj.add(projectile)


    def updateCoordinates(self):
        """Met a jour les coordonnées en fonction de la position de chaque projectile"""
        ind = 0
        for projectile in self.all_proj :
            self.circle_coordinates[ind] = projectile.getPos()


    def update(self, dt):
        for i in range(len(self.circle_coordinates)):
            self.circle_coordinates[i] += self.circle_direction * self.circle_speed * dt
        self.updateCoordinates()
        print(self.circle_coordinates)
        self.all_proj.update(dt)