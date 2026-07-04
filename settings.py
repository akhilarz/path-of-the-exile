"""
Game settings, colors, and constants
"""
import pygame

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (139, 0, 0)
GREEN = (40, 220, 40)
DARK_GREEN = (0, 100, 0)
BLUE = (60, 60, 220)
YELLOW = (220, 220, 40)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
PURPLE = (160, 50, 220)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)
BROWN = (101, 67, 33)
DARK_BROWN = (60, 40, 20)
LIGHT_GRAY = (180, 180, 180)
CYAN = (0, 200, 200)

# Player
PLAYER_SPEED = 250
PLAYER_SIZE = 16
PLAYER_MAX_HP = 150
PLAYER_MAX_MANA = 80
PLAYER_BASE_DAMAGE = 15
PLAYER_BASE_ARMOR = 10
PLAYER_BASE_CRIT = 8

# Enemies
ENEMY_TYPES = {
    "skeleton": {"hp": 30, "damage": 8, "speed": 100, "xp": 20, "color": (200, 200, 200), "size": 14},
    "zombie": {"hp": 60, "damage": 12, "speed": 50, "xp": 30, "color": (100, 150, 80), "size": 18},
    "archer": {"hp": 25, "damage": 10, "speed": 80, "xp": 25, "color": (180, 160, 200), "size": 12},
    "mage": {"hp": 35, "damage": 15, "speed": 70, "xp": 35, "color": (150, 50, 200), "size": 13},
    "boss": {"hp": 300, "damage": 30, "speed": 60, "xp": 200, "color": (220, 20, 20), "size": 28},
}

# Dungeon
DUNGEON_WIDTH = 2000
DUNGEON_HEIGHT = 2000
TILE_SIZE = 40
ROOM_MIN_SIZE = 300
ROOM_MAX_SIZE = 500

# Skills
SKILLS = {
    'cleave': {'name': 'Cleave', 'mult': 1.8, 'mana': 12, 'cd': 0.8, 'type': 'aoe', 'radius': 100},
    'heavy_strike': {'name': 'Heavy Strike', 'mult': 3.0, 'mana': 18, 'cd': 1.5, 'type': 'single'},
    'fireball': {'name': 'Fireball', 'mult': 2.0, 'mana': 22, 'cd': 1.2, 'type': 'projectile'},
}

# Fonts (initialized later in main)
FONT_TINY = None
FONT_SMALL = None
FONT_MEDIUM = None
FONT_LARGE = None
FONT_HUGE = None

def init_fonts():
    global FONT_TINY, FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_HUGE
    FONT_TINY = pygame.font.Font(None, 16)
    FONT_SMALL = pygame.font.Font(None, 20)
    FONT_MEDIUM = pygame.font.Font(None, 28)
    FONT_LARGE = pygame.font.Font(None, 36)
    FONT_HUGE = pygame.font.Font(None, 52)