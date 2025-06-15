"""
Configuration settings for MindFlip: Memory Arcade
"""

import os
import pathlib

# Base paths
BASE_DIR = pathlib.Path(__file__).parent.parent
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CARDS_DIR = os.path.join(ASSETS_DIR, "cards")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GAME_TITLE = "MindFlip: Memory Arcade"

# Card settings
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_MARGIN = 10
CARD_BACK_COLOR = (50, 50, 200)  # Blue
CARD_FRONT_COLOR = (200, 200, 200)  # Light gray
CARD_HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow
CARD_MATCHED_COLOR = (150, 255, 150)  # Light green for matched cards

# UI settings
BACKGROUND_COLOR = (30, 30, 60)  # Dark blue
TEXT_COLOR = (255, 255, 255)  # White
TITLE_COLOR = (255, 220, 100)  # Gold
SCORE_COLOR = (100, 255, 100)  # Green
LIVES_COLOR = (255, 100, 100)  # Red
BUTTON_COLOR = (80, 80, 180)  # Button background
BUTTON_HOVER_COLOR = (100, 100, 220)  # Button hover
BUTTON_TEXT_COLOR = (255, 255, 255)  # Button text
ICON_COLOR = (200, 200, 255)  # Icon color
ICON_HOVER_COLOR = (255, 255, 255)  # Icon hover color

# Game timing (in milliseconds)
FLIP_DELAY = 1000  # Time cards stay flipped when not matched
LEVEL_TRANSITION_DELAY = 2000  # Time between levels (2 seconds)
MATCH_ANIMATION_TIME = 500  # Time for match animation

# High score file
HIGH_SCORE_FILE = os.path.join(DATA_DIR, "high_score.txt")

# Starting game parameters
INITIAL_LIVES = 3
STARTING_LEVEL = 1
STARTING_GRID = (2, 2)  # rows, columns (2x2 = 4 cards, 2 pairs)

# Life increment logic
LIVES_INCREMENT_LEVELS = 2  # Award +1 life every 2 levels

# Points
MATCH_POINTS = 10
LEVEL_BONUS = 20
TIME_BONUS_FACTOR = 0.5  # Bonus points factor for quick matches

# Debug mode
DEBUG_MODE = False  # Set to False by default, can be toggled in game

# Power-up settings
POWERUP_CHANCE = 0.30         # 30% chance of a card being a power-up
POWERUP_TYPES = {
    'REVEAL': {'symbol': '👁️', 'color': (100, 200, 255)},  # Reveals cards temporarily
    'HINT': {'symbol': '💡', 'color': (255, 255, 100)},     # Highlights matching pair
    'EXTRA_LIFE': {'symbol': '❤️', 'color': (255, 100, 100)} # Gives an extra life
}

# Animation settings
ANIMATE_BACKGROUND = True
BACKGROUND_ANIMATION_SPEED = 0.5  # Speed of background animation

# Game rules text
GAME_RULES = [
    "HOW TO PLAY:",
    "1. Flip cards to find matching pairs",
    "2. Use arrow keys to navigate",
    "3. Press Enter to flip a card",
    "4. Match all pairs to complete a level",
    "5. Each level adds more cards",
    "6. Earn an extra life every 2 levels",
    "7. Press ESC to return to menu",
    "8. Press R to restart, Q to quit",
    "9. Look for special power-up cards!"
]

# Points system text
POINTS_SYSTEM = [
    "SCORING SYSTEM:",
    f"• Match found: +{MATCH_POINTS} points",
    f"• Level completion: +{LEVEL_BONUS} × level",
    "• Extra life: Every 2 levels",
    "• Grid size: +2 cards per level",
    "• Power-ups: Special abilities when matched",
    "• High scores not saved in Debug Mode"
]

# Game difficulty settings
DIFFICULTY_EASY = 0
DIFFICULTY_MEDIUM = 1
DIFFICULTY_HARD = 2
DIFFICULTY = DIFFICULTY_MEDIUM  # Default difficulty
