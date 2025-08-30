import pygame
import random
from sys import exit
import threading  # For running other background tasks if needed

pygame.init()
window = pygame.display.Info()
x = window.current_w
y = window.current_h
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
unitx = x / 1000
unity = y / 1000

# Pages booleans
menu_scrn = True
start_scrn = False
question_scrn = False
paused = False  # NEW: Pause flag

# Font
font1 = pygame.font.Font("Assets/Fonts/1.TTF", 50)

# Physics variables
player_vel_y = 0
gravity = 1 * unity
jump_strength = -30 * unity

# Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x, y))
fade_surface.fill((0, 0, 0))
fade_surface.set_alpha(0)
alpha = 0

# Player variables
framesize = (1.7 * unitx, 2.6 * unity)
immortal = False
immortaltime = 0
playerattack = False
playerinjure = False

# Enemies variables
framesizeE = (.3 * unitx, .6 * unity)
Enemydead = False
enemyattack = False

# Animation variables
signs = ['+', '-', '/', '*']

# Backgrounds variables
sizebk = (7000 * unitx, y)
speedbk = 4 * unitx
k = 0

# Floor variables
l = 0
sizefl = (21000 * unitx, 200 * unity)
speedfl = 12 * unitx

# Ground position
ground = y - (200 * unity)
onground = True

# --- Frame Class ---
class Frame:
    def __init__(self, size, path, pos=(0, ground)):
        self.size = size
        self.path = path
        self.frameF = pygame.image.load(path).convert_alpha()
        self.frameF = pygame.transform.scale(self.frameF, (self.frameF.get_width() * size[0], self.frameF.get_height() * size[1]))
        self.frameB = pygame.transform.flip(self.frameF, 1, 0)
        self.rect = self.frameF.get_rect(bottomleft=pos)

# --- Background Class ---
class background:
    def __init__(self, path, speed, size):
        self.size = size
        self.speed = speed
        self.path = path
        self.img = pygame.image.load(path).convert_alpha()
        self.img = pygame.transform.scale(self.img, (size[0], size[1]))
        self.rect = self.img.get_rect(bottomleft=(0, y))
    def move(self, front):
        if front:
            self.rect.left -= self.speed
        else:
            self.rect.left += self.speed

# --- Equation Class ---
class equationC:
    def __init__(self, eqaution="", sign="", ans=0, isactive=False, delay=0):
        self.equation = eqaution
        self.isactive = isactive
        self.sign = sign
        self.ans = ans
        self.delay = delay
    def generate_equation(self, signs):
        self.equation = str(random.randint(1, 50)) + signs[random.randint(0, 3)] + str(random.randint(1, 50))
        self.ans = str(int(eval(self.equation)))
        self.delay = 0
        self.equation = self.equation + "=" + self.ans
        return self.equation
    def active(self, wait, dt, cur_equation, eqn_locx, eqn_locy, i):
        if self.delay < wait:
            equationText = font1.render(f"{cur_equation[i]}", True, "Black")
            screen.blit(equationText, (eqn_locx[i], eqn_locy[i]))
            self.delay += dt
            self.isactive = True
        else:
            cur_equation[i] = self.generate_equation(signs)
            eqn_locx[i] = (random.randint(int(unitx * 100), int(x - (unitx * 200))))
            eqn_locy[i] = (random.randint(int(unity * 100), int(y - (unity * 150))))
            self.isactive = False
        return self.isactive

# --- Button Class ---
class button:
    def __init__(self, default_path, size, rect_pos, key=""):
        self.size = size
        self.default_img = pygame.image.load(default_path).convert_alpha()
        self.default_img = pygame.transform.scale(self.default_img, self.size)
        self.touched_img = pygame.transform.scale(self.default_img, (int(self.size[0] * 0.8), int(self.size[1] * 0.8)))
        self.rect = self.default_img.get_rect(topleft=rect_pos)
        self.touched = False
        self.touching = True
        self.key = key
    def draw(self, screen):
        if self.touched:
            img = self.touched_img
        else:
            img = self.default_img
        screen.blit(img, self.rect)
    def handle_event(self, event, mouse_pos):
        self.touched = self.rect.collidepoint(mouse_pos)
        if self.touched and self.touching:
            touch_sound.play()
        self.touching = False
        if not self.touched:
            self.touching = True
        if self.touched and event.type == pygame.MOUSEBUTTONDOWN:
            return self.key
        return None

# Buttons list
buttons = [
    button("Assets/Buttons/Default/start.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity * 300)), "start"),
    button("Assets/Buttons/Default/options.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity * 150)), "options"),
    button("Assets/Buttons/Default/custom level.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity)), "custom level"),
    button("Assets/Buttons/Default/exit.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) + (unity * 150)), "exit")
]

# Equations list
equations = [equationC() for _ in range(13)]

# Background and floor lists
backgrounds = [background(f"Assets/Backgrounds/{i}.png", speedbk, sizebk) for i in range(1, 5)]
floors = [background(f"Assets/Floor/{i}.png", speedfl, sizefl) for i in range(1, 3)]

# Question board
board = Frame((unitx * .8, unity * 1.5), "Assets/Questions/board.png", (150 * unitx, 800 * unity))

# Sounds
pygame.mixer.init()
touch_sound = pygame.mixer.Sound("Assets/Sounds/touch.mp3")

# Menu background
menu = pygame.image.load("Assets/Menu/menu.jpg")
menu_rect = menu.get_rect(topleft=(0, 0))
menu = pygame.transform.scale(menu, (x, y))
j = 0
cur_equation = ["" for _ in range(13)]
eqn_locx = [0 for _ in range(13)]
eqn_locy = [0 for _ in range(13)]

# --- Dummy Player and Enemies ---
# Placeholders to allow running. (Assumes your full Animation & Enemy classes are defined above)
class Animation:
    def __init__(self):
        self.playerrect = pygame.Rect(100, ground, 50, 100)
        self.playersuf = pygame.Surface((50, 100))
        self.index = 0

player = Animation()

# Main Loop
while True:
    dt = clock.tick(60)
    mouse = pygame.mouse.get_pos()
    kpressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # Toggle pause

    screen.blit(menu, menu_rect)

    if menu_scrn and not paused:
        i = 0
        for equ in equations:
            wait = random.randint(400, 800)
            if not equ.active(wait, dt, cur_equation, eqn_locx, eqn_locy, i):
                if j < 13:
                    cur_equation[i] = equ.generate_equation(signs)
                    eqn_locx[i] = (random.randint(int(unitx * 100), int(x - (unitx * 100))))
                    eqn_locy[i] = (random.randint(int(unity * 100), int(y - (unity * 100))))
            i += 1
            j += 1
        for btn in buttons:
            btn.draw(screen)
            action = btn.handle_event(event, mouse)
            if action == "exit":
                pygame.quit()
                exit()
            if action == "start":
                menu_scrn = False
                start_scrn = True

    if paused:
        pause_text = font1.render("GAME PAUSED - Press SPACE to Resume", True, "Red")
        screen.blit(pause_text, (x / 2 - 300, y / 2))

    pygame.display.update()
