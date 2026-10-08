import pygame
from core.constants import (
    COLOR_BG,
    COLOR_HITBOX_DEBUG,
    COLOR_PLAY_AREA_BORDER,
    DEBUG_MODE,
    GAME_SURFACE_HEIGHT_RATIO,
    GAME_SURFACE_WIDTH_RATIO,
    OFFSET_X_RATIO,
    OFFSET_Y_RATIO,
    PLAY_AREA_H_RATIO,
    PLAY_AREA_W_RATIO,
    PLAY_AREA_X_RATIO,
    PLAY_AREA_Y_RATIO,
)
from entities.player import Player
from rooms.room_manager import RoomManager
from entities.interactables.reward_manager import RewardManager
from scenes.scene import Scene
from systems.collision_system import CollisionSystem
from ui.hud import HUD


class Gameplay(Scene):
    """Scène principale du jeu orchestrant le joueur, la salle courante, les collisions et l'interface."""

    def __init__(self, game):
        super().__init__(game)

        screen_w, screen_h = self.game.screen.get_size()

        # Surface de jeu intérieure et positionnement
        game_width = screen_w * GAME_SURFACE_WIDTH_RATIO
        game_height = screen_h * GAME_SURFACE_HEIGHT_RATIO
        self.play_surface = pygame.Surface((game_width, game_height))
        self.offset_x = screen_w * OFFSET_X_RATIO
        self.offset_y = screen_h * OFFSET_Y_RATIO

        # Aire de déplacement restreinte (à l'intérieur du cadre de jeu)
        self.play_area = pygame.Rect(
            self.play_surface.get_width() * PLAY_AREA_X_RATIO,
            self.play_surface.get_height() * PLAY_AREA_Y_RATIO,
            self.play_surface.get_width() * PLAY_AREA_W_RATIO,
            self.play_surface.get_height() * PLAY_AREA_H_RATIO
        )

        # Groupe global pour tous les projectiles (joueur + ennemis)
        self.all_projectiles = pygame.sprite.Group()

        # Gestionnaire des rewards
        self.reward_manager = RewardManager()

        # Joueur
        self.player = Player(self.play_surface, self.play_area)

        # Gestionnaire de salles et progression
        self.room_manager = RoomManager("rooms.json")
        self.current_room = self.room_manager.create_room(
            tier=0,
            room_index=0,
            play_surface=self.play_surface,
            play_area=self.play_area,
            reward_manager=self.reward_manager,
            player_upgrades=self.player.upgrades
        )
        self.transitioning = False

        # Interface HUD
        self.hud = HUD(self.game.screen.get_size())

    def restart_game(self):
        """Réinitialise la partie après un Game Over."""
        self.all_projectiles.empty()
        self.current_room = self.room_manager.reset(self.play_surface, self.play_area, self.reward_manager, self.player.upgrades)
        self.player = Player(self.play_surface, self.play_area)
        self.hud.reset_game_over()

    def advance_to_next_room(self):
        """Passe à la salle suivante tout en conservant l'état du joueur."""
        self.all_projectiles.empty()
        self.current_room = self.room_manager.next_room(self.play_surface, self.play_area, self.reward_manager, self.player.upgrades)
        # Recentrer le joueur sur la nouvelle salle
        self.player.rect.center = self.play_surface.get_rect().center
        self.player.sync_hitbox()
        self.transitioning = False

    def check_transition(self) -> None:
        door = self.current_room.selected_door
        if door is not None and not self.transitioning:
            self.transitioning = True
            self.player.add_upgrade(door.reward_id, self.reward_manager.data[door.reward_id])
            self.advance_to_next_room()

    def handle_events(self, event: pygame.event.Event):
        super().handle_events(event)

        if event.type == pygame.KEYDOWN:
            # Touche F3 : bascule du mode débug
            if event.key == pygame.K_F3 or event.key == pygame.K_3:
                if DEBUG_MODE:
                    DEBUG_MODE.pop()
                else:
                    DEBUG_MODE.append(1)

            # Touche R : recommencer
            elif event.key == pygame.K_r and self.player.dead:
                self.restart_game()

    def update(self, dt: float):
        # En cas de mort du joueur, seule son animation finale et le fondu continuent
        if self.player.dead:
            self.player.animate(dt)
            return

        # Mise à jour du joueur
        self.player.update(dt, self.current_room.obstacles, self.all_projectiles)

        # Mise à jour de la salle et des ennemis
        self.current_room.update(dt, self.player, self.all_projectiles)

        # Vérifie le choix de l'amélioration et du passage a la room suivante
        self.check_transition()

        # Mise à jour des projectiles
        self.all_projectiles.update(dt)

        # Détection et résolution des collisions via le CollisionSystem
        CollisionSystem.handle_player_projectiles_vs_enemies(
            self.player.player_projectiles,
            self.current_room.enemies
        )
        CollisionSystem.handle_enemy_projectiles_vs_player(
            self.current_room.enemy_projectiles,
            self.player
        )
        CollisionSystem.handle_projectiles_vs_obstacles(
            self.player.player_projectiles,
            self.current_room.obstacles
        )
        CollisionSystem.handle_projectiles_vs_obstacles(
            self.current_room.enemy_projectiles,
            self.current_room.obstacles
        )
        CollisionSystem.handle_player_vs_enemies_contact(
            self.player,
            self.current_room.enemies
        )

    def draw(self):
        # Arrière-plan de la fenêtre
        self.game.screen.fill(COLOR_BG)

        # 1. Rendu de la salle (fond, obstacles, ennemis)
        self.current_room.draw(self.play_surface, DEBUG_MODE)

        # 2. Rendu du joueur
        self.player.draw(self.play_surface, DEBUG_MODE)

        # 3. Rendu des projectiles
        self.player.player_projectiles.draw(self.play_surface)
        self.current_room.enemy_projectiles.draw(self.play_surface)

        # 4. Rendu de la bordure d'aire de jeu (en débug ou léger contour)
        if DEBUG_MODE:
            pygame.draw.rect(self.play_surface, COLOR_PLAY_AREA_BORDER, self.play_area, 2)
            for proj in self.all_projectiles:
                pygame.draw.rect(self.play_surface, COLOR_HITBOX_DEBUG, proj.hitbox, 1)

        # 5. Affichage de la surface de jeu sur l'écran principal
        self.game.screen.blit(self.play_surface, (self.offset_x, self.offset_y))

        # 6. Éléments d'interface HUD
        self.hud.draw_health_bar(self.game.screen, self.player.hp, self.player.max_hp)
        self.hud.draw_attack_cooldown(self.game.screen, self.player.shoot_timer, self.player.shoot_cooldown)

        total_rooms = self.room_manager.get_room_count(self.room_manager.current_tier)
        self.hud.draw_room_info(
            screen=self.game.screen,
            tier=self.room_manager.current_tier,
            room_id=self.room_manager.current_room_index,
            total_rooms=total_rooms,
            enemy_count=len(self.current_room.enemies),
            is_cleared=self.current_room.is_cleared()
        )

        # 7. Écran de Game Over si le joueur est mort
        if self.player.dead:
            dt = self.game.clock.get_time() / 1000.0
            self.hud.draw_game_over(self.game.screen, dt)

        # 8. Overlay de debug FPS / Entités
        fps = self.game.clock.get_fps()
        total_entities = 1 + len(self.current_room.enemies) + len(self.current_room.obstacles) + len(self.all_projectiles)
        self.hud.draw_debug_overlay(self.game.screen, fps, total_entities, DEBUG_MODE)