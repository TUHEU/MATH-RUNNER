import pygame
import random
# Enemy class with multiple types
class Enemy:
    def __init__(self, x, y, enemy_type=1):
        # Define properties per type
        if enemy_type == 1:
            self.width, self.height = 40, 60
            self.color = (0, 0, 0)
            self.speed = 5
        elif enemy_type == 2:
            self.width, self.height = 60, 80
            self.color = (50, 0, 150)
            self.speed = 3
        elif enemy_type == 3:
            self.width, self.height = 30, 50
            self.color = (150, 0, 0)
            self.speed = 7

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.max_death_time = 15  # frames

    def update(self):
        if self.alive and not self.dying:
            self.rect.x -= self.speed
        elif self.dying:
            self.death_timer += 1
            if self.death_timer >= self.max_death_time:
                self.alive = False
                self.dying = False

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
        elif self.dying:
            alpha = max(0, 255 - int((self.death_timer/self.max_death_time)*255))
            death_surface = pygame.Surface((self.rect.width, self.rect.height))
            death_surface.fill((255,0,0))
            death_surface.set_alpha(alpha)
            surface.blit(death_surface, (self.rect.x, self.rect.y))

    def die(self):
        self.dying = True
        self.death_timer = 0

# Spawn enemies randomly with different types
if random.randint(0, 100) < 2:
    enemy_y = screen_height - 100
    enemy_type = random.choice([1, 2, 3])
    enemies.append(Enemy(screen_width, enemy_y, enemy_type))
