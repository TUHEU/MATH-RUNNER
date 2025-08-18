import pygame
import random
import os
from sys import exit

pygame.init()
window = pygame.display.Info()
x = window.current_w
y = window.current_h
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
unitx = x / 1000
unity = y / 1000

# Game states
class GameState:
    MENU = 0
    PLAYING = 1
    TRANSITION = 2

current_state = GameState.MENU
transition_alpha = 0

# Setup asset folders
def load_image(path, size):
    img = pygame.image.load(os.path.join('Assets', path)).convert_alpha()
    return pygame.transform.scale(img, size)

#pages booleans
menu_scrn = True
start_scrn = False

#font
font1 = pygame.font.Font("Assets/Fonts/1.TTF", 50)

#physics variables
player_vel_y = 0
gravity = 1 * unity
jump_strength = -25 * unity

#Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x, y))
fade_surface.fill((0, 0, 0))
fade_surface.set_alpha(0)
alpha = 0

#player variables
framesize = (1.7 * unitx, 2.6 * unity)

#animation variables
signs = ['+', '-', '/', '*']

#backgrounds variables
sizebk = (7000 * unitx, y)
speedbk = 4 * unitx
k = 0

#floor variables
l = 0
sizefl = (21000 * unitx, 200 * unity)
speedfl = 12 * unitx

#animation variables
ground = y - (200 * unity)
onground = True

# Frame class
class Frame:
    def __init__(self, size, path):
        self.size = size
        self.path = path
        self.frameF = pygame.image.load(path).convert_alpha()
        self.frameF = pygame.transform.scale(self.frameF, (self.frameF.get_width() * size[0], self.frameF.get_height() * size[1]))
        self.frameB = pygame.transform.flip(self.frameF, 1, 0)
        self.rect = self.frameF.get_rect(bottomleft=(0, ground))

# Background class
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

# Equation class
class equationC:
    def __init__(self, equation="", sign="", ans=0, isactive=False, delay=0):
        self.equation = equation
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
            eqn_locx[i] = random.randint(int(unitx * 100), int(x - (unitx * 200)))
            eqn_locy[i] = random.randint(int(unity * 100), int(y - (unity * 150)))
            self.isactive = False
        return self.isactive

# Button class
class button:
    def __init__(self, default_path, size, rect_pos, key=""):
        self.size = size
        self.default_img = pygame.image.load(default_path).convert_alpha()
        self.default_img = pygame.transform.scale(self.default_img, self.size)
        self.touched_img = pygame.transform.scale(self.default_img, (self.size[0] * 0.8, self.size[1] * 0.8))
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

# Animation class
class Animation:
    def __init__(self, index=0, front=True, playersuf=player_idle[0].frameF, playerrect=player_idle[0].rect):
        self.index = index
        self.front = front
        self.playersuf = playersuf
        self.playerrect = playerrect
        self.vel_y = 0
    
    def createanimation(self, rect, onground, kpressed):
        if kpressed[pygame.K_d]:
            self.front = True
            self.playersuf = player_run[int(self.index)].frameF
            self.playerrect = self.playersuf.get_rect(bottomleft=rect)
            backgrounds[k].move(True)
            floors[l].move(True)
            if self.playerrect.right <= x - (unitx * 150):
                self.playerrect.left += 5
        
        elif kpressed[pygame.K_a]:
            self.front = False
            self.playersuf = player_run[int(self.index)].frameB
            self.playerrect = self.playersuf.get_rect(bottomleft=rect)
            if self.playerrect.left > x - 980 * unitx:
                backgrounds[k].move(False)
                floors[l].move(False)
                self.playerrect.left -= 5
        
        elif kpressed[pygame.K_s]:
            self.index -= 0.02
            self.index %= len(player_knee)
            if self.front:
                self.playersuf = player_knee[int(self.index)].frameF
            else:
                self.playersuf = player_knee[int(self.index)].frameB
            self.playerrect = self.playersuf.get_rect(bottomleft=rect)
        
        elif onground:
            if self.front:
                self.playersuf = player_idle[int(self.index)].frameF
            else:
                self.playersuf = player_idle[int(self.index)].frameB
            self.playerrect = self.playersuf.get_rect(bottomleft=rect)
        
        if kpressed[pygame.K_w] and onground:
            self.vel_y = jump_strength
            self.index = 0
            onground = False
            self.playerrect = player_jump[1].frameF.get_rect(bottomleft=rect)
        
        self.vel_y += gravity
        self.playerrect.bottom += self.vel_y
        
        if self.playerrect.bottom >= ground:
            self.playerrect.bottom = ground
            self.vel_y = 0
            onground = True
        
        if not onground:
            self.index += 0.07
            if self.index >= len(player_jump):
                self.index = 7
            if self.front:
                self.playersuf = player_jump[int(self.index)].frameF
            else:
                self.playersuf = player_jump[int(self.index)].frameB
        
        self.index += 0.1
        self.index %= len(player_run)
        return onground

# Menu class
class Menu:
    def __init__(self):
        self.buttons = [
            button("Assets/Buttons/Default/start.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - (unity * 300)), "start"),
            button("Assets/Buttons/Default/options.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - (unity * 150)), "options"),
            button("Assets/Buttons/Default/custom level.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - unity), "custom level"),
            button("Assets/Buttons/Default/exit.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) + (unity * 150)), "exit")
        ]
    
    def draw(self, screen):
        for button in self.buttons:
            button.draw(screen)

# Background system with transitions
class BackgroundSystem:
    def __init__(self):
        self.backgrounds = [
            background("Assets/Backgrounds/1.png", speedbk, sizebk),
            background("Assets/Backgrounds/2.png", speedbk, sizebk),
            background("Assets/Backgrounds/3.png", speedbk, sizebk),
            background("Assets/Backgrounds/4.png", speedbk, sizebk)
        ]
        self.current_bg = 0
        self.scroll = 0
    
    def update(self):
        self.scroll += 2
        if self.scroll > x:
            global current_state, transition_alpha
            current_state = GameState.TRANSITION
            transition_alpha = 0
            self.scroll = 0
    
    def draw(self, surface):
        surface.blit(self.backgrounds[self.current_bg].img, (-self.scroll, 0))
        surface.blit(self.backgrounds[(self.current_bg + 1) % len(self.backgrounds)].img, (x - self.scroll, 0))

# Initialize objects
buttons = [
    button("Assets/Buttons/Default/start.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - (unity * 300)), "start"),
    button("Assets/Buttons/Default/options.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - (unity * 150)), "options"),
    button("Assets/Buttons/Default/custom level.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) - unity), "custom level"),
    button("Assets/Buttons/Default/exit.png", (x/4, y/8), ((x/2) - (unitx * 120), (y/2) + (unity * 150)), "exit")
]

equations = [equationC() for _ in range(13)]
backgrounds = [
    background("Assets/Backgrounds/1.png", speedbk, sizebk),
    background("Assets/Backgrounds/2.png", speedbk, sizebk),
    background("Assets/Backgrounds/3.png", speedbk, sizebk),
    background("Assets/Backgrounds/4.png", speedbk, sizebk)
]

floors = [
    background("Assets/Floor/1.png", speedfl, sizefl),
    background("Assets/Floor/2.png", speedfl, sizefl)
]

# Player animations
player_run = [Frame(framesize, f"Assets/Player/run/{i}.png") for i in range(1, 9)]
player_jump = [Frame(framesize, f"Assets/Player/jump/{i}.png") for i in range(1, 9)]
player_idle = [Frame(framesize, f"Assets/Player/idle/{i}.png") for i in range(1, 9)]
player_shot = [Frame(framesize, f"Assets/Player/shot/{i}.png") for i in range(1, 14)]
player_hurt = [Frame(framesize, f"Assets/Player/hurt/{i}.png") for i in range(1, 4)]
player_death = [Frame(framesize, f"Assets/Player/death/{i}.png") for i in range(1, 6)]
player_knee = [Frame(framesize, f"Assets/Player/knee/{i}.png") for i in range(1, 3)]

# Sounds
pygame.mixer.init()
pygame.mixer.music.load('Assets/Sounds/touch.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.25)
touch_sound = pygame.mixer.Sound("Assets/Sounds/touch.mp3")

# Menu
menu_img = pygame.image.load("Assets/Menu/menu.jpg")
menu_rect = menu_img.get_rect(topleft=(0, 0))
menu_img = pygame.transform.scale(menu_img, (x, y))

# Game variables
j = 0
cur_equation = ["" for _ in range(13)]
eqn_locx = [0 for _ in range(13)]
eqn_locy = [0 for _ in range(13)]
player = Animation()
q = 600
menu = Menu()
bg_system = BackgroundSystem()

# Main game loop
while True:
    rect = player.playerrect.bottomleft
    if player.playerrect.bottom < q:
        q = player.playerrect.bottom
    
    dt = clock.tick(60)
    mouse = pygame.mouse.get_pos()
    testtext = font1.render(f"ply {q}  {unity}  {gravity} groun {ground} vbot {player.playerrect.bottom} ong {onground} b {backgrounds[k].rect.right}   mou{mouse}", False, "Black")
    kpressed = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        
        if current_state == GameState.MENU:
            for button in menu.buttons:
                result = button.handle_event(event, mouse)
                if result == "exit":
                    pygame.quit()
                    exit()
                elif result == "start":
                    current_state = GameState.PLAYING
    
    screen.blit(menu_img, menu_rect)
    
    # State updates
    if current_state == GameState.MENU:
        i = 0
        for equ in equations:
            wait = random.randint(400, 800)
            if not equ.active(wait, dt, cur_equation, eqn_locx, eqn_locy, i):
                if j < 13:
                    cur_equation[i] = equ.generate_equation(signs)
                    eqn_locx[i] = random.randint(int(unitx * 100), int(x - (unitx * 100)))
                    eqn_locy[i] = random.randint(int(unity * 100), int(y - (unity * 100)))
                    i += 1
                    j += 1
        
        menu.draw(screen)
    
    elif current_state == GameState.PLAYING:
        if backgrounds[k].rect.right >= x:
            screen.blit(backgrounds[k].img, backgrounds[k].rect)
            screen.blit(floors[l].img, floors[l].rect)
            onground = player.createanimation(rect, onground, kpressed)
            screen.blit(player.playersuf, player.playerrect)
            
            if backgrounds[k].rect.right <= x + 250 * unitx:
                fade_surface.set_alpha(alpha)
                alpha += 5
                screen.blit(fade_surface, (0, 0))
            else:
                backgrounds[k].rect.bottomleft = (0, y)
                floors[l].rect.bottomleft = (0, y)
                k += 1
                l += 1
                k %= 4
                l %= 2
                alpha = 0
                player.playerrect.left = 10 * unitx
        
        screen.blit(testtext, (10, 10))
    
    elif current_state == GameState.TRANSITION:
        transition_alpha += 5
        if transition_alpha >= 255:
            transition_alpha = 255
            player.rect.left = 0
            k = (k + 1) % len(backgrounds)
            current_state = GameState.PLAYING
        
        fade_surface.set_alpha(transition_alpha)
        screen.blit(fade_surface, (0, 0))
    
    pygame.display.update()
