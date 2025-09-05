# main.py
# Math Runner Game - Initial setup
# Commit #2: Add imports and initialize Pygame window

import pygame
import random
import textwrap
from sys import exit

# Initialize pygame
pygame.init()

# Get display info (full screen dimensions)
window = pygame.display.Info()
x = window.current_w
y = window.current_h

# Create main screen
screen = pygame.display.set_mode((x, y))
pygame.display.set_caption("Math Runner")

# Create clock for FPS control
clock = pygame.time.Clock()

# Scaling units based on resolution
unitx = x / 1000
unity = y / 1000

# Basic game loop (empty for now)
def main():
    running = True
    while running:
        # Limit to 60 FPS
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Fill screen with black
        screen.fill((0, 0, 0))

        # Update display
        pygame.display.update()

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
