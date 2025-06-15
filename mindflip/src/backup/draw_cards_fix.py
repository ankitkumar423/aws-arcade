import re

with open('ui.py', 'r') as f:
    content = f.read()

# Find the draw_cards method
match = re.search(r'def draw_cards\(self, game\):(.*?)def', content, re.DOTALL)
if match:
    # Get the current method
    current_method = match.group(0)
    
    # Create a new method with power-up handling
    new_method = '''    def draw_cards(self, game):
        """
        Draw the card grid.
        
        Args:
            game: The game state object
        """
        rows, cols = game.grid_size
        
        # Calculate available space for the grid
        available_width = WINDOW_WIDTH - 40  # 20px margin on each side
        available_height = WINDOW_HEIGHT - 200  # Space for HUD and controls
        
        # Calculate card dimensions to fit within available space
        card_width = min(CARD_WIDTH, (available_width - (cols-1) * CARD_MARGIN) / cols)
        card_height = min(CARD_HEIGHT, (available_height - (rows-1) * CARD_MARGIN) / rows)
        
        # Maintain aspect ratio
        aspect_ratio = CARD_WIDTH / CARD_HEIGHT
        if card_width / card_height > aspect_ratio:
            card_width = card_height * aspect_ratio
        else:
            card_height = card_width / aspect_ratio
            
        # Calculate grid dimensions with the adjusted card size
        grid_width = cols * (card_width + CARD_MARGIN) - CARD_MARGIN
        grid_height = rows * (card_height + CARD_MARGIN) - CARD_MARGIN
        
        # Center the grid on screen
        start_x = (WINDOW_WIDTH - grid_width) // 2
        start_y = 120  # Position below HUD
        
        # Draw each card
        for card in game.cards:
            x = start_x + card.col * (card_width + CARD_MARGIN)
            y = start_y + card.row * (card_height + CARD_MARGIN)
            
            # Draw card background with different colors based on state
            if card.matched:
                # Matched cards get a green tint
                pygame.draw.rect(self.surface, CARD_MATCHED_COLOR, (x, y, card_width, card_height))
            elif card.flipped:
                # Flipped but not matched cards
                # If it's a power-up card, use a special color
                if card.powerup_type:
                    if card.powerup_type == 'REVEAL':
                        powerup_color = (100, 200, 255)  # Light blue
                    elif card.powerup_type == 'HINT':
                        powerup_color = (255, 255, 100)  # Light yellow
                    elif card.powerup_type == 'EXTRA_LIFE':
                        powerup_color = (255, 100, 100)  # Light red
                    else:
                        powerup_color = CARD_FRONT_COLOR
                    pygame.draw.rect(self.surface, powerup_color, (x, y, card_width, card_height))
                else:
                    pygame.draw.rect(self.surface, CARD_FRONT_COLOR, (x, y, card_width, card_height))
            else:
                # Face-down cards
                if game.debug_mode:
                    # Semi-transparent in debug mode
                    card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                    card_surface.fill((CARD_BACK_COLOR[0], CARD_BACK_COLOR[1], CARD_BACK_COLOR[2], 180))
                    self.surface.blit(card_surface, (x, y))
                else:
                    pygame.draw.rect(self.surface, CARD_BACK_COLOR, (x, y, card_width, card_height))
            
            # Scale font size based on card size
            font_scale = min(card_width / CARD_WIDTH, 1.0)
            card_font = pygame.font.SysFont('Arial', int(32 * font_scale), bold=True)
            debug_font = pygame.font.SysFont('Arial', int(16 * font_scale), bold=True)
            
            # Draw card value
            if card.flipped or (game.debug_mode and not card.matched):
                # For flipped cards or in debug mode, show the value
                if card.powerup_type:
                    # Add a symbol for power-up cards
                    symbol = ''
                    if card.powerup_type == 'REVEAL':
                        symbol = '👁️'
                    elif card.powerup_type == 'HINT':
                        symbol = '💡'
                    elif card.powerup_type == 'EXTRA_LIFE':
                        symbol = '❤️'
                    value_text = card_font.render(symbol + str(card.value), True, (0, 0, 0))
                else:
                    value_text = card_font.render(str(card.value), True, (0, 0, 0))
                text_rect = value_text.get_rect(center=(x + card_width//2, y + card_height//2))
                self.surface.blit(value_text, text_rect)
            
            # In debug mode, also show small number in corner for face-down cards
            if game.debug_mode and not card.flipped and not card.matched:
                if card.powerup_type:
                    symbol = ''
                    if card.powerup_type == 'REVEAL':
                        symbol = '👁️'
                    elif card.powerup_type == 'HINT':
                        symbol = '💡'
                    elif card.powerup_type == 'EXTRA_LIFE':
                        symbol = '❤️'
                    small_value = debug_font.render(symbol + str(card.value), True, (255, 255, 255))
                else:
                    small_value = debug_font.render(str(card.value), True, (255, 255, 255))
                self.surface.blit(small_value, (x + 5, y + 5))
            
            # If not in debug mode and card is face down, draw card back design
            if not game.debug_mode and not card.flipped:
                inner_margin = int(10 * font_scale)
                pygame.draw.rect(self.surface, (100, 100, 150), 
                                (x + inner_margin, y + inner_margin, 
                                 card_width - 2*inner_margin, card_height - 2*inner_margin))
                
                # Draw a simple pattern on the back
                line_spacing = int(30 * font_scale)
                line_margin = int(20 * font_scale)
                for i in range(3):
                    pygame.draw.line(self.surface, (50, 50, 100),
                                    (x + line_margin, y + line_margin + i*line_spacing),
                                    (x + card_width - line_margin, y + line_margin + i*line_spacing), 
                                    max(1, int(3 * font_scale)))
            
            # Highlight the card under the cursor
            if card.row == game.cursor_pos[0] and card.col == game.cursor_pos[1]:
                highlight_thickness = max(1, int(3 * font_scale))
                pygame.draw.rect(self.surface, CARD_HIGHLIGHT_COLOR, 
                                (x - highlight_thickness, y - highlight_thickness, 
                                 card_width + 2*highlight_thickness, card_height + 2*highlight_thickness), 
                                highlight_thickness)
                
            # Highlight hint card if active
            if hasattr(game, 'hint_card') and game.hint_card and card == game.hint_card:
                hint_thickness = max(1, int(4 * font_scale))
                pygame.draw.rect(self.surface, (255, 255, 0), 
                                (x - hint_thickness, y - hint_thickness, 
                                 card_width + 2*hint_thickness, card_height + 2*highlight_thickness), 
                                hint_thickness)
    
    def'''
    
    # Replace the method in the content
    modified_content = content.replace(current_method, new_method)
    
    with open('ui.py', 'w') as f:
        f.write(modified_content)
    
    print('Updated draw_cards method with power-up handling')
else:
    print('Could not find draw_cards method')
