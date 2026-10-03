import os
import random
import pygame


class AssetManager:
    """Gestionnaire centralisé pour le chargement, la transformation et la mise en cache des assets."""

    _images = {}
    _fonts = {}
    _player_sprites = None
    _obstacle_images = {}

    @classmethod
    def get_image(cls, path: str, scale: tuple[int, int] | None = None, scale_by: float | None = None, rotate: float | None = None) -> pygame.Surface:
        """Charge ou récupère une image mise en cache avec transformations facultatives."""
        key = (path, scale, scale_by, rotate)
        if key in cls._images:
            return cls._images[key]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Asset introuvable : {path}")

        image = pygame.image.load(path).convert_alpha()

        if scale_by is not None:
            image = pygame.transform.scale_by(image, scale_by)
        elif scale is not None:
            image = pygame.transform.scale(image, scale)

        if rotate is not None and rotate != 0:
            image = pygame.transform.rotate(image, rotate)

        cls._images[key] = image
        return image

    @classmethod
    def get_font(cls, name: str | None, size: int) -> pygame.font.Font:
        """Récupère une police mise en cache sans la réallouer à chaque frame."""
        key = (name, size)
        if key not in cls._fonts:
            cls._fonts[key] = pygame.font.Font(name, size)
        return cls._fonts[key]

    @classmethod
    def normalize_player_sprite(cls, image: pygame.Surface, target_height: int = 90, canvas_size: int = 256) -> pygame.Surface:
        """Normalise l'échelle et l'ancrage d'un sprite joueur."""
        bbox = image.get_bounding_rect()
        visible = image.subsurface(bbox).copy()

        ratio = target_height / max(visible.get_height(), 1)
        new_width = round(visible.get_width() * ratio)
        new_height = target_height

        visible = pygame.transform.scale(visible, (new_width, new_height))
        canvas = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)

        x = (canvas_size - new_width) // 2
        foot_y = 190
        y = foot_y - new_height

        canvas.blit(visible, (x, y))
        return canvas

    @classmethod
    def get_player_sprites(cls) -> dict:
        """Charge l'ensemble des sprites du joueur une seule fois et les met en cache."""
        if cls._player_sprites is not None:
            return cls._player_sprites

        states = ["idle", "walk", "cast", "death", "hurt"]
        directions = ["up", "up_right", "right", "down_right", "down", "down_left", "left", "up_left"]
        target_heights = {"idle": 120, "walk": 90, "cast": 90, "death": 90, "hurt": 90}

        player_sprites = {}

        for state in states:
            player_sprites[state] = {}
            for direction in directions:
                player_sprites[state][direction] = []
                path = f"assets/player/{state}/{direction}"

                if not os.path.exists(path):
                    continue

                for filename in sorted(os.listdir(path)):
                    if filename.endswith(".png"):
                        raw_img = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                        normalized = cls.normalize_player_sprite(raw_img, target_height=target_heights.get(state, 90))
                        player_sprites[state][direction].append(normalized)

        cls._player_sprites = player_sprites
        return cls._player_sprites

    @classmethod
    def get_random_obstacle_image(cls, obstacle_folder: str, prefix: str) -> pygame.Surface:
        """Charge une variante aléatoire d'un obstacle en évitant les I/O disque inutiles."""
        cache_key = (obstacle_folder, prefix)
        if cache_key not in cls._obstacle_images:
            folder_path = os.path.join("assets", "rooms", "obstacles", obstacle_folder)
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"Dossier d'obstacles introuvable : {folder_path}")

            files = [f for f in sorted(os.listdir(folder_path)) if f.startswith(prefix) and f.endswith(".png")]
            if not files:
                raise FileNotFoundError(f"Aucune image trouvée pour {prefix} dans {folder_path}")

            cls._obstacle_images[cache_key] = [
                pygame.image.load(os.path.join(folder_path, f)).convert_alpha()
                for f in files
            ]

        images = cls._obstacle_images[cache_key]
        return random.choice(images).copy()
