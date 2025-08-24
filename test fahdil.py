import pygame
import random
from sys import exit

import cv2  # OpenCV for computer vision tasks
import numpy as np  # to handle arrays and matrices
from tensorflow.keras.models import load_model  # Keras for loading the pre-trained model
import threading  # For running emotion detection in a separate thread (simultaneous execution)

# --- EMOTION DETECTOR SETUP ---

# Load the pre-trained emotion recognition model
model = load_model("Assets/Emotion detection models/fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)

# List of emotions in the same order as the model's output neurons
Emotions_list = ['Angry', 'Disgust', 'Fear', 'Happy', 'Suprise', 'Sad', 'Neutral']

# Initialize webcam
cap = cv2.VideoCapture(0)

# Load face detection model (Caffe-based DNN)
net = cv2.dnn.readNetFromCaffe("Assets/Emotion detection models/dat.prototxt", "Assets/Emotion detection models/caffe.caffemodel")

# Input size expected by the emotion model
input_height, input_width = 64, 64

# Contrast Limited Adaptive Histogram Equalization (CLAHE) for enhancing faces
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Shared variable for storing detected emotion (default = Neutral)
current_emotion = "Neutral"

def emotion_loop():
    """Continuously reads frames from webcam, detects faces using Caffe DNN,
    preprocesses the face, and updates the global variable 'current_emotion'
    with the detected emotion."""
    global current_emotion
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (h, w) = gray.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

        net.setInput(blob)
        detections = net.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Extract the face ROI
                face_roi = gray[startY:endY, startX:endX]
                if face_roi.size == 0:
                    continue

                # Apply CLAHE to the face ROI
                face_roi = clahe.apply(face_roi)

                # Resize and normalize for the emotion model
                face_roi = cv2.resize(face_roi, (input_height, input_width))
                face_roi = face_roi.astype("float") / 255.0
                face_roi = np.expand_dims(face_roi, axis=0)
                face_roi = np.expand_dims(face_roi, axis=-1)

                # Predict emotion
                preds = model.predict(face_roi)[0]
                emotion_index = np.argmax(preds)
                current_emotion = Emotions_list[emotion_index]
                break  # Process only the first detected face


# Start emotion detection in background thread
# Normal (non-daemon) thread → the program will wait for it to finish before exiting.
# Daemon thread→ the program will not wait for it. When the main program ends, daemon threads are killed automatically.
threading.Thread(target=emotion_loop, daemon=True).start()

# --- PYGAME SETUP ---
pygame.init()
window = pygame.display.Info()
x = window.current_w
y = window.current_h
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
unitx = x / 1000
unity = y / 1000

# pages booleans
menu_scrn = True
start_scrn = False
pause_scrn = False  # New boolean for pause screen

# font
font1 = pygame.font.Font("Assets/Fonts/1.TTF", 50)

# physics variables
player_vel_y = 0
gravity = 1 * unity
jump_strength = -25 * unity

# Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x, y))
fade_surface.fill((0, 0, 0))
fade_surface.set_alpha(0)
alpha = 0

# player variables
framesize = (1.7 * unitx, 2.6 * unity)
framesizeE = (.3 * unitx, .6 * unity)

# animation variables
signs = ['+', '-', '/', '*']

# backgrounds variables
sizebk = (7000 * unitx, y)
speedbk = 4 * unitx
k = 0

# floor variables
l = 0
sizefl = (21000 * unitx, 200 * unity)
speedfl = 12 * unitx

# animation variables
ground = y - (200 * unity)
onground = True

# --- Frame class for player animations ---
class Frame:
    def __init__(self, size, path):
        self.size = size
        self.path = path
        self.frameF = pygame.image.load(path).convert_alpha()
        self.frameF = pygame.transform.scale(self.frameF, (self.frameF.get_width() * size[0], self.frameF.get_height() * size[1]))
        self.frameB = pygame.transform.flip(self.frameF, 1, 0)
        self.rect = self.frameF.get_rect(bottomleft=(0, ground))
        self.rectE1 = self.frameF.get_rect(bottomleft=(x, ground))

# --- Background class ---
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

# --- Equation class ---
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

    def active(self, wait, dt, cur_equation, eqn_locx, eqn_locy):
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

# --- Button class ---
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

# --- Enemy class ---
class Enemy:
    def __init__(self, index=0, enemysuf=None, enemyrect=None):
        self.index = index
        self.frontE = False
        self.enemysuf = enemysuf if enemysuf else enemy1_idle[0].frameF
        self.enemyrect = enemyrect if enemyrect else enemy1_idle[0].rectE1
        self.collide = False

    def createanimaion(self, rectE1):
        if self.index >= len(enemy1_Walk):
            self.index = 0
        if not self.frontE and not self.collide:
            self.enemysuf = enemy1_Walk[int(self.index)].frameB
            self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
            self.enemyrect.left -= 5
        elif self.frontE and not self.collide:
            self.front = False
            self.enemysuf = enemy1_Walk[int(self.index)].frameF
            self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
            self.enemyrect.left += 3 * unitx
        elif self.collide:
            if self.frontE:
                self.enemysuf = enemy1_idle[int(self.index)].frameF
            else:
                self.enemysuf = enemy1_idle[int(self.index)].frameB
            self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
        if self.enemyrect.left < 0:
            self.frontE = True
        if self.enemyrect.right >= x:
            self.frontE = False
        if player.playerrect.colliderect(self.enemyrect):
            self.collide = True
        self.index += 0.4

# --- Player Animation class ---
class Animation:
    def __init__(self, index=0, front=True, playersuf=None, playerrect=None):
        self.index = index
        self.front = front
        self.playersuf = playersuf if playersuf else player_idle[0].frameF
        self.playerrect = playerrect if playerrect else player_idle[0].rect
        self.vel_y = 0

    def createanimaion(self, rect, onground, kpressed):
        pass  # Placeholder, as the original code had an empty method.

# --- GAME ASSET INITIALIZATION ---

# button list
buttons = [
    button("Assets/Buttons/Default/start.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity * 300)), "start"),
    button("Assets/Buttons/Default/options.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity * 150)), "options"),
    button("Assets/Buttons/Default/custom level.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) - (unity)), "custom level"),
    button("Assets/Buttons/Default/exit.png", (x / 4, y / 8), ((x / 2) - (unitx * 120), (y / 2) + (unity * 150)), "exit")
]

# equations list
equations = [equationC() for _ in range(13)]
cur_equation = [""] * 13
eqn_locx = [0] * 13
eqn_locy = [0] * 13

# background list
backgrounds = [
    background("Assets/Backgrounds/1.png", speedbk, sizebk),
    background("Assets/Backgrounds/2.png", speedbk, sizebk),
    background("Assets/Backgrounds/3.png", speedbk, sizebk),
    background("Assets/Backgrounds/4.png", speedbk, sizebk),
]

# floor list
floors = [background("Assets/Floor/1.png", speedfl, sizefl), background("Assets/Floor/2.png", speedfl, sizefl)]

# player animations lists
player_run = [Frame(framesize, f"Assets/Player/run/{i}.png") for i in range(1, 9)]
player_jump = [Frame(framesize, f"Assets/Player/jump/{i}.png") for i in range(1, 9)]
player_idle = [Frame(framesize, f"Assets/Player/idle/{i}.png") for i in range(1, 9)]
player_shot = [Frame(framesize, f"Assets/Player/shot/{i}.png") for i in range(1, 15)]
player_hurt = [Frame(framesize, f"Assets/Player/hurt/{i}.png") for i in range(1, 4)]
player_death = [Frame(framesize, f"Assets/Player/death/{i}.png") for i in range(1, 6)]
player_knee = [Frame(framesize, f"Assets/Player/knee/{i}.png") for i in range(1, 3)]

# Enemy1 Lists
enemy1_attack = [Frame(framesizeE, f"Assets/Enemy/Enemy1/attack/{i}.png") for i in range(0, 12)]
enemy1_dying = [Frame(framesizeE, f"Assets/Enemy/Enemy1/Dying/{i}.png") for i in range(0, 15)]
enemy1_hurt = [Frame(framesizeE, f"Assets/Enemy/Enemy1/Hurt/{i}.png") for i in range(0, 12)]
enemy1_idle = [Frame(framesizeE, f"Assets/Enemy/Enemy1/Idle/{i}.png") for i in range(0, 12)]
enemy1_idleBlink = [Frame(framesizeE, f"Assets/Enemy/Enemy1/Idle Blink/{i}.png") for i in range(0, 12)]
enemy1_Walk = [Frame(framesizeE, f"Assets/Enemy/Enemy1/Walk/{i}.png") for i in range(0, 12)]

# sounds
pygame.mixer.init()
pygame.mixer.music.load('Assets/Sounds/touch.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.25)
touch_sound = pygame.mixer.Sound("Assets/Sounds/touch.mp3")

# menu
menu = pygame.image.load("Assets/Menu/menu.jpg")
menu_rect = menu.get_rect(topleft=(0, 0))
menu = pygame.transform.scale(menu, (x, y))

j = 0
player = Animation()
enemy1 = Enemy()
enemy2 = Enemy()
enemy3 = Enemy()
q = 600
ground = player.playerrect.bottom

# --- GAME LOOP ---
while True:
    rect = player.playerrect.bottomleft
    rectE1 = enemy1.enemyrect.bottomleft
    if player.playerrect.bottom < q:
        q = player.playerrect.bottom
    dt = clock.tick(60)
    mouse = pygame.mouse.get_pos()
    testtext = font1.render(f"curemo {current_emotion}  {x}  {enemy1.enemyrect.left} groun {ground} S {enemy1.frontE} ", False, "Black")
    kpressed = pygame.key.get_pressed()

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT or kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        
        # Toggle pause with 'P' key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            if start_scrn:
                pause_scrn = not pause_scrn
        
        # Handle button clicks
        for button in buttons:
            key_pressed = button.handle_event(event, mouse)
            if key_pressed == "exit":
                pygame.quit()
                exit()
            if key_pressed == "start":
                menu_scrn = False
                start_scrn = True
                pause_scrn = False # Ensure game is not paused when starting
    
    # --- Game State Logic ---
    if menu_scrn:
        screen.blit(menu, menu_rect)
        i = 0
        for equ in equations:
            print(equ.isactive)
            wait = (random.randint(400, 800))
            if not equ.active(wait, dt, cur_equation, eqn_locx, eqn_locy):
                if j < 13:
                    cur_equation[i] = (equ.generate_equation(signs))
                    eqn_locx[i] = (random.randint(int(unitx * 100), int(x - (unitx * 100))))
                    eqn_locy[i] = (random.randint(int(unity * 100), int(y - (unity * 100))))
                    i += 1
                j += 1
        for button in buttons:
            button.draw(screen)
    elif start_scrn:
        if not pause_scrn:
            # --- Game Update Logic (when not paused) ---
            # (Your existing game update code goes here, e.g., player movement, enemy logic, etc.)
            
            # Example placeholder for game logic:
            screen.fill((255, 255, 255)) # Fill with white to show game is running
            game_text = font1.render("Game is running! Press 'P' to pause.", True, "Black")
            screen.blit(game_text, (x/2 - game_text.get_width()/2, y/2 - game_text.get_height()/2))

        else:
            # --- Pause screen logic ---
            # (Draw pause menu, 'Paused' text, or other elements)
            
            # Example placeholder for pause screen:
            pause_overlay = pygame.Surface((x, y), pygame.SRCALPHA) # Transparent surface
            pause_overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            screen.blit(pause_overlay, (0, 0))
            
            pause_text = font1.render("PAUSED", True, "White")
            screen.blit(pause_text, (x/2 - pause_text.get_width()/2, y/2 - pause_text.get_height()/2))
            resume_text = font1.render("Press 'P' to resume", True, "White")
            screen.blit(resume_text, (x/2 - resume_text.get_width()/2, y/2 + 50))

    if player.playerrect.bottom < ground:
        onground = False

    pygame.display.update()
