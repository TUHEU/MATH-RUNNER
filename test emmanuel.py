# ... (Keep all imports and existing classes same as commit 14)

# Initialize player health
player_health = 100
max_health = 100
health_bar_width = 200
health_bar_height = 20

# Function to draw health bar
def draw_health_bar(surface, x, y, health, max_health):
    # Background bar
    pygame.draw.rect(surface, (255,0,0), (x, y, health_bar_width, health_bar_height))
    # Current health
    current_width = int((health / max_health) * health_bar_width)
    pygame.draw.rect(surface, (0,255,0), (x, y, current_width, health_bar_height))
    # Border
    pygame.draw.rect(surface, (0,0,0), (x, y, health_bar_width, health_bar_height), 2)
