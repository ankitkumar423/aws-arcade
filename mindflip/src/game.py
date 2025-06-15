"""
Game state handler for MindFlip: Memory Arcade
"""

import os
import random
import time
from mindflip.src.card import Card
from mindflip.src.config import (
    HIGH_SCORE_FILE, 
    INITIAL_LIVES, 
    STARTING_LEVEL, 
    STARTING_GRID,
    MATCH_POINTS,
    LEVEL_BONUS,
    DATA_DIR,
    LIVES_INCREMENT_LEVELS,
    DEBUG_MODE,
    COMBO_BONUS_MULTIPLIER,
    MAX_COMBO_MULTIPLIER,
    COMBO_TIMEOUT
)

class Game:
    """
    Manages the game state, including level progression, scoring, and card matching.
    """
    
    # Game states
    STATE_FIRST_CARD = 0   # Waiting for first card selection
    STATE_SECOND_CARD = 1  # First card flipped, waiting for second
    STATE_DELAY = 2        # Two cards flipped, waiting for delay (match or no match)
    STATE_LEVEL_COMPLETE = 3  # Level completed, showing transition screen
    
    def __init__(self):
        """Initialize a new game."""
        self.reset()
        self.load_high_score()
        self.debug_mode = DEBUG_MODE
        self.text_size = 1.0  # Default text size
        
        # Combo system
        self.combo_count = 0
        self.last_match_time = 0
    
    def reset(self):
        """Reset the game to initial state."""
        self.level = STARTING_LEVEL
        self.score = 0
        self.tries = INITIAL_LIVES
        self.grid_size = STARTING_GRID  # (rows, cols)
        self.cards = []
        self.first_card = None
        self.second_card = None
        self.match_time = 0
        self.level_complete_time = 0
        self.game_over = False
        self.level_complete = False
        self.cursor_pos = (0, 0)  # (row, col)
        self.game_state = self.STATE_FIRST_CARD  # Start in first card state
        self.points_earned_this_level = 0
        
        # Reset combo
        self.combo_count = 0
        self.last_match_time = 0
        self.setup_level()
    
    def calculate_grid_size(self, level):
        """
        Calculate grid size based on level.
        
        Args:
            level: Current game level
            
        Returns:
            tuple: (rows, cols) for the grid
        """
        # Start with 2x2 (4 cards, 2 pairs)
        # Add 2 cards (1 pair) per level
        total_cards = 4 + (level - 1) * 2
        
        # Cap the total cards to prevent grid from becoming too large
        # Maximum of 24 cards (12 pairs) to ensure they fit on screen
        total_cards = min(total_cards, 24)
        
        # Determine optimal grid dimensions to fit within screen
        if total_cards <= 6:  # 2x3
            return (2, total_cards // 2)
        elif total_cards <= 8:  # 2x4
            return (2, 4)
        elif total_cards <= 12:  # 3x4
            return (3, 4)
        elif total_cards <= 16:  # 4x4
            return (4, 4)
        elif total_cards <= 20:  # 4x5
            return (4, 5)
        elif total_cards <= 24:  # 4x6
            return (4, 6)
        else:  # This shouldn't happen due to the cap, but just in case
            return (4, 6)
    
    def setup_level(self):
        """Set up the current level with appropriate grid size and cards."""
        # Calculate grid size based on level
        self.grid_size = self.calculate_grid_size(self.level)
        rows, cols = self.grid_size
        
        # Reset level state
        self.level_complete = False
        self.game_state = self.STATE_FIRST_CARD
        self.points_earned_this_level = 0
        
        # Create pairs of cards
        num_pairs = (rows * cols) // 2
        values = list(range(1, num_pairs + 1))
        pairs = values + values  # Duplicate each value to create pairs
        random.shuffle(pairs)
        
        # Create card grid
        self.cards = []
        card_index = 0
        for row in range(rows):
            for col in range(cols):
                if card_index < len(pairs):
                    self.cards.append(Card(pairs[card_index], row, col))
                    card_index += 1
        
        # Reset cursor to top-left
        self.cursor_pos = (0, 0)
        self.first_card = None
        self.second_card = None
    
    def move_cursor(self, direction):
        """
        Move the cursor in the specified direction.
        
        Args:
            direction (str): One of 'up', 'down', 'left', 'right'
        """
        row, col = self.cursor_pos
        rows, cols = self.grid_size
        
        if direction == 'up':
            row = (row - 1) % rows
        elif direction == 'down':
            row = (row + 1) % rows
        elif direction == 'left':
            col = (col - 1) % cols
        elif direction == 'right':
            col = (col + 1) % cols
        
        self.cursor_pos = (row, col)
    
    def check_combo(self):
        """Check and update combo status."""
        current_time = time.time()
        
        # If it's been too long since the last match, reset combo
        if current_time - self.last_match_time > COMBO_TIMEOUT and self.combo_count > 0:
            self.combo_count = 0
            return False
            
        return True
    
    def get_combo_multiplier(self):
        """Get the current combo multiplier for scoring."""
        if self.combo_count == 0:
            return 1.0
            
        multiplier = 1.0 + (self.combo_count * COMBO_BONUS_MULTIPLIER)
        return min(multiplier, MAX_COMBO_MULTIPLIER)
    
    def flip_card(self):
        """
        Flip the card at the current cursor position based on current game state.
        
        Returns:
            bool: True if a card was flipped, False otherwise
        """
        if self.game_over or self.level_complete:
            return False
            
        # Don't allow flipping cards during delay or level complete states
        if self.game_state in (self.STATE_DELAY, self.STATE_LEVEL_COMPLETE):
            return False
            
        card = self.get_card_at_cursor()
        if not card or card.matched or card.flipped:
            return False
        
        # Handle card flipping based on game state
        if self.game_state == self.STATE_FIRST_CARD:
            # First card of a pair
            card.flip()
            self.first_card = card
            self.game_state = self.STATE_SECOND_CARD
            
        elif self.game_state == self.STATE_SECOND_CARD:
            # Second card of a pair
            card.flip()
            self.second_card = card
            
            # Enter delay state to show both cards
            self.game_state = self.STATE_DELAY
            self.match_time = time.time()
            
            # Check for match
            if self.first_card.value == self.second_card.value:
                # Match found
                self.first_card.mark_matched()
                self.second_card.mark_matched()
                
                # Update combo
                self.combo_count += 1
                self.last_match_time = time.time()
                
                # Calculate points with combo multiplier
                multiplier = self.get_combo_multiplier()
                points = int(MATCH_POINTS * multiplier)
                self.score += points
                self.points_earned_this_level += points
                
                # Check if level is complete
                if self.check_level_complete():
                    self.level_complete = True
                    self.level_complete_time = time.time()
                    self.game_state = self.STATE_LEVEL_COMPLETE
                    
                    # Add level bonus
                    level_bonus = LEVEL_BONUS * self.level
                    self.score += level_bonus
                    self.points_earned_this_level += level_bonus
                    
                    # Award extra life every LIVES_INCREMENT_LEVELS levels
                    if self.level % LIVES_INCREMENT_LEVELS == 0:
                        self.tries += 1
            else:
                # Not a match
                self.tries -= 1
                
                # Reset combo
                self.combo_count = 0
                
                if self.tries <= 0:
                    self.game_over = True
                    if not self.debug_mode:  # Only save high score if not in debug mode
                        self.save_high_score()
        
        return True
    
    def update(self):
        """
        Update game state, handling card flipping and level transitions.
        
        Returns:
            dict: Game state updates including any events that occurred
        """
        updates = {
            'match': False,
            'mismatch': False,
            'level_complete': False,
            'game_over': False,
            'extra_life': False
        }
        
        # Check combo status
        self.check_combo()
        if self.game_state == self.STATE_DELAY:
            if time.time() - self.match_time > 1.0:  # 1 second delay
                if self.first_card.matched:
                    # Cards matched - return to first card state
                    updates['match'] = True
                    self.game_state = self.STATE_FIRST_CARD
                    self.first_card = None
                    self.second_card = None
                else:
                    # Cards didn't match - flip them back
                    updates['mismatch'] = True
                    self.first_card.flip()
                    self.second_card.flip()
                    self.game_state = self.STATE_FIRST_CARD
                    self.first_card = None
                    self.second_card = None
        
        # Handle level completion transition
        elif self.game_state == self.STATE_LEVEL_COMPLETE:
            if time.time() - self.level_complete_time > 2.0:  # 2 second delay for level transition
                updates['level_complete'] = True
                self.level += 1
                
                # Check if we should award an extra life
                if (self.level - 1) % LIVES_INCREMENT_LEVELS == 0:
                    updates['extra_life'] = True
                
                self.setup_level()
        
        # Handle game over
        if self.game_over:
            updates['game_over'] = True
        
        return updates
    
    def check_level_complete(self):
        """Check if all cards have been matched."""
        return all(card.matched for card in self.cards)
    
    def load_high_score(self):
        """Load the high score from file."""
        self.high_score = 0
        
        # Create data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    self.high_score = int(f.read().strip())
        except (IOError, ValueError):
            # If there's an error reading the file, start with 0
            self.high_score = 0
    
    def save_high_score(self):
        """Save the high score to file if current score is higher."""
        if self.score > self.high_score:
            self.high_score = self.score
            
            # Create data directory if it doesn't exist
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
                
            try:
                with open(HIGH_SCORE_FILE, 'w') as f:
                    f.write(str(self.high_score))
            except IOError:
                pass  # Silently fail if we can't write the file
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
        
    def set_text_size(self, size):
        """Set the text size for UI elements."""
        self.text_size = size

    def get_card_at_cursor(self):
        """Get the card at the current cursor position."""
        row, col = self.cursor_pos
        for card in self.cards:
            if card.row == row and card.col == col:
                return card
        return None
