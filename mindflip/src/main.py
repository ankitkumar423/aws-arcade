"""
Main game loop for MindFlip: Memory Arcade
"""

import sys
import pygame
from mindflip.src.game import Game
from mindflip.src.ui import UI
from mindflip.src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, GAME_TITLE, 
    MATCH_POINTS, LEVEL_BONUS,
    TEXT_SIZE_SMALL, TEXT_SIZE_MEDIUM, TEXT_SIZE_LARGE
)

def main():
    """Main entry point for the game."""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    # Create game objects
    game = Game()
    ui = UI()
    
    # Game state
    game_started = False
    running = True
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if not game_started:
                    # Start game on Enter press from splash screen
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game_started = True
                        ui.show_toast("Game started! Find matching pairs")
                else:
                    # Game controls
                    if event.key == pygame.K_UP:
                        game.move_cursor('up')
                    elif event.key == pygame.K_DOWN:
                        game.move_cursor('down')
                    elif event.key == pygame.K_LEFT:
                        game.move_cursor('left')
                    elif event.key == pygame.K_RIGHT:
                        game.move_cursor('right')
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if game.flip_card():
                            # Show appropriate toast messages based on game state
                            if game.game_state == game.STATE_SECOND_CARD:
                                ui.show_toast("Find a matching card!")
                            elif game.game_state == game.STATE_DELAY:
                                if game.first_card.value == game.second_card.value:
                                    # Show combo message if applicable
                                    if game.combo_count > 1:
                                        multiplier = game.get_combo_multiplier()
                                        points = int(MATCH_POINTS * multiplier)
                                        ui.show_toast(f"Match found! +{points} points (Combo x{game.combo_count})")
                                    else:
                                        ui.show_toast(f"Match found! +{MATCH_POINTS} points")
                                else:
                                    ui.show_toast("Not a match! Try again")
                    elif event.key == pygame.K_r:
                        game.reset()
                        ui.show_toast("Game reset! Starting from level 1")
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_d:
                        # Toggle debug mode
                        debug_on = game.toggle_debug_mode()
                        ui.show_toast(f"Debug mode {'enabled' if debug_on else 'disabled'}")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        # Return to main menu
                        game_started = False
                        game.reset()  # Reset the game state
                        ui.show_toast("Returned to main menu")
            
            # Handle splash screen button events
            if not game_started:
                if ui.handle_splash_events(event, game):
                    # Debug mode was toggled, update UI
                    pass
            else:
                # Handle game screen events (info icons)
                ui.handle_game_events(event)
                
                # Handle text size button clicks
                if ui.handle_text_size_buttons(event, game):
                    size_name = "Small" if game.text_size == TEXT_SIZE_SMALL else "Large" if game.text_size == TEXT_SIZE_LARGE else "Medium"
                    ui.show_toast(f"Text size: {size_name}")
                
                # Check for back button click
                if event.type == pygame.MOUSEBUTTONDOWN and ui.back_button.check_hover(pygame.mouse.get_pos()):
                    game_started = False
                    game.reset()  # Reset the game state
                    ui.show_toast("Returned to main menu")
        
        # Update mouse position for button hover effects
        mouse_pos = pygame.mouse.get_pos()
        if not game_started:
            ui.debug_button.check_hover(mouse_pos)
            ui.rules_icon.check_hover(mouse_pos)
            ui.points_icon.check_hover(mouse_pos)
        else:
            # Check icon hovers during gameplay
            ui.rules_icon.check_hover(mouse_pos)
            ui.points_icon.check_hover(mouse_pos)
            ui.back_button.check_hover(mouse_pos)
            
            # Check text size buttons
            for button in ui.text_size_buttons:
                button.check_hover(mouse_pos)
        
        # Update game state
        if game_started:
            updates = game.update()
            
            # Show toast messages for game events
            if updates['level_complete']:
                ui.show_toast(f"Level {game.level-1} complete! Moving to level {game.level}")
            elif updates['game_over']:
                ui.show_toast("Game over! Press R to restart")
            elif updates['extra_life']:
                ui.show_toast("Extra life awarded! ♥")
        
        # Render
        if not game_started:
            ui.draw_splash_screen(screen, game.debug_mode)
        else:
            ui.draw_game(game, screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
