import pygame
import random

# Enemy class with type support
class Enemy:
    def __init__(self, enemy_type=1):
        self.enemy_type = enemy_type
        self.width = 50
        self.height = 80
        self.rect = pygame.Rect(screen_width + random.randint(50, 300),
                                screen_height - self.height - 50,
                                self.width, self.height)
        self.speed = random.choice([3, 4, 5]) if enemy_type==1 else random.choice([2,3,4])
        self.color = (255, 0, 0) if enemy_type==1 else (0, 255, 0) if enemy_type==2 else (0,0,255)
        self.alive = True
        self.dying = False

    def update(self, dt):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.left = screen_width + random.randint(50, 200)
            self.speed = random.randint(2,5)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
