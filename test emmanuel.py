

# Player class update
class Player:
    def __init__(self, x, y, width=50, height=80):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 100, 200)
        self.attacking = False
        self.attack_cooldown = 1000  # milliseconds
        self.last_attack_time = 0

    def attack(self, current_time):
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attacking = True
            self.last_attack_time = current_time

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

        # Draw attack cooldown bar
        cooldown_ratio = min((pygame.time.get_ticks() - self.last_attack_time) / self.attack_cooldown, 1)
        bar_width = self.rect.width
        bar_height = 5
        cooldown_color = (0, 255, 0) if cooldown_ratio >= 1 else (255, 0, 0)
        pygame.draw.rect(surface, cooldown_color, (self.rect.x, self.rect.y - 10, bar_width * cooldown_ratio, bar_height))
