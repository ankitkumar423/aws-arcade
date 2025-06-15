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
    POWERUP_CHANCE,
    POWERUP_TYPES
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
        self.combo_count = 0  # For combo system
        
        # Power-ups
        self.active_powerups = []
        self.hint_card = None
        self.powerup_message = None
    
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
        
        # Reset power-ups
        self.active_powerups = []
        self.hint_card = None
        self.powerup_message = None
        
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
        
        # Determine which values will be power-ups (ensure pairs match)
        powerup_values = []
        for value in range(1, num_pairs + 1):
            if random.random() < POWERUP_CHANCE:
                powerup_values.append(value)
        
        # Assign power-up types to values
        powerup_assignments = {}
        for value in powerup_values:
            powerup_type = random.choice(list(POWERUP_TYPES.keys()))
            powerup_assignments[value] = powerup_type
        
        # Create the cards
        for row in range(rows):
            for col in range(cols):
                if card_index < len(pairs):
                    value = pairs[card_index]
                    
                    # Check if this value is a power-up
                    powerup_type = None
                    if value in powerup_assignments:
                        powerup_type = powerup_assignments[value]
                    
                    self.cards.append(Card(value, row, col, powerup_type))
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
    
    def get_card_at_cursor(self):
        """Get the card at the current cursor position."""
        row, col = self.cursor_pos
        for card in self.cards:
            if card.row == row and card.col == col:
                return card
        return None
    
    def activate_powerup(self, card):
        """
        Activate a power-up card's special ability.
        
        Args:
            card: The power-up card that was matched
            
        Returns:
            str: Description of the power-up effect
        """
        if not card.powerup_type:
            return None
            
        effect_description = None
        
        if card.powerup_type == 'REVEAL':
            # Temporarily reveal all cards for a short time
            for c in self.cards:
                if not c.matched and not c.flipped:
                    c.temporarily_reveal = True
            self.active_powerups.append({
                'type': 'REVEAL',
                'end_time': time.time() + 3.0  # 3 seconds of reveal
            })
            effect_description = "All cards revealed for 3 seconds!"
            
        elif card.powerup_type == 'HINT':
            # Find a matching pair and highlight one card
            unmatched_cards = [c for c in self.cards if not c.matched and not c.flipped]
            if len(unmatched_cards) >= 2:
                # Find a pair
                values = {}
                for c in unmatched_cards:
                    if c.value in values:
                        # Found a pair
                        self.hint_card = c
                        self.active_powerups.append({
                            'type': 'HINT',
                            'end_time': time.time() + 5.0  # 5 seconds of hint
                        })
                        effect_description = "Hint activated! A matching card is highlighted."
                        break
                    values[c.value] = c
                    
        elif card.powerup_type == 'EXTRA_LIFE':
            # Award an extra life
            self.tries += 1
            effect_description = "Extra life awarded! ♥"
            
        return effect_description
    
    def update_powerups(self):
        """Update active power-ups and remove expired ones."""
        current_time = time.time()
        active_powerups_updated = []
        
        for powerup in self.active_powerups:
            if current_time < powerup['end_time']:
                active_powerups_updated.append(powerup)
            else:
                # Handle power-up expiration
                if powerup['type'] == 'REVEAL':
                    # Turn off temporary reveal
                    for card in self.cards:
                        card.temporarily_reveal = False
                elif powerup['type'] == 'HINT':
                    # Clear hint
                    self.hint_card = None
                    
        self.active_powerups = active_powerups_updated
    
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
                self.score += MATCH_POINTS
                self.points_earned_this_level += MATCH_POINTS
                
                # Check for power-ups
                self.powerup_message = None
                if self.first_card.powerup_type:
                    self.powerup_message = self.activate_powerup(self.first_card)
                if self.second_card.powerup_type and not self.powerup_message:
                    self.powerup_message = self.activate_powerup(self.second_card)
                
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
            'extra_life': False,
            'powerup_activated': self.powerup_message
        }
        
        # Reset powerup message after it's been processed
        self.powerup_message = None
        
        # Update power-ups
        self.update_powerups()
        
        # Handle delay state (showing two cards)
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
    
    def set_text_size(self, size):
        """Set the text size for UI elements."""
        # Text size adjustment not fully implemented yet
        pass

    def set_text_size(self, size):
        """Set the text size for UI elements."""
        # Text size adjustment not fully implemented yet
        pass

    def toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode

    def get_combo_multiplier(self):
        """Get the current combo multiplier for scoring."""
        return 1.0  # Combo system not fully implemented yet
