import pygame

# --- Affichage & Fenêtre ---
DEFAULT_SCREEN_WIDTH = 1280
DEFAULT_SCREEN_HEIGHT = 720
FPS = 60

# --- Couleurs ---
COLOR_BG = pygame.Color("#0f0e1f")
COLOR_PLAY_AREA_BORDER = pygame.Color("pink")
COLOR_GRID = pygame.Color("lime")
COLOR_HITBOX_DEBUG = pygame.Color("red")
COLOR_HP_BAR = pygame.Color("red")
COLOR_WHITE = pygame.Color("white")
COLOR_COOLDOWN_OVERLAY = (200, 200, 200, 120)

# --- Ratios de l'Aire de Jeu ---
GAME_SURFACE_WIDTH_RATIO = 0.975
GAME_SURFACE_HEIGHT_RATIO = 0.85
OFFSET_X_RATIO = 0.0125
OFFSET_Y_RATIO = 0.025

PLAY_AREA_X_RATIO = 0.0449688
PLAY_AREA_Y_RATIO = 0.1834696
PLAY_AREA_W_RATIO = 0.9105076
PLAY_AREA_H_RATIO = 0.6993642

# --- Joueur ---
PLAYER_BASE_SPEED = 400.0
PLAYER_MAX_HP = 10
PLAYER_FIRE_RATE = 1.0  # tirs par seconde
PLAYER_HITBOX_SCALE = 0.4
JOYSTICK_DEADZONE = 0.15

# --- Projectiles ---
PLAYER_PROJECTILE_SPEED = 550.0
PLAYER_PROJECTILE_DAMAGE = 1
ENEMY_PROJECTILE_SPEED = 450.0
ENEMY_PROJECTILE_DAMAGE = 1

# --- Symboles Layout Salles -> Obstacles ---
OBSTACLE_SYMBOLS = {
    "P": "Pillar",
    "W": "Wall",
    "C": "Container",
    "S": "Stone",
    "B": "Container",  # Baril/Container fallback
}

# --- Débug ---
DEBUG_MODE = True
