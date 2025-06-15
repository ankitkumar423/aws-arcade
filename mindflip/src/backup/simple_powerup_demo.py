import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_MARGIN = 10
BACKGROUND_COLOR = (30, 30, 60)
CARD_BACK_COLOR = (50, 50, 200)
CARD_FRONT_COLOR = (200, 200, 200)
CARD_HIGHLIGHT_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

# Power-up settings
POWERUP_CHANCE = 0.30  # 30% chance of a card being a power-up
POWERUP_TYPES = {
    'REVEAL': {'symbol': '👁️', 'color': (100, 200, 255)},  # Reveals cards temporarily
    'HINT': {'symbol': '💡', 'color': (255, 255, 100)},     # Highlights matching pair
    'EXTRA_LIFE': {'symbol': '❤️', 'color': (255, 100, 100)} # Gives an extra life
}

class Card:
    def __init__(self, value, row, col, powerup_type=None):
        self.value = value
        self.row = row
        self.col = col
        self.flipped = False
        self.matched = False
        self.powerup_type = powerup_type
    
    def flip(self):
        if not self.matched:
            self.flipped = not self.flipped
            return True
        return False
    
    def mark_matched(self):
        self.matched = True
        self.flipped = True

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("MindFlip Power-Up Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 24)
        
        self.grid_size = (2, 2)  # Start with a 2x2 grid
        self.cards = []
        self.cursor_pos = (0, 0)
        self.first_card = None
        self.second_card = None
        self.match_time = 0
        self.game_state = 0  # 0: first card, 1: second card, 2: delay
        self.lives = 3
        self.score = 0
        self.level = 1
        
        self.setup_level()
    
    def setup_level(self):
        rows, cols = self.grid_size
        
        # Create pairs of cards
        num_pairs = (rows * cols) // 2
        values = list(range(1, num_pairs + 1))
        pairs = values + values  # Duplicate each value to create pairs
        random.shuffle(pairs)
        
        # Determine which values will be power-ups
        powerup_values = []
        for value in range(1, num_pairs + 1):
            if random.random() < POWERUP_CHANCE:
                powerup_values.append(value)
        
        # Assign power-up types to values
        powerup_assignments = {}
        for value in powerup_values:
            powerup_type = random.choice(list(POWERUP_TYPES.keys()))
            powerup_assignments[value] = powerup_type
        
        # Create card grid
        self.cards = []
        card_index = 0
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
    
    def draw_cards(self):
        rows, cols = self.grid_size
        
        # Calculate grid dimensions
        grid_width = cols * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
        grid_height = rows * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
        
        # Center the grid on screen
        start_x = (WINDOW_WIDTH - grid_width) // 2
        start_y = 120  # Position below HUD
        
        # Draw each card
        for card in self.cards:
            x = start_x + card.col * (CARD_WIDTH + CARD_MARGIN)
            y = start_y + card.row * (CARD_HEIGHT + CARD_MARGIN)
            
            # Draw card background
            if card.matched:
                # Matched cards get a green tint
                pygame.draw.rect(self.screen, (150, 255, 150), (x, y, CARD_WIDTH, CARD_HEIGHT))
            elif card.flipped:
                # Flipped but not matched cards
                if card.powerup_type:
                    # Use power-up color
                    powerup_color = POWERUP_TYPES[card.powerup_type]['color']
                    pygame.draw.rect(self.screen, powerup_color, (x, y, CARD_WIDTH, CARD_HEIGHT))
                else:
                    pygame.draw.rect(self.screen, CARD_FRONT_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT))
            else:
                # Face-down cards
                pygame.draw.rect(self.screen, CARD_BACK_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT))
            
            # Draw card value if flipped
            if card.flipped:
                if card.powerup_type:
                    # Draw power-up symbol
                    value_text = self.font.render(POWERUP_TYPES[card.powerup_type]['symbol'] + str(card.value), True, (0, 0, 0))
                else:
                    value_text = self.font.render(str(card.value), True, (0, 0, 0))
                text_rect = value_text.get_rect(center=(x + CARD_WIDTH//2, y + CARD_HEIGHT//2))
                self.screen.blit(value_text, text_rect)
            
            # Highlight the card under the cursor
            if card.row == self.cursor_pos[0] and card.col == self.cursor_pos[1]:
                pygame.draw.rect(self.screen, CARD_HIGHLIGHT_COLOR, 
                                (x - 3, y - 3, CARD_WIDTH + 6, CARD_HEIGHT + 6), 3)
    
    def draw_hud(self):
        # Draw level
        level_text = self.small_font.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, (WINDOW_WIDTH//2 - level_text.get_width()//2, 70))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, (100, 255, 100))
        self.screen.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 20, 70))
        
        # Draw lives
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, (255, 100, 100))
        self.screen.blit(lives_text, (20, 70))
        
        # Draw title
        title = self.font.render("MIND FLIP: POWER-UP DEMO", True, (255, 220, 100))
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=20)
        self.screen.blit(title, title_rect)
        
        # Draw instructions
        instructions = self.small_font.render("Arrow keys to move, Enter to flip, R to reset, Q to quit", True, TEXT_COLOR)
        instructions_rect = instructions.get_rect(centerx=WINDOW_WIDTH//2, bottom=WINDOW_HEIGHT - 20)
        self.screen.blit(instructions, instructions_rect)
        
        # Draw power-up explanation
        powerup_text = self.small_font.render("Power-up cards: 👁️ Reveal, 💡 Hint, ❤️ Extra Life", True, TEXT_COLOR)
        powerup_rect = powerup_text.get_rect(centerx=WINDOW_WIDTH//2, bottom=WINDOW_HEIGHT - 50)
        self.screen.blit(powerup_text, powerup_rect)
    
    def get_card_at_cursor(self):
        row, col = self.cursor_pos
        for card in self.cards:
            if card.row == row and card.col == col:
                return card
        return None
    
    def move_cursor(self, direction):
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
    
    def flip_card(self):
        card = self.get_card_at_cursor()
        if not card or card.matched or card.flipped:
            return False
        
        if self.game_state == 0:  # First card
            card.flip()
            self.first_card = card
            self.game_state = 1  # Second card state
        elif self.game_state == 1:  # Second card
            card.flip()
            self.second_card = card
            self.game_state = 2  # Delay state
            self.match_time = time.time()
            
            # Check for match
            if self.first_card.value == self.second_card.value:
                # Match found
                self.first_card.mark_matched()
                self.second_card.mark_matched()
                self.score += 10
                
                # Handle power-up activation
                if self.first_card.powerup_type:
                    self.activate_powerup(self.first_card.powerup_type)
                elif self.second_card.powerup_type:
                    self.activate_powerup(self.second_card.powerup_type)
                
                # Check if level complete
                if all(card.matched for card in self.cards):
                    self.level += 1
                    self.score += 20 * self.level
                    
                    # Increase grid size for next level
                    if self.level <= 2:
                        self.grid_size = (2, 3)  # 2x3 = 6 cards
                    elif self.level <= 3:
                        self.grid_size = (2, 4)  # 2x4 = 8 cards
                    elif self.level <= 4:
                        self.grid_size = (3, 4)  # 3x4 = 12 cards
                    else:
                        self.grid_size = (4, 4)  # 4x4 = 16 cards
                    
                    self.setup_level()
            else:
                # Not a match
                self.lives -= 1
                if self.lives <= 0:
                    print("Game over! Final score:", self.score)
                    self.reset()
        
        return True
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up effect."""
        if powerup_type == 'REVEAL':
            print("Power-up activated: REVEAL - All cards revealed for 3 seconds!")
            # In a full implementation, this would temporarily reveal all cards
        elif powerup_type == 'HINT':
            print("Power-up activated: HINT - A matching pair is highlighted!")
            # In a full implementation, this would highlight a matching pair
        elif powerup_type == 'EXTRA_LIFE':
            print("Power-up activated: EXTRA LIFE - You gained an extra life! ♥")
            self.lives += 1
    
    def update(self):
        # Handle delay state
        if self.game_state == 2:
            if time.time() - self.match_time > 1.0:  # 1 second delay
                if not self.first_card.matched:
                    # Cards didn't match - flip them back
                    self.first_card.flip()
                    self.second_card.flip()
                
                self.game_state = 0  # Back to first card state
                self.first_card = None
                self.second_card = None
    
    def reset(self):
        self.grid_size = (2, 2)
        self.level = 1
        self.score = 0
        self.lives = 3
        self.setup_level()
    
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_cursor('up')
                    elif event.key == pygame.K_DOWN:
                        self.move_cursor('down')
                    elif event.key == pygame.K_LEFT:
                        self.move_cursor('left')
                    elif event.key == pygame.K_RIGHT:
                        self.move_cursor('right')
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.flip_card()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        running = False
            
            # Update game state
            self.update()
            
            # Draw everything
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_hud()
            self.draw_cards()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
