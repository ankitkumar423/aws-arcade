"""
Card class for MindFlip: Memory Arcade
"""

class Card:
    """
    Represents a single card in the memory game.
    
    Attributes:
        value (int): The value/identifier of the card (used for matching)
        row (int): Row position in the grid
        col (int): Column position in the grid
        flipped (bool): Whether the card is currently face up
        matched (bool): Whether the card has been matched
    """
    
    def __init__(self, value, row, col):
        """
        Initialize a new card.
        
        Args:
            value (int): The value/identifier of the card
            row (int): Row position in the grid
            col (int): Column position in the grid
        """
        self.value = value
        self.row = row
        self.col = col
        self.flipped = False
        self.matched = False
    
    def flip(self):
        """Toggle the flipped state of the card if not already matched."""
        if not self.matched:
            self.flipped = not self.flipped
            return True
        return False
    
    def mark_matched(self):
        """Mark this card as matched."""
        self.matched = True
        self.flipped = True
    
    def reset(self):
        """Reset the card to its initial state."""
        self.flipped = False
        self.matched = False
    
    def __eq__(self, other):
        """
        Compare cards for equality based on their value.
        
        Args:
            other (Card): Another card to compare with
            
        Returns:
            bool: True if the cards have the same value
        """
        if isinstance(other, Card):
            return self.value == other.value
        return False
    
    def __repr__(self):
        """String representation of the card."""
        status = "matched" if self.matched else ("flipped" if self.flipped else "hidden")
        return f"Card(value={self.value}, pos=({self.row},{self.col}), {status})"
