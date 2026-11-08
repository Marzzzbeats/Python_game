import pygame
from core.asset_manager import AssetManager
from core.constants import COLOR_COOLDOWN_OVERLAY, COLOR_HP_BAR, COLOR_WHITE


class HUD:
    """Gestionnaire d'interface utilisateur (HUD) : vie, rechargement d'attaque, état de la salle et game over."""

    def __init__(self, screen_size: tuple[int, int]):
        self.screen_width, self.screen_height = screen_size

        # Cadre de barre de vie
        self.health_bar_height = 150
        self.health_bar_frame = AssetManager.get_image(
            "assets/player/health_bar.png",
            scale=(self.health_bar_height * 3, self.health_bar_height)
        )

        # Icône d'attaque
        self.attack_image = AssetManager.get_image(
            "assets/misc/attack.png",
            scale=(180, 180)
        )
        self.alpha_layer_attack = pygame.Surface(self.attack_image.get_size(), pygame.SRCALPHA)

        # Écran de Game Over
        self.game_over_alpha = 0.0
        self.game_over_image = AssetManager.get_image(
            "assets/scenes/game_over.png",
            scale=screen_size
        )

    def draw_health_bar(self, screen: pygame.Surface, current_hp: int, max_hp: int):
        """Dessine la barre de vie du joueur."""
        offset = 40
        x = offset
        y = screen.get_height() - self.health_bar_height - offset
        frame_rect = self.health_bar_frame.get_rect(topleft=(x, y))

        bar_x = frame_rect.x + 90
        bar_y = frame_rect.y + 50
        max_width = 320
        bar_height = 40

        ratio = max(0.0, current_hp / max(max_hp, 1))
        current_width = int(max_width * ratio)
        health_rect = pygame.Rect(bar_x, bar_y, current_width, bar_height)
        full_bar_rect = pygame.Rect(bar_x, bar_y, max_width, bar_height)

        # Remplissage rouge
        pygame.draw.rect(screen, COLOR_HP_BAR, health_rect)

        # Texte PV
        font = AssetManager.get_font(None, 28)
        text = font.render(f"{current_hp} / {max_hp}", True, COLOR_WHITE)
        text_rect = text.get_rect(center=full_bar_rect.center)
        screen.blit(text, text_rect)

        # Cadre orné par-dessus
        screen.blit(self.health_bar_frame, frame_rect)

    def draw_attack_cooldown(self, screen: pygame.Surface, shoot_timer: float, shoot_cooldown: float):
        """Affiche l'icône d'attaque et son voile de rechargement."""
        w, h = self.attack_image.get_size()
        x = (screen.get_width() - w) // 2
        y = screen.get_height() - h - 25

        screen.blit(self.attack_image, (x, y))

        if shoot_cooldown > 0 and shoot_timer > 0:
            self.alpha_layer_attack.fill((0, 0, 0, 0))
            square_x = 40
            square_y = 35
            square_size = w - 80

            ratio = min(1.0, max(0.0, shoot_timer / shoot_cooldown))
            fill_height = int(square_size * ratio)
            current_y = square_y + square_size - fill_height

            overlay_rect = pygame.Rect(square_x, current_y, square_size, fill_height)
            pygame.draw.rect(self.alpha_layer_attack, COLOR_COOLDOWN_OVERLAY, overlay_rect)
            screen.blit(self.alpha_layer_attack, (x, y))

    def draw_room_info(self, screen: pygame.Surface, tier: int, room_id: int, total_rooms: int, enemy_count: int, is_cleared: bool):
        """Affiche les informations d'étage, de salle et d'objectifs."""
        font = AssetManager.get_font(None, 26)
        large_font = AssetManager.get_font(None, 34)

        info_text = f"Palier {tier} - Salle {room_id + 1}/{total_rooms} | Ennemis : {enemy_count}"
        rendered_info = font.render(info_text, True, (200, 200, 220))
        screen.blit(rendered_info, (40, 30))

        if is_cleared:
            cleared_surf = large_font.render("SALLE NETTOYÉE ! [N] pour avancer", True, (100, 255, 120))
            screen.blit(cleared_surf, ((screen.get_width() - cleared_surf.get_width()) // 2, 30))

    def draw_game_over(self, screen: pygame.Surface, dt: float):
        """Anime et affiche l'écran de Game Over en fondu."""
        self.game_over_alpha = min(255.0, self.game_over_alpha + (320.0 + self.game_over_alpha * 0.1) * dt)
        self.game_over_image.set_alpha(int(self.game_over_alpha))
        screen.blit(self.game_over_image, (0, 0))

        if self.game_over_alpha >= 180:
            font = AssetManager.get_font(None, 32)
            retry_text = font.render("Appuyez sur [R] pour recommencer", True, (255, 230, 150))
            rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80))
            screen.blit(retry_text, rect)

    def draw_debug_overlay(self, screen: pygame.Surface, fps: float, entity_count: int, debug_active: bool):
        """Affiche des indicateurs de performance et d'état débug."""
        font = AssetManager.get_font(None, 20)
        status = "ACTIF" if debug_active else "INACTIF"
        txt = font.render(f"FPS: {fps:.0f} | Entités: {entity_count} | [F3] Débug: {status}", True, (150, 255, 150))
        screen.blit(txt, (screen.get_width() - txt.get_width() - 20, 15))

    def reset_game_over(self):
        """Réinitialise l'opacité du fondu de mort."""
        self.game_over_alpha = 0.0
