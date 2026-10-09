import pygame
from core.asset_manager import AssetManager
from core.constants import (
    COLOR_HITBOX_DEBUG,
    COLOR_WHITE,
    DEBUG_MODE,
    JOYSTICK_DEADZONE,
    PLAYER_BASE_SPEED,
    PLAYER_FIRE_RATE,
    PLAYER_HITBOX_SCALE,
    PLAYER_MAX_HP,
    PLAYER_PROJECTILE_DAMAGE,
    PLAYER_PROJECTILE_SPEED,
)
from entities.projectiles.player_projectiles import ATTACK_TYPE_CLASS
from systems.collision_system import CollisionSystem


class Player(pygame.sprite.Sprite):
    """Entité Joueur avec contrôles (AZERTY/QWERTY/Manette), animations et tir."""

    def __init__(self, play_surface: pygame.Surface, play_area: pygame.Rect):
        super().__init__()

        self.play_surface = play_surface
        self.play_area = play_area

        # Groupe interne des projectiles tirés par ce joueur
        self.player_projectiles = pygame.sprite.Group()

        # Initialisation Manette
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            except pygame.error:
                self.joystick = None

        # Caractéristiques
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed
        self.base_max_hp = PLAYER_MAX_HP
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp
        self.base_damage = PLAYER_PROJECTILE_DAMAGE
        self.damage = self.base_damage
        self.base_fire_rate = PLAYER_FIRE_RATE
        self.fire_rate = self.base_fire_rate
        
        self.shoot_cooldown = 1.0 / self.fire_rate
        self.shoot_timer = 0.0
        self.dead = False

        self.attack_type = ATTACK_TYPE_CLASS["Base"]

        self.upgrades: dict[str, int] = {}
        self.upgrades_data = {}

        # Invulnérabilité temporaire après dégâts
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 0.6

        # Sprites et Animation
        self.sprites = AssetManager.get_player_sprites()
        self.state = "idle"
        self.sprite_direction = "right"
        self.frame = 0
        self.previous_state = self.state
        self.previous_direction = self.sprite_direction

        self.animation_timer = 0.0
        self.animation_speed = {
            "idle": 0.15,
            "walk": 0.12,
            "cast": 0.08,
            "death": 0.15,
            "hurt": 0.10,
        }

        self.cast_duration = 0.25
        self.cast_timer = 0.0

        self.look_direction = pygame.Vector2(1, 0)

        # Image et Hitbox
        self.image = self.sprites[self.state][self.sprite_direction][self.frame]
        self.rect = self.image.get_rect(center=self.play_surface.get_rect().center)

        self.hitbox = self.rect.copy()
        self.hitbox.scale_by_ip(PLAYER_HITBOX_SCALE)
        self.sync_hitbox()

    def sync_hitbox(self):
        """Synchronise précisément la boîte de collision sur les pieds du personnage."""
        self.hitbox.center = (self.rect.centerx, self.rect.centery + 10)

    def get_animation_direction(self) -> str:
        """Adapte les directions diagonales si une animation n'a que les 4 points cardinaux."""
        if self.state in ("death", "hurt"):
            diagonal_map = {
                "up_right": "right",
                "down_right": "down",
                "up_left": "up",
                "down_left": "left",
            }
            return diagonal_map.get(self.sprite_direction, self.sprite_direction)
        return self.sprite_direction

    def animate(self, dt: float):
        """Met à jour les frames d'animation en fonction de l'état."""
        if self.state != self.previous_state or self.sprite_direction != self.previous_direction:
            self.frame = 0
            self.animation_timer = 0.0
            self.previous_state = self.state
            self.previous_direction = self.sprite_direction

        direction = self.get_animation_direction()
        frames = self.sprites.get(self.state, {}).get(direction, [])

        if not frames:
            return

        if len(frames) <= 1:
            self.frame = 0
        else:
            self.animation_timer += dt
            speed = self.animation_speed.get(self.state, 0.12)
            if self.animation_timer >= speed:
                self.animation_timer = 0.0
                if self.state == "death":
                    self.frame = min(self.frame + 1, len(frames) - 1)
                else:
                    self.frame = (self.frame + 1) % len(frames)

        center = self.rect.center
        self.image = frames[self.frame]
        self.rect = self.image.get_rect(center=center)
        self.sync_hitbox()

    def can_move_to(self, dx: float, dy: float, obstacles: pygame.sprite.Group) -> bool:
        """Vérifie que la future position reste dans l'aire de jeu et sans collision obstacle."""
        future_hitbox = self.hitbox.move(dx, dy)
        if not self.play_area.contains(future_hitbox):
            return False
        return not CollisionSystem.check_obstacle_collision(future_hitbox, obstacles)

    def move(self, dx: float, dy: float, obstacles: pygame.sprite.Group):
        """Déplace le joueur avec glissement indépendant sur les axes X et Y contre les obstacles."""
        if self.can_move_to(dx, dy, obstacles):
            self.rect.move_ip(dx, dy)
        elif self.can_move_to(dx, 0, obstacles):
            self.rect.move_ip(dx, 0)
        elif self.can_move_to(0, dy, obstacles):
            self.rect.move_ip(0, dy)

        self.sync_hitbox()

    def take_damage(self, amount: int, debug: bool):
        """Inflige des dégâts avec délai d'invulnérabilité."""
        if debug or self.invulnerable_timer > 0:
            return

        self.hp -= amount
        self.invulnerable_timer = self.invulnerable_duration

        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.state = "death"

    def shoot(self, target_group: pygame.sprite.Group):
        """Crée un projectile dirigé selon l'orientation du joueur."""
        if self.dead:
            return

        self.state = "cast"
        self.cast_timer = self.cast_duration

        projectile = self.attack_type(
            area=self.play_area,
            pos=self.rect.center,
            direction=self.look_direction,
            owner="player",
            speed=PLAYER_PROJECTILE_SPEED,
            damage=100000000 if DEBUG_MODE else self.damage
        )

        target_group.add(projectile)
        self.player_projectiles.add(projectile)

    def get_movement_vector(self, keys) -> pygame.Vector2:
        """Gère les entrées clavier (AZERTY ZQSD + QWERTY WASD + Flèches) et manette."""
        direction = pygame.Vector2(0, 0)

        # Clavier : ZQSD ou WASD ou Flèches
        if keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        if keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1

        # Joystick Manette
        if self.joystick is not None:
            try:
                jx = self.joystick.get_axis(0)
                jy = self.joystick.get_axis(1)
                if abs(jx) > JOYSTICK_DEADZONE:
                    direction.x += jx
                if abs(jy) > JOYSTICK_DEADZONE:
                    direction.y += jy
            except pygame.error:
                pass

        if direction.length_squared() > 0:
            direction = direction.normalize()

        return direction

    def update_look_direction(self, move_dir: pygame.Vector2):
        """Met à jour le vecteur d'orientation et la direction du sprite."""
        self.look_direction = move_dir

        deadzone = JOYSTICK_DEADZONE
        if move_dir.x > deadzone and move_dir.y < -deadzone:
            self.sprite_direction = "up_right"
        elif move_dir.x < -deadzone and move_dir.y < -deadzone:
            self.sprite_direction = "up_left"
        elif move_dir.x > deadzone and move_dir.y > deadzone:
            self.sprite_direction = "down_right"
        elif move_dir.x < -deadzone and move_dir.y > deadzone:
            self.sprite_direction = "down_left"
        elif abs(move_dir.x) > abs(move_dir.y):
            self.sprite_direction = "right" if move_dir.x > 0 else "left"
        else:
            self.sprite_direction = "down" if move_dir.y > 0 else "up"


    def _change_attack_type(self, upgrade_id) -> None:
        attack_type: str = self.upgrades_data[upgrade_id]["attack_type"]
        self.attack_type = ATTACK_TYPE_CLASS[attack_type]


    def _recalculate_stats(self) -> None:
        """Recalcule les stats depuis les valeurs de base."""
        self.speed = self.base_speed
        self.max_hp = self.base_max_hp
        self.damage = self.base_damage
        self.fire_rate = self.base_fire_rate

        for upgrade_id, count in self.upgrades.items():
            data = self.upgrades_data[upgrade_id]
            
            if data["type"] != "stat":
                continue
            
            stat = data["stat"]
            bonus = data["bonus"] * count

            current_value = getattr(self, stat)
            setattr(self, stat, current_value + bonus)

        self.shoot_cooldown = 1.0 / self.fire_rate
        self.hp = min(self.hp, self.max_hp)


    def _handle_consumable(self, upgrade_id: str) -> None:
        """Applique l'effet d'un consommable."""
        if upgrade_id == "heal":
            bonus = self.upgrades_data[upgrade_id]["bonus"]
            self.hp = round(min(self.max_hp, self.hp + self.max_hp * bonus))


    def add_upgrade(self, upgrade_id: str, upgrade_data: dict) -> None:
        """Ajoute un upgrade et actualise les stats."""
        self.upgrades_data[upgrade_id] = upgrade_data.copy()
        self.upgrades[upgrade_id] = self.upgrades.get(upgrade_id, 0) + 1
        upgrade_type = self.upgrades_data[upgrade_id]["type"]
        if upgrade_type == "stat":
            self._recalculate_stats()
        elif upgrade_type == "consumable":
            self._handle_consumable(upgrade_id)
        elif upgrade_type == "attack":
            self._change_attack_type(upgrade_id)
        elif upgrade_type == "spell":
            pass

    def handle_inputs(self, dt: float, obstacles: pygame.sprite.Group, global_projectiles: pygame.sprite.Group):
        """Gère les entrées utilisateur pour le déplacement et l'attaque."""
        keys = pygame.key.get_pressed()

        # Touches d'attaque : L, Espace ou bouton manette
        shoot_pressed = keys[pygame.K_l] or keys[pygame.K_SPACE]
        if self.joystick is not None:
            try:
                shoot_pressed = shoot_pressed or self.joystick.get_button(0)
            except pygame.error:
                pass

        move_dir = self.get_movement_vector(keys)

        # Ralentissement lors du tir continu
        move_speed = self.speed * 0.8 if shoot_pressed else self.speed

        if move_dir.length_squared() > 0:
            dx = move_dir.x * move_speed * dt
            dy = move_dir.y * move_speed * dt
            self.move(dx, dy, obstacles)

            if not shoot_pressed:
                self.update_look_direction(move_dir)

            if self.cast_timer <= 0:
                self.state = "walk"
        else:
            if self.cast_timer <= 0:
                self.state = "idle"

        # Gestion du tir
        if shoot_pressed and self.shoot_timer <= 0:
            self.shoot(global_projectiles)
            self.shoot_timer = self.shoot_cooldown

    def update(self, dt: float, obstacles: pygame.sprite.Group, global_projectiles: pygame.sprite.Group):
        """Mise à jour principale du joueur."""
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.cast_timer > 0:
            self.cast_timer -= dt

        if not self.dead:
            self.handle_inputs(dt, obstacles, global_projectiles)

        self.animate(dt)

    def draw(self, surface: pygame.Surface | None = None, debug: bool = False):
        """Affiche le joueur, le réticule de visée et les éléments de débug si activés."""
        target = surface if surface is not None else self.play_surface

        # Clignotement en cas d'invulnérabilité
        if self.invulnerable_timer > 0 and int(self.invulnerable_timer * 20) % 2 == 0:
            return

        # Réticule de visée directionnelle
        aim_dist = 85
        aim_pos = self.rect.center + self.look_direction * aim_dist
        pygame.draw.circle(target, COLOR_WHITE, (round(aim_pos.x), round(aim_pos.y)), 6, 2)

        target.blit(self.image, self.rect)

        if debug:
            pygame.draw.rect(target, COLOR_HITBOX_DEBUG, self.hitbox, 2)