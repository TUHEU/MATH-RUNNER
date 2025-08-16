import pygame
import random
from sys import exit

pygame.init()
window = pygame.display.Info()
x = window.current_w
y = window.current_h
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
unitx = x / 1000
unity = y / 1000

# Screen state
current_screen = "menu"

# font
font1 = pygame.font.Font("Assets/Fonts/1.TTF", 50)

# animation variables
signs = ['+', '-', '/', '*']

# equation animation class
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
            cur_equation[i] = (self.generate_equation(signs))
            eqn_locx[i] = (random.randint(int(unitx * 100), int(x - (unitx * 200))))
            eqn_locy[i] = (random.randint(int(unity * 100), int(y - (unity * 150))))
            self.isactive = False
        return self.isactive

# button class
class button:
    def __init__(self, default_path, size, rect_pos, key=""):
        self.size = size
        self.default_img = pygame.image.load(default_path).convert_alpha()
        self.default_img = pygame.transform.scale(self.default_img, self.size)
        self.touched_img = pygame.transform.scale(self.default_img, (int(self.size[0] * .8), int(self.size[1] * .8)))
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

# buttons
buttons = [
    button("Assets/Buttons/Default/start.png", (x // 4, y // 8), ((x // 2) - int(unitx * 120), (y // 2) - int(unity * 300)), "start"),
    button("Assets/Buttons/Default/options.png", (x // 4, y // 8), ((x // 2) - int(unitx * 120), (y // 2) - int(unity * 150)), "options"),
    button("Assets/Buttons/Default/custom level.png", (x // 4, y // 8), ((x // 2) - int(unitx * 120), (y // 2) - int(unity)), "custom level"),
    button("Assets/Buttons/Default/exit.png", (x // 4, y // 8), ((x // 2) - int(unitx * 120), (y // 2) + int(unity * 150)), "exit")
]

# equations list
equations = [equationC() for _ in range(13)]

# sounds
pygame.mixer.init()
touch_sound = pygame.mixer.Sound("Assets/Sounds/touch.mp3")

# menu background
menu = pygame.image.load("Assets/Menu/menu.jpg")
menu_rect = menu.get_rect(topleft=(0, 0))
menu = pygame.transform.scale(menu, (x, y))

# equation storage
cur_equation = ["" for _ in range(13)]
eqn_locx = [0 for _ in range(13)]
eqn_locy = [0 for _ in range(13)]

# slideshow images
slideshow_images = [
    pygame.image.load("Assets/Backgrounds/1.png"),  # replace with actual filename
    pygame.image.load("Assets/Backgrounds/2.png"),   # replace with actual filename
    pygame.image.load("Assets/Backgrounds/3.png"),    # replace with actual filename
    pygame.image.load("Assets/Backgrounds/4.png")   # repeat first
]
slideshow_images = [pygame.transform.scale(img, (x, y)) for img in slideshow_images]
current_slide = 0
fade_alpha = 0
fade_speed = 200  # pixels per second
slide_timer = 0
slide_delay = 2000  # milliseconds to hold fully visible image

while True:
    dt = clock.tick(60)
    mouse = pygame.mouse.get_pos()
    kpressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()

        if current_screen == "menu":
            for button in buttons:
                action = button.handle_event(event, mouse)
                if action == "exit":
                    pygame.quit()
                    exit()
                elif action == "start":
                    current_screen = "slideshow"
                    current_slide = 0
                    fade_alpha = 0
                    slide_timer = 0

    if current_screen == "menu":
        screen.blit(menu, menu_rect)
        j = 0
        for i, equ in enumerate(equations):
            wait = random.randint(400, 800)
            if not equ.active(wait, dt, cur_equation, eqn_locx, eqn_locy, i):
                if j < 13:
                    cur_equation[i] = equ.generate_equation(signs)
                    eqn_locx[i] = random.randint(int(unitx * 100), int(x - (unitx * 100)))
                    eqn_locy[i] = random.randint(int(unity * 100), int(y - (unity * 100)))
            j += 1
        for button in buttons:
            button.draw(screen)

    elif current_screen == "slideshow":
        # Draw current image with fade
        img = slideshow_images[current_slide].copy()
        img.set_alpha(fade_alpha)
        screen.blit(img, (0, 0))

        fade_alpha += fade_speed * (dt / 1000)
        if fade_alpha >= 255:
            fade_alpha = 255
            slide_timer += dt
            if slide_timer >= slide_delay:
                current_slide += 1
                if current_slide >= len(slideshow_images):
                    current_screen = "menu"
                else:
                    fade_alpha = 0
                    slide_timer = 0

    pygame.display.update()
