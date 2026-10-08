import pygame
from core.constants import COLOR_HITBOX_DEBUG, SECONDARY_COLOR_HITBOX_DEBUG
from core.asset_manager import AssetManager


class Door:
    """Représente une porte avec sa zone d'entrée et sa récompense."""

    def __init__(self, size: tuple[int, int], centerx: float, bottom: float, reward: str) -> None:
        # Frames d'une porte
        self.frames = [
            AssetManager.get_image(
                f"assets/rooms/door_frames/door_{index}.png",
                scale=size
            )
            for index in range(6)
        ]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(
            midbottom=(round(centerx), round(bottom))
        )

        # Image de l'upgrade
        icon_size = (round(self.rect.width*0.35), round(self.rect.height*0.35))
        self.upgrade_icon = AssetManager.get_image(
            f"assets/rewards/upgrade_icons/{reward}.png",
            scale=icon_size
        )
        self.upgrade_rect = self.upgrade_icon.get_rect(midtop=self.rect.center)

        # Etat de la porte
        self.is_open = False
        self.reward_id: str | None = reward

        self.animation_timer = 0.0
        self.frame_duration = 0.04  # Secondes entre deux frames

        # Zone d'entrée placée juste devant la porte
        self.trigger_rect = pygame.Rect(0, 0, self.rect.width, 50)
        self.trigger_rect.midtop = self.rect.midbottom

        # Zone au seuil pour avoir l'amélioration
        self.entry_rect = pygame.Rect(
            0, 0, round(self.rect.width * 0.7), 10
        )
        self.entry_rect.midtop = self.rect.midbottom

    def can_enter(self, player_hitbox: pygame.Rect) -> bool:
        """Indique si le joueur entre dans la porte ouverte."""
        return (
            self.is_open
            and self.entry_rect.colliderect(player_hitbox)
        )        

    def update(self, dt: float, player_hitbox: pygame.Rect, enabled: bool) -> None:
        """Anime l'ouverture ou la fermeture selon la position du joueur."""
        player_inside = (enabled and self.trigger_rect.colliderect(player_hitbox))
        target_frame = len(self.frames) - 1 if player_inside else 0

        if self.frame_index == target_frame:
            self.animation_timer = 0.0
            return

        self.animation_timer += dt

        while self.animation_timer >= self.frame_duration:
            self.animation_timer -= self.frame_duration

            if self.frame_index < target_frame:
                self.frame_index += 1
            else:
                self.frame_index -= 1

            if self.frame_index == target_frame:
                self.animation_timer = 0.0
                break

        self.image = self.frames[self.frame_index]
        self.is_open = self.frame_index == len(self.frames) - 1

    def draw(self, surface: pygame.Surface, debug: bool = False) -> None:
        """Affiche la porte et sa zone d'entrée si le débug est activé."""
        surface.blit(self.image, self.rect)

        if self.is_open:
            surface.blit(self.upgrade_icon, self.upgrade_rect)

        if debug:
            pygame.draw.rect(
                surface, COLOR_HITBOX_DEBUG, self.trigger_rect, 1
            )
            pygame.draw.rect(
                surface, SECONDARY_COLOR_HITBOX_DEBUG, self.entry_rect, 1
            )