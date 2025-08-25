
# ... (Keep all imports and existing classes same as commit 15)

# Enemy respawn delay (in milliseconds)
respawn_delay = 3000  # 3 seconds

# Update Enemy class to handle respawn
class Enemy:
    def __init__(self, x, y, enemy_type=1):
        # Existing initialization code ...
        self.alive = True
        self.dying = False
        self.respawn_timer = 0

    def update(self, dt):
        if self.alive and not self.dying:
            self.rect.x -= self.speed
        elif self.dying:
            self.respawn_timer += dt
            if self.respawn_timer >= respawn_delay:
                self.respawn()

    def die(self):
        self.dying = True
        self.alive = False
        self.respawn_timer = 0

    def respawn(self):
        self.dying = False
        self.alive = True
        self.rect.x = screen_width + random.randint(50, 200)
        self.rect.y = screen_height - self.height - 50
        self.respawn_timer = 0
        # Optionally randomize type or speed on respawn
        self.speed = random.choice([3, 5, 7])
