with open('ui.py', 'r') as f:
    lines = f.readlines()

# Find the problematic line
for i, line in enumerate(lines):
    if '    def"""' in line:
        # Fix the indentation
        lines[i] = '    def draw_game_state(self, game):\n        """Draw the game state indicator."""\n'
        break

# Write the fixed content back
with open('ui.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation error in ui.py')
