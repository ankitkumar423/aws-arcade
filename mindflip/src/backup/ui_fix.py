with open('ui.py', 'r') as f:
    content = f.read()

# Find the problematic line
if '    def"""' in content:
    # Replace it with a proper function definition
    fixed_content = content.replace('    def"""', '    def draw_game_state(self, game):\n        """')
    
    with open('ui.py', 'w') as f:
        f.write(fixed_content)
    
    print('Fixed function definition in ui.py')
else:
    print('Could not find the problematic line')
