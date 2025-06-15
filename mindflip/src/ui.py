"""
UI rendering for MindFlip: Memory Arcade
"""

import pygame
import time
import math
import random
from mindflip.src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN,
    CARD_BACK_COLOR, CARD_FRONT_COLOR, CARD_HIGHLIGHT_COLOR, CARD_MATCHED_COLOR,
    BACKGROUND_COLOR, TEXT_COLOR, TITLE_COLOR, SCORE_COLOR, LIVES_COLOR,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, ICON_COLOR, ICON_HOVER_COLOR,
    DEBUG_MODE, LEVEL_BONUS, ANIMATE_BACKGROUND, BACKGROUND_ANIMATION_SPEED,
    GAME_RULES, POINTS_SYSTEM
)

class Button:
    """A simple button class for UI interactions."""
    
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False
    
    def draw(self, surface):
        """Draw the button on the given surface."""
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2)  # Border
        
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        """Check if mouse position is over the button."""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def handle_event(self, event):
        """Handle mouse events on the button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action()
        return False

class Icon:
    """An icon that can show a tooltip when hovered."""
    
    def __init__(self, x, y, radius, symbol, font, tooltip_lines):
        self.x = x
        self.y = y
        self.radius = radius
        self.symbol = symbol
        self.font = font
        self.tooltip_lines = tooltip_lines
        self.hovered = False
    
    def draw(self, surface):
        """Draw the icon on the given surface."""
        color = ICON_HOVER_COLOR if self.hovered else ICON_COLOR
        
        # Draw circle
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, TEXT_COLOR, (self.x, self.y), self.radius, 2)  # Border
        
        # Draw symbol
        symbol_surf = self.font.render(self.symbol, True, TEXT_COLOR)
        symbol_rect = symbol_surf.get_rect(center=(self.x, self.y))
        surface.blit(symbol_surf, symbol_rect)
    
    def draw_tooltip(self, surface):
        """Draw the tooltip if icon is hovered."""
        if not self.hovered:
            return
            
        # Calculate tooltip dimensions
        line_height = 22
        padding = 10
        width = 300
        height = len(self.tooltip_lines) * line_height + padding * 2
        
        # Position tooltip to not go off screen
        x = min(self.x + 10, WINDOW_WIDTH - width - 10)
        y = min(self.y + 10, WINDOW_HEIGHT - height - 10)
        
        # Draw tooltip background
        tooltip_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        tooltip_surface.fill((0, 0, 0, 220))  # Semi-transparent black
        pygame.draw.rect(tooltip_surface, TEXT_COLOR, (0, 0, width, height), 2)  # Border
        
        # Draw tooltip text
        for i, line in enumerate(self.tooltip_lines):
            text_surf = self.font.render(line, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(x=padding, y=padding + i * line_height)
            tooltip_surface.blit(text_surf, text_rect)
        
        # Draw tooltip
        surface.blit(tooltip_surface, (x, y))
    
    def check_hover(self, pos):
        """Check if mouse position is over the icon."""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        self.hovered = (dx*dx + dy*dy) <= (self.radius * self.radius)
        return self.hovered

class UI:
    """
    Handles all rendering and UI elements for the game.
    """
    
    def __init__(self):
        """Initialize the UI system."""
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.hud_font = pygame.font.SysFont('Arial', 24)
        self.card_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.debug_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.message_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.state_font = pygame.font.SysFont('Arial', 18)
        self.icon_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        # Create the main surface
        self.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Animation variables
        self.match_flash_time = 0
        self.show_match_flash = False
        self.animation_time = 0
        self.stars = []
        
        # Initialize stars for background animation
        self.stars = []
        for _ in range(100):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            size = random.uniform(0.5, 2.0)
            speed = random.uniform(0.2, 1.0)
            self.stars.append((x, y, size, speed))
        
        # Toast message system
        self.toast_message = None
        self.toast_time = 0
        self.toast_duration = 2.0  # seconds
        
        # Create buttons for splash screen
        self.debug_button = Button(
            WINDOW_WIDTH - 120, 
            WINDOW_HEIGHT - 40, 
            110, 30, 
            "Debug: OFF", 
            self.debug_font
        )
        
        # Create back button for game screen
        self.back_button = Button(
            20, 
            20, 
            80, 30, 
            "Menu", 
            self.debug_font
        )
        
        # Create text size buttons
        self.text_size_buttons = [
            Button(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 40, 50, 30, "A-", self.debug_font),
            Button(WINDOW_WIDTH - 140, WINDOW_HEIGHT - 40, 50, 30, "A", self.debug_font),
            Button(WINDOW_WIDTH - 80, WINDOW_HEIGHT - 40, 50, 30, "A+", self.debug_font)
        ]
        
        # Create info icons
        self.rules_icon = Icon(
            WINDOW_WIDTH - 60, 
            40, 
            15, 
            "?", 
            self.icon_font,
            GAME_RULES
        )
        
        self.points_icon = Icon(
            WINDOW_WIDTH - 30, 
            40, 
            15, 
            "$", 
            self.icon_font,
            POINTS_SYSTEM
        )
    
    def update_fonts(self, text_size):
        """Update font sizes based on text size setting."""
        self.title_font = pygame.font.SysFont('Arial', int(36 * text_size), bold=True)
        self.hud_font = pygame.font.SysFont('Arial', int(24 * text_size), bold=True)
        self.card_font = pygame.font.SysFont('Arial', int(32 * text_size), bold=True)
        self.debug_font = pygame.font.SysFont('Arial', int(16 * text_size), bold=True)
        self.message_font = pygame.font.SysFont('Arial', int(48 * text_size), bold=True)
        self.state_font = pygame.font.SysFont('Arial', int(18 * text_size), bold=True)
        self.icon_font = pygame.font.SysFont('Arial', int(18 * text_size), bold=True)
    
    def draw_animated_background(self):
        """Draw an animated starfield background."""
        if not ANIMATE_BACKGROUND:
            self.surface.fill(BACKGROUND_COLOR)
            return
            
        # Fill with dark background
        self.surface.fill((20, 20, 40))
        
        # Update animation time
        self.animation_time += 0.01 * BACKGROUND_ANIMATION_SPEED
        
        # Draw stars
        for i, (x, y, size, speed) in enumerate(self.stars):
            # Calculate star brightness based on time
            brightness = 128 + int(127 * math.sin(self.animation_time * speed))
            color = (brightness, brightness, brightness)
            
            # Draw star
            pygame.draw.circle(self.surface, color, (int(x), int(y)), size)
            
            # Move star slightly for animation
            new_x = x + speed * 0.2
            if new_x > WINDOW_WIDTH:
                new_x = 0
            self.stars[i] = (new_x, y, size, speed)
    
    def draw_game(self, game, screen):
        """
        Draw the complete game UI.
        
        Args:
            game: The game state object
            screen: The pygame screen to draw on
        """
        # Draw animated background
        self.draw_animated_background()
        
        # Draw title
        self.draw_title(game)
        
        # Draw back button
        self.back_button.draw(self.surface)
        
        # Draw info icons
        self.rules_icon.draw(self.surface)
        self.points_icon.draw(self.surface)
        
        # Draw tooltips if hovered
        self.rules_icon.draw_tooltip(self.surface)
        self.points_icon.draw_tooltip(self.surface)
        
        # Draw HUD (score, level, tries)
        self.draw_hud(game)
        
        # Draw card grid
        self.draw_cards(game)
        
        # Draw game state indicator (for better user feedback)
        self.draw_game_state(game)
        
        # Draw combo indicator
        self.draw_combo(game)
        
        # Draw controls info
        self.draw_controls()
        
        # Draw text size buttons
        for button in self.text_size_buttons:
            button.draw(self.surface)
        
        # Draw toast message if active
        self.draw_toast()
        
        # Draw level transition screen if in that state
        if game.game_state == game.STATE_LEVEL_COMPLETE:
            self.draw_level_transition(game)
        
        # Draw game over if needed
        if game.game_over:
            self.draw_game_over(game)
        
        # Draw to the screen
        screen.blit(self.surface, (0, 0))
    
    def draw_title(self, game=None):
        """
        Draw the game title and debug indicator if applicable.
        
        Args:
            game: Optional game state object to check debug mode
        """
        title = self.title_font.render("MIND FLIP", True, TITLE_COLOR)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=20)
        self.surface.blit(title, title_rect)
        
        # Add debug mode indicator if enabled
        if game and game.debug_mode:
            debug_text = self.debug_font.render("DEBUG MODE", True, (255, 100, 100))
            self.surface.blit(debug_text, (10, 10))
    
    def draw_hud(self, game):
        """
        Draw the heads-up display with game stats.
        
        Args:
            game: The game state object
        """
        # Draw level
        level_text = self.hud_font.render(f"Level: {game.level}", True, TEXT_COLOR)
        self.surface.blit(level_text, (WINDOW_WIDTH//2 - level_text.get_width()//2, 70))
        
        # Draw score
        score_text = self.hud_font.render(f"Score: {game.score}", True, SCORE_COLOR)
        self.surface.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 20, 70))
        
        # Draw tries/lives
        lives_text = self.hud_font.render("Lives: ", True, TEXT_COLOR)
        self.surface.blit(lives_text, (20, 70))
        
        # Draw heart symbols for lives
        heart_width = 25
        for i in range(game.tries):
            heart_x = 20 + lives_text.get_width() + (i * heart_width)
            pygame.draw.polygon(self.surface, LIVES_COLOR, [
                (heart_x, 80),
                (heart_x - 10, 70),
                (heart_x - 5, 65),
                (heart_x, 70),
                (heart_x + 5, 65),
                (heart_x + 10, 70)
            ])
    
    def draw_cards(self, game):
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
                value_text = card_font.render(str(card.value), True, (0, 0, 0))
                text_rect = value_text.get_rect(center=(x + card_width//2, y + card_height//2))
                self.surface.blit(value_text, text_rect)
            
            # In debug mode, also show small number in corner for face-down cards
            if game.debug_mode and not card.flipped and not card.matched:
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
    
    def draw_game_state(self, game):
        """
        Draw an indicator of the current game state for better user feedback.
        
        Args:
            game: The game state object
        """
        state_text = ""
        if game.game_state == game.STATE_FIRST_CARD:
            state_text = "Select first card"
        elif game.game_state == game.STATE_SECOND_CARD:
            state_text = "Select second card"
        elif game.game_state == game.STATE_DELAY:
            state_text = "Checking match..."
        
        if state_text:
            text = self.state_font.render(state_text, True, TEXT_COLOR)
            text_rect = text.get_rect(centerx=WINDOW_WIDTH//2, y=100)
            self.surface.blit(text, text_rect)
    
    def draw_combo(self, game):
        """Draw the combo indicator."""
        if game.combo_count > 0:
            multiplier = game.get_combo_multiplier()
            combo_text = self.hud_font.render(f"Combo: x{game.combo_count} ({multiplier:.1f}x)", True, SCORE_COLOR)
            self.surface.blit(combo_text, (20, 110))
    
    def draw_controls(self):
        """Draw the control instructions."""
        controls_text = self.state_font.render(
            "Controls: Arrows ←↑↓→ | Flip: Enter | Reset: R | Menu: ESC | Quit: Q", 
            True, TEXT_COLOR
        )
        controls_rect = controls_text.get_rect(
            centerx=WINDOW_WIDTH//2, 
            bottom=WINDOW_HEIGHT - 20
        )
        self.surface.blit(controls_text, controls_rect)
    
    def draw_toast(self):
        """Draw a toast message if one is active."""
        if self.toast_message:
            current_time = time.time()
            if current_time - self.toast_time < self.toast_duration:
                # Calculate alpha based on time remaining (fade out effect)
                time_left = self.toast_duration - (current_time - self.toast_time)
                alpha = min(255, int(time_left * 255 / (self.toast_duration / 2)))
                
                # Create toast background
                toast_surface = pygame.Surface((400, 40), pygame.SRCALPHA)
                toast_surface.fill((0, 0, 0, min(180, alpha)))
                
                # Create toast text
                toast_text = self.hud_font.render(self.toast_message, True, (255, 255, 255, alpha))
                text_rect = toast_text.get_rect(center=(200, 20))
                toast_surface.blit(toast_text, text_rect)
                
                # Draw toast at bottom center
                self.surface.blit(toast_surface, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT - 80))
            else:
                self.toast_message = None
    
    def show_toast(self, message):
        """
        Show a toast message at the bottom of the screen.
        
        Args:
            message: The message to display
        """
        self.toast_message = message
        self.toast_time = time.time()
    
    def draw_level_transition(self, game):
        """
        Draw the level transition screen.
        
        Args:
            game: The game state object
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with alpha
        self.surface.blit(overlay, (0, 0))
        
        # Level complete text
        level_text = self.message_font.render(f"LEVEL {game.level} COMPLETED!", True, (100, 255, 100))
        level_rect = level_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 - 70)
        self.surface.blit(level_text, level_rect)
        
        # Points earned
        points_text = self.hud_font.render(f"Points Earned: {game.points_earned_this_level}", True, SCORE_COLOR)
        points_rect = points_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2)
        self.surface.blit(points_text, points_rect)
        
        # Level bonus
        bonus_text = self.hud_font.render(f"Level Bonus: {LEVEL_BONUS * game.level}", True, SCORE_COLOR)
        bonus_rect = bonus_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 30)
        self.surface.blit(bonus_text, bonus_rect)
        
        # Next level text
        next_text = self.hud_font.render(f"Level {game.level + 1} Unlocked!", True, TEXT_COLOR)
        next_rect = next_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 70)
        self.surface.blit(next_text, next_rect)
        
        # Extra life notification if applicable
        if game.level % 2 == 0:  # Every 2 levels
            life_text = self.hud_font.render("Extra Life Awarded! ♥", True, LIVES_COLOR)
            life_rect = life_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 110)
            self.surface.blit(life_text, life_rect)
    
    def draw_game_over(self, game):
        """
        Draw the game over screen.
        
        Args:
            game: The game state object
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha
        self.surface.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.message_font.render("GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 - 70)
        self.surface.blit(game_over_text, game_over_rect)
        
        # Score text
        score_text = self.hud_font.render(f"Final Score: {game.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 - 10)
        self.surface.blit(score_text, score_rect)
        
        # Level reached
        level_text = self.hud_font.render(f"Level Reached: {game.level}", True, TEXT_COLOR)
        level_rect = level_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 20)
        self.surface.blit(level_text, level_rect)
        
        # High score text (only if not in debug mode)
        if not game.debug_mode:
            high_score_text = self.hud_font.render(f"High Score: {game.high_score}", True, SCORE_COLOR)
            high_score_rect = high_score_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 50)
            self.surface.blit(high_score_text, high_score_rect)
        else:
            debug_note = self.hud_font.render("(Debug Mode: High Score Not Saved)", True, (255, 100, 100))
            debug_rect = debug_note.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 50)
            self.surface.blit(debug_note, debug_rect)
        
        # Restart instructions
        restart_text = self.hud_font.render("Press R to restart or Q to quit", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 100)
        self.surface.blit(restart_text, restart_rect)
    
    def draw_splash_screen(self, screen, debug_mode=False):
        """
        Draw the initial splash screen.
        
        Args:
            screen: The pygame screen to draw on
            debug_mode: Current debug mode state
        """
        # Draw animated background
        self.draw_animated_background()
        
        # Title
        title = self.title_font.render("MIND FLIP: MEMORY ARCADE", True, TITLE_COLOR)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 - 120)
        self.surface.blit(title, title_rect)
        
        # Game description
        desc_text = self.hud_font.render("Match pairs of cards before running out of lives!", True, TEXT_COLOR)
        desc_rect = desc_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 - 60)
        self.surface.blit(desc_text, desc_rect)
        
        # Start instruction
        start_text = self.hud_font.render("Press ENTER to Start", True, TEXT_COLOR)
        start_rect = start_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 20)
        self.surface.blit(start_text, start_rect)
        
        # Controls info
        controls_text = self.state_font.render("Use arrow keys to navigate, Enter to flip cards", True, TEXT_COLOR)
        controls_rect = controls_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//2 + 60)
        self.surface.blit(controls_text, controls_rect)
        
        # Update debug button text based on current state
        self.debug_button.text = "Debug: " + ("ON" if debug_mode else "OFF")
        
        # Draw debug mode button
        self.debug_button.draw(self.surface)
        
        # Draw info icons
        self.rules_icon.draw(self.surface)
        self.points_icon.draw(self.surface)
        
        # Draw tooltips if hovered
        self.rules_icon.draw_tooltip(self.surface)
        self.points_icon.draw_tooltip(self.surface)
        
        # Draw to the screen
        screen.blit(self.surface, (0, 0))
    
    def handle_splash_events(self, event, game):
        """
        Handle events on the splash screen.
        
        Args:
            event: The pygame event
            game: The game state object
            
        Returns:
            bool: True if debug mode was toggled
        """
        if event.type == pygame.MOUSEMOTION:
            self.debug_button.check_hover(event.pos)
            self.rules_icon.check_hover(event.pos)
            self.points_icon.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.debug_button.hovered:
                game.toggle_debug_mode()
                return True
        return False
    
    def handle_game_events(self, event):
        """
        Handle events during gameplay.
        
        Args:
            event: The pygame event
        """
        if event.type == pygame.MOUSEMOTION:
            self.rules_icon.check_hover(event.pos)
            self.points_icon.check_hover(event.pos)
    
    def handle_text_size_buttons(self, event, game):
        """Handle clicks on text size buttons."""
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
