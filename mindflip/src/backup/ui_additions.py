"""
Additional UI functions for MindFlip: Memory Arcade
"""

import pygame
from mindflip.src.config import TEXT_COLOR, SCORE_COLOR

def draw_combo(self, game):
    """
    Draw the combo indicator.
    
    Args:
        game: The game state object
    """
    if game.combo_count > 0:
        multiplier = game.get_combo_multiplier()
        combo_text = self.hud_font.render(f"Combo: x{game.combo_count} ({multiplier:.1f}x)", True, SCORE_COLOR)
        self.surface.blit(combo_text, (20, 110))

def handle_text_size_buttons(self, event, game):
    """
    Handle clicks on text size buttons.
    
    Args:
        event: The pygame event
        game: The game state object
        
    Returns:
        bool: True if text size was changed
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        
        # Check small text button
        if self.text_size_buttons[0].check_hover(pos):
            game.set_text_size(0.8)  # Small
            self.update_fonts(0.8)
            return True
            
        # Check medium text button
        elif self.text_size_buttons[1].check_hover(pos):
            game.set_text_size(1.0)  # Medium (default)
            self.update_fonts(1.0)
            return True
            
        # Check large text button
        elif self.text_size_buttons[2].check_hover(pos):
            game.set_text_size(1.2)  # Large
            self.update_fonts(1.2)
            return True
            
    return False
