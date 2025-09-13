import pygame
import random
import textwrap
from sys import exit

import cv2
import numpy as np
import tensorflow as tf
import threading


# ============================
# EMOTION DETECTOR SETUP
# ============================

# Load the TensorFlow Lite model for emotion detection
interpreter = tf.lite.Interpreter(model_path="Assets/Emotion detection models/emotion_model.tflite")
interpreter.allocate_tensors()

# Get input/output details for the model
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# List of emotions in the same order as the model's output neurons
Emotions_list = ['Angry','Disgust','Fear','Happy','Suprise','Sad','Neutral']

# Initialize webcam for emotion detection
cap = cv2.VideoCapture(0)

# Load face detection model (Caffe-based DNN)
net = cv2.dnn.readNetFromCaffe("Assets/Emotion detection models/dat.prototxt",
                               "Assets/Emotion detection models/caffe.caffemodel")

# Input size expected by the emotion model
input_height, input_width = 64, 64

# Contrast Limited Adaptive Histogram Equalization (CLAHE) for image enhancement
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Shared variable for storing detected emotion
current_emotion = "Neutral"


def emotion_loop():
    """Background thread function for continuous emotion detection"""
    global current_emotion
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            continue  

        frame = cv2.flip(frame, 1)
        (h, w) = frame.shape[:2]

        # Create blob from frame for face detection
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            1.0, 
            (300, 300), 
            (104.0, 177.0, 123.0)
        )
        net.setInput(blob)
        detections = net.forward()

        # Process detections
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.3:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                face_roi = frame[startY:endY, startX:endX]
                if face_roi.size == 0: 
                    continue

                # Preprocess face for emotion detection
                gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                enhanced_face = clahe.apply(gray_face)
                resized = cv2.resize(enhanced_face, (input_width, input_height))

                normalized = resized.astype('float32') / 255.0
                input_tensor = normalized.reshape(1, input_height, input_width, 1)

                # Run inference with TFLite
                interpreter.set_tensor(input_details[0]['index'], input_tensor)
                interpreter.invoke()
                predictions = interpreter.get_tensor(output_details[0]['index'])

                # Get the detected emotion
                emotion_idx = np.argmax(predictions)
                current_emotion = Emotions_list[emotion_idx]

                break  # only process first detected face


# Start emotion detection in background thread
threading.Thread(target=emotion_loop, daemon=True).start()


# Initialize pygame
pygame.init()
window=pygame.display.Info()
x=window.current_w
y=window.current_h
screen=pygame.display.set_mode((x,y))
clock=pygame.time.Clock() 
unitx=x/1000  # Unit for scaling based on screen width
unity=y/1000  # Unit for scaling based on screen height

# Game state flags
menu_scrn=True      # Main menu screen
start_scrn=False    # Gameplay screen
question_scrn=False # Question screen
options_scrn=False  # Options screen
level_scrn=False    # Level selection screen
gameover_scrn=False # Game over screen
paused = False      # Pause state
aboutus_scrn=False  # About us screen

# Fonts
font1=pygame.font.Font("Assets/Fonts/1.TTF",50)
font2=pygame.font.Font("Assets/Fonts/2.TTF",50)
font3=pygame.font.Font("Assets/Fonts/3.ttf",50)
font4=pygame.font.Font("Assets/Fonts/4.ttf",80)
font5=pygame.font.Font(None,50)
font6=pygame.font.Font("Assets/Fonts/5.ttf",70)

# Physics variables
player_vel_y = 0  
gravity = 1 * unity  
jump_strength = -30 * unity

# Background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x,y))
fade_surface.fill((0, 0, 0)) 
fade_surface.set_alpha(0)
alpha=0

# Emotion detector variables for decision making
bademotion=0      # Counter for negative emotions
changeLevel=0      # Counter for level changes

# Player variables
total_lives=5      # Player lives
framesize=(1.7*unitx,2.6*unity)  # Player frame size
immortal=False     # Invincibility state after being hit
immortaltime=0     # Timer for invincibility
playerattack=False # Player attack state
playerinjure=False # Player injury state
score=0            # Player score
scoreincrement=0   # Score increment based on level

# Questions variables
questionsize=(unitx*1.2,2*unity)
position_question=(200*unitx,600*unity)
answer=''           # Player's answer to question
answer_chosen=False # Whether answer has been chosen
correction_delay=0  # Delay after answering
timer=30            # Question timer
second=0            # Timer seconds
seconds=0           # Formatted seconds
minutes=0           # Formatted minutes
level="easy"        # Current difficulty level
initial_level="easy" # Initial difficulty level
previous_question=0 # Previous question index

# Enemies variables
framesizeE=(.3*unitx,.6*unity) # Enemy frame size
Enemydead=False     # Enemy dead state
enemyattack=False   # Enemy attack state
wave_interval=0     # Wave interval counter
wavesize=1          # Number of enemies per wave
wave=0              # Current wave counter

# Animation variables
signs=['+','-','/','*']  # Math operation signs

# Backgrounds variables
sizebk=(7000*unitx,y) # Background size
speedbk=4*unitx       # Background speed
k=0                   # Current background index
sound_pause=False     # Sound paused state
last_state=False      # Previous sound state

# Floor variables
l=0                   # Current floor index
sizefl=(21000*unitx,200*unity) # Floor size
speedfl=12*unitx      # Floor speed

# Animation variables
ground=y-(200*unity)  # Ground level
onground=True         # Whether player is on ground
border=0              # Background border

# Mouse variables
click_allowed=True    # Whether clicking is allowed

# Heart variables
sizeheart=(40*unitx,60*unity) # Heart icon size


# Player animations Frame class
class Frame:
    def _init_(self,size,path,pos=(0,ground)):
        self.size=size
        self.path=path
        self.frameF=pygame.image.load(path).convert_alpha()
        self.frameF=pygame.transform.scale(self.frameF,(self.frameF.get_width()*size[0],self.frameF.get_height()*size[1]))
        self.frameB=pygame.transform.flip(self.frameF,1,0)
        self.rect=self.frameF.get_rect(bottomleft=pos)

# Background class
class background:
    def _init_(self,path,speed,size):
        self.size=size
        self.speed=speed
        self.path=path
        self.img=pygame.image.load(path).convert_alpha()
        self.img=pygame.transform.scale(self.img,(size[0],size[1]))
        self.rect=self.img.get_rect(bottomleft=(0,y))
    
    def move(self,front):
        # Move background left or right
        if front:
            self.rect.left-=self.speed   
        else: 
            self.rect.left+=self.speed

# Equation class for math questions                       
class equationC:
    def _init_(self,eqaution="",sign="",ans=0,isactive=False,delay=0):
        self.equation=eqaution
        self.isactive=isactive
        self.sign=sign
        self.ans=ans
        self.delay=delay
    
    def generate_equation(self,signs):
        # Generate a random math equation
        self.equation=str(random.randint(1,50))+signs[random.randint(0,3)]+str(random.randint(1,50))
        self.ans=str(int(eval(self.equation)))
        self.delay=0
        self.equation=self.equation+"="+self.ans
        return self.equation
    
    def active(self,wait,dt,cur_equation,eqn_locx,eqn_locy):
        # Display equation for a certain time
        if(self.delay<wait):
            equationText=font1.render(f"{cur_equation[i]}",True,"Black")
            screen.blit(equationText,(eqn_locx[i],eqn_locy[i]))
            self.delay+=dt
            self.isactive=True
        else:
            # Generate new equation when time is up
            cur_equation[i]=(equ.generate_equation(signs))
            eqn_locx[i]=(random.randint(int(unitx*100),int(x-(unitx*200))))
            eqn_locy[i]=(random.randint(int(unity*100),int(y-(unity*150))))
            self.isactive=False
        return self.isactive

# Heart lives class
class Heart:
    def _init_(self,default_path,rect_pos):
        self.size=sizeheart
        self.default_img=pygame.image.load(default_path).convert_alpha()
        self.default_img=pygame.transform.scale(self.default_img,self.size)
        self.next_img=pygame.transform.scale(self.default_img,(self.size[0].8,self.size[1].8))
        self.rect=self.default_img.get_rect(center=rect_pos)
        self.delay=0
    
    def draw(self,screen):
        # Animate heart with pulsing effect
        self.delay+=dt
        if(self.delay>700):
            self.delay=0
        if self.delay<=350:
            img=self.next_img
        elif(self.delay>350):
            img=self.default_img
        screen.blit(img, self.rect)

# Button class
class button:
    def _init_(self,default_path,size,rect_pos,key=""):
        self.size=size
        self.default_img=pygame.image.load(default_path).convert_alpha()
        self.default_img=pygame.transform.scale(self.default_img,self.size)
        self.touched_img=pygame.transform.scale(self.default_img,(self.size[0].8,self.size[1].8))
        self.rect=self.default_img.get_rect(topleft=rect_pos)
        self.touched=False
        self.touching=True
        self.key=key
    
    def draw(self,screen):
        # Draw button with touch effect
        if self.touched: 
            img=self.touched_img 
        else:
            img=self.default_img
        screen.blit(img, self.rect)
    
    def handle_event(self, event, mouse_pos):
        # Handle button events
        self.touched = self.rect.collidepoint(mouse_pos)
        if self.touched and self.touching:
            touch_sound.play()
        self.touching=False
        if(not self.touched):
            self.touching=True
        if self.touched and click_allowed and event.type == pygame.MOUSEBUTTONDOWN:
            click_sound.play() 
            return self.key    
        return None

# Button list
buttons=[button("Assets\Buttons\Default\start.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*250)),"start"),
         button("Assets\Buttons\Default\settings.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*100)),"options"),
         button("Assets\Buttons\Default\exit.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)+(unity*50)),"exit"),
         button("Assets/Buttons/Default/reset.png",(x/28,y/19),((x/2)+(unitx*54),(y/2)+(unity*256)),"reset"),
         button("Assets/Buttons/Default/about us.png",(x/12,y/11),((unitx*850),(unity*850)),"about us")]

# Equations list
equations=[equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC()]

# Background list
backgrounds=[background("Assets/Backgrounds/1.png",speedbk,sizebk),
             background("Assets/Backgrounds/2.png",speedbk,sizebk),
             background("Assets/Backgrounds/3.png",speedbk,sizebk),
             background("Assets/Backgrounds/4.png",speedbk,sizebk),]

# Floor list
floors=[background("Assets/Floor/1.png",speedfl,sizefl),background("Assets/Floor/2.png",speedfl,sizefl)]


# Question TEXT BOXES
board=Frame((unitx*.8,unity*1.5),f"Assets/Questions/board.png",(150*unitx,800*unity))
hint_active=Frame((unitx*1.16,unity*.3),f"Assets/Questions/board.png",(10*unitx,980*unity))
hint_inactive=Frame((unitx*.3,unity*.5),f"Assets/Questions/hint.png",(10*unitx,980*unity))


# Player animations lists
player_run=[Frame(framesize,f"Assets/Player/run/{i}.png") for i in range(1,9)]    
player_jump=[Frame(framesize,f"Assets/Player/jump/{i}.png") for i in range(1,9)]
player_idle=[Frame(framesize,f"Assets/Player/idle/{i}.png") for i in range(1,9)]
player_shot=[Frame(framesize,f"Assets/Player/shot/{i}.png") for i in range(1,15)]
player_hurt=[Frame(framesize,f"Assets/Player/hurt/{i}.png") for i in range(1,4)]
player_death=[Frame(framesize,f"Assets/Player/death/{i}.png") for i in range(1,6)]
player_attack=[Frame(framesize,f"Assets/Player/attack/{i}.png") for i in range(1,7)]
player_knee=[Frame(framesize,f"Assets/Player/knee/{i}.png") for i in range(1,3)]      


# Enemy1 animations lists
enemy1_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy1/attack/{i}.png") for i in range(0,12)]
enemy1_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Dying/{i}.png") for i in range(0,15)]
enemy1_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Hurt/{i}.png") for i in range(0,12)]
enemy1_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Idle/{i}.png") for i in range(0,12)]
enemy1_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Idle Blink/{i}.png") for i in range(0,12)]
enemy1_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Walk/{i}.png") for i in range(0,12)]

# Enemy2 animations lists
enemy2_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy2/attack/{i}.png") for i in range(0,12)]
enemy2_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Dying/{i}.png") for i in range(0,15)]
enemy2_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Hurt/{i}.png") for i in range(0,12)]
enemy2_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Idle/{i}.png") for i in range(0,12)]
enemy2_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Idle Blink/{i}.png") for i in range(0,12)]
enemy2_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Walk/{i}.png") for i in range(0,12)]

# Enemy3 animations lists
enemy3_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy3/attack/{i}.png") for i in range(0,12)]
enemy3_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Dying/{i}.png") for i in range(0,15)]
enemy3_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Hurt/{i}.png") for i in range(0,12)]
enemy3_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Idle/{i}.png") for i in range(0,12)]
enemy3_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Idle Blink/{i}.png") for i in range(0,12)]
enemy3_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Walk/{i}.png") for i in range(0,12)]

# List of hearts for lives display
lives=[Heart("Assets\Player\heart\heart.png",((20*unitx)+(unitx*(i*50)),unity*100)) for i in range(1,6)]
HP=font6.render(f"HP",True,"Red")  # HP text

# Load high score from file
with open("Assets/HighScore.txt","r") as f:
    highscore=int(f.read())

# Questions/Answers datastructures and function

# Load questions from txt file
def load_questions(filename):
    questions = []
    with open(filename, "r") as f:
        content = f.read().strip().split("\n\n")  # Questions separated by blank line
        for block in content:
            lines = block.split("\n")
            q = lines[0]
            # Wrap the question if it's longer than 55 characters
            if len(q) > 35:
                q = "\n".join(textwrap.wrap(q, width=35))
            options = lines[1:5]
            hint = lines[5]  # hint
            answer = lines[6]  # correct answer index (A–D)
            questions.append((q, options, answer,hint))
    return questions

# Level selection buttons
level_buttons=[button("Assets\Buttons\Default\easy.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*250)),"easy"),
               button("Assets\Buttons\Default\medium.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*50)),"medium"),
               button("Assets\Buttons\Default\high.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)+(unity*150)),"high")]

# Gameover screen elements
gameover_background=Frame((unitx*1.4,unity*1.4),"Assets\Gameover\gameovertext.png",(70*unitx,700*unity))
descions=[button("Assets/Buttons/Default/yes.png",(x/10,y/12),((unitx*300),(unity*800)),"yes"),
          button("Assets/Buttons/Default/no.png",(x/10,y/12),((unitx*650),(unity*800)),"no")]

# Always on-screen buttons
home=button("Assets/Buttons/Default/home.png",(x/13,y/12),((unitx*900),(unity*50)),"home")
sound_unpaused=button("Assets/Buttons/Default/sound_unpaused.png",(x/13,y/12),((unitx*800),(unity*50)),"sound_unpaused")
sound_paused=button("Assets/Buttons/Default/sound_paused.png",(x/13,y/12),((unitx*800),(unity*50)),"sound_paused")

# Animation enemy class
class Enemy:
    active_attacker = None  # Class-level: only one enemy can attack at once

    def _init_(self, index=0, enemysuf=enemy1_idle[0].frameF, key=""):
        self.index = index
        self.frontE = False  # Facing direction
        self.attack = False  # Attack state
        self.enemysuf = enemysuf
        self.key = key
        self.wave = wavesize
        
        # Enemy states
        self.dying = False    # Dying animation state
        self.dead = False     # Dead state
        self.death_timer = 0  # Timer for death animation

        # Set initial position based on enemy type
        if key == "enemy1":
            self.enemyrect = enemy1_idleBlink[0].frameF.get_rect(bottomleft=(x, ground))
        elif key == "enemy2":
            self.enemyrect = enemy1_idle[0].frameF.get_rect(
                bottomleft=(x + (random.randint(200, 300) * unitx), ground)
            )
        elif key == "enemy3":
            self.enemyrect = enemy1_idle[0].frameF.get_rect(
                bottomleft=(x + (random.randint(500, 750) * unitx), ground)
            )

    def createanimation(self, rectE1):
        global playerattack, question_scrn, immortal, enemyattack, dt, wave
        
        # If already DEAD (stay on ground, then disappear)
        if self.dead:
            self.death_timer += dt
            if self.death_timer > 100:  # after ~100 frames remove enemy
                if(self.wave > 0):
                    self.dead = False
                    self.dying = False
                    self.enemyrect.bottomleft = (x + (random.randint(200, 500) * unitx), ground)  # Move off-screen
                    self.wave -= 1
                    wave -= 1
                elif(self.wave == 0):
                    self.enemyrect.bottom = -100 * unity  # Move completely off-screen
            return
        
        # DYING animation in progress
        if self.dying:
            self.index += 0.2
            # Select appropriate death animation based on enemy type
            death_frames = enemy1_dying if self.key == "enemy1" else enemy2_dying if self.key == "enemy2" else enemy3_dying
            
            if int(self.index) >= len(death_frames):
                self.index = len(death_frames) - 1
                self.dying = False
                self.dead = True
                self.death_timer = 0
            self.enemysuf = death_frames[int(self.index)].frameF
            self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
            return

        # MOVEMENT & ATTACK if alive
        if not question_scrn and not playerattack and not self.attack:
            if self.index >= len(enemy1_Walk):
                self.index = 0

            # Movement left/right
            if not self.frontE:
                self._set_walk_frame(rectE1, forward=False)
                self.enemyrect.left -= 3 * unitx
            else:
                self._set_walk_frame(rectE1, forward=True)
                self.enemyrect.left += 3 * unitx

            # Boundaries - change direction at screen edges
            if self.enemyrect.left < 0: 
                self.frontE = True
            if self.enemyrect.right >= x: 
                self.frontE = False
            self.index += 0.4

            # Start attack if collides with player and no other enemy is attacking
            if self.enemyrect.colliderect(player.playerrect) and Enemy.active_attacker is None and enemyattack:
                self.attack = True
                Enemy.active_attacker = self
                question_scrn = False

        # ATTACK animation
        elif self.attack:
            self.index += 0.2
            if self.index >= len(enemy1_attack):
                self.index = 0
                self.attack = False
                immortal = True  # Player becomes invincible after being attacked
                enemyattack = False
                Enemy.active_attacker = None
                return

            self._set_attack_frame()

    def _set_walk_frame(self, rectE1, forward):
        # Helper to set walking frames based on direction
        if self.key == "enemy1":
            self.enemysuf = enemy1_Walk[int(self.index)].frameF if forward else enemy1_Walk[int(self.index)].frameB
        elif self.key == "enemy2":
            self.enemysuf = enemy2_Walk[int(self.index)].frameF if forward else enemy2_Walk[int(self.index)].frameB
        elif self.key == "enemy3":
            self.enemysuf = enemy3_Walk[int(self.index)].frameF if forward else enemy3_Walk[int(self.index)].frameB
        self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)

    def _set_attack_frame(self):
        # Helper to set attack frames based on player position
        if self.key == "enemy1":
            self.enemysuf = (
                enemy1_attack[int(self.index)].frameF
                if self.enemyrect.right <= player.playerrect.right
                else enemy1_attack[int(self.index)].frameB
            )
        elif self.key == "enemy2":
            self.enemysuf = (
                enemy2_attack[int(self.index)].frameF
                if self.enemyrect.right <= player.playerrect.right
                else enemy2_attack[int(self.index)].frameB
            )
        elif self.key == "enemy3":
            self.enemysuf = (
                enemy3_attack[int(self.index)].frameF
                if self.enemyrect.right <= player.playerrect.right
                else enemy3_attack[int(self.index)].frameB
            )

    def trigger_death(self):
        """Call this when the player successfully finishes an attack on this enemy"""
        self.dying = True
        self.index = 0

# Animation player class
class Animation:
    def _init_(self, index=0, front=True, playersuf=player_idle[0].frameF, playerrect=player_idle[0].rect):
        self.index = index
        self.front = front  # Facing direction
        self.playersuf = playersuf
        self.playerrect = playerrect
        self.vel_y = 0  # Vertical velocity for jumping
    
    def createanimation(self, rect, onground, kpressed, playerattack):
        global wave_interval, walk_channel
        
        if not question_scrn and not playerattack:
            if(self.index >= len(player_jump)):
                self.index = 0
            
            # Move right (D key or auto-scroll)
            if((kpressed[pygame.K_d] or backgrounds[k].rect.right <= x + 250 * unitx) and not enemyattack):
                if(walk_channel is None or not walk_channel.get_busy()):
                    walk_channel = walk_sound.play()
                self.front = True
                self.playersuf = player_run[int(self.index)].frameF
                self.playerrect = self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width = self.playerrect.width - (91 * unitx)
                self.playerrect.bottomleft = rect
                backgrounds[k].move(True)
                floors[l].move(True)
                wave_interval += speedbk
                if self.playerrect.right <= x - (unitx * 150):
                    self.playerrect.left += 5 * unitx

            # Move left (A key)
            elif(kpressed[pygame.K_a] and not enemyattack):
                self.front = False
                self.playersuf = player_run[int(self.index)].frameB
                self.playerrect = self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width = self.playerrect.width - (91 * unitx)
                if self.playerrect.left > x - 980 * unitx:
                    backgrounds[k].move(False)
                    wave_interval -= speedbk
                    floors[l].move(False)
                    self.playerrect.left -= 5 * unitx

            # Crouch (S key)
            elif(kpressed[pygame.K_s] and not enemyattack):
                self.index -= .02
                self.index %= len(player_knee)
                if(self.front):
                    self.playersuf = player_knee[int(self.index)].frameF
                else:
                    self.playersuf = player_knee[int(self.index)].frameB
                self.playerrect = self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width = self.playerrect.width - (91 * unitx)

            # Idle animation when on ground
            elif(onground):
                if(self.front):
                    self.playersuf = player_idle[int(self.index)].frameF
                else: 
                    self.playersuf = player_idle[int(self.index)].frameB
                self.playerrect = self.playersuf.get_rect(bottomleft=rect)
                
            # Jump (W key)
            if(kpressed[pygame.K_w] and onground and not enemyattack):
                jump_sound.play()
                self.vel_y = jump_strength
                self.index = 0
                onground = False
                self.playerrect = player_jump[1].frameF.get_rect(bottomleft=rect)
                self.playerrect.width = self.playerrect.width - (91 * unitx)

            # Apply gravity
            self.vel_y += gravity
            self.playerrect.bottom += self.vel_y

            # Ground collision
            if(self.playerrect.bottom >= ground):
                self.playerrect.bottom = ground
                self.vel_y = 0
                onground = True
            
            # Jump animation
            if not onground:
                self.index += .07
                if(self.index >= len(player_jump)):
                    self.index = 7
                if self.front:
                    self.playersuf = player_jump[int(self.index)].frameF
                else:
                    self.playersuf = player_jump[int(self.index)].frameB
            
            # Update animation index
            self.index += 0.2
            self.index %= len(player_run)
            return onground
        
        # Attack animation
        elif playerattack:
            self.index += .2
            if self.index >= len(player_attack):
                playerattack = False
                # Check if attack hit any enemy
                if self.playerrect.colliderect(enemy1.enemyrect):
                    enemy1.trigger_death()
                elif self.playerrect.colliderect(enemy2.enemyrect):
                    enemy2.trigger_death()
                elif self.playerrect.colliderect(enemy3.enemyrect):
                    enemy3.trigger_death()
                return 
            
            # Set attack frame based on enemy position
            if self.playerrect.colliderect(enemy1.enemyrect):
                if enemy1.enemyrect.right >= self.playerrect.right:
                    self.playersuf = player_attack[int(self.index)].frameF
                else:
                    self.playersuf = player_attack[int(self.index)].frameB
            if self.playerrect.colliderect(enemy2.enemyrect):
                if enemy2.enemyrect.right >= self.playerrect.right:
                    self.playersuf = player_attack[int(self.index)].frameF
                else:
                    self.playersuf = player_attack[int(self.index)].frameB
            if self.playerrect.colliderect(enemy3.enemyrect):
                if enemy3.enemyrect.right >= self.playerrect.right:
                    self.playersuf = player_attack[int(self.index)].frameF
                else:
                    self.playersuf = player_attack[int(self.index)].frameB
            self.playerrect = player_attack[int(self.index)].frameF.get_rect(bottomleft=rect)


# Sound initialization
pygame.mixer.init()
touch_sound = pygame.mixer.Sound("Assets/Sounds/touch.mp3")
click_sound = pygame.mixer.Sound("Assets/Sounds/buttonclick.mp3")
menu_sound = pygame.mixer.Sound("Assets/Sounds/menu.mp3")
attack_player_sound = pygame.mixer.Sound("Assets/Sounds/attack.wav")
attack_monster_sound = pygame.mixer.Sound("Assets/Sounds/attackmonster.mp3")
hurt_player_sound = pygame.mixer.Sound("Assets/Sounds/hurt.mp3")
success_sound = pygame.mixer.Sound("Assets/Sounds/success.mp3")
walk_sound = pygame.mixer.Sound("Assets/Sounds/walk.wav")
fail_sound = pygame.mixer.Sound("Assets/Sounds/fail.mp3")
gameover_sound = pygame.mixer.Sound("Assets/Sounds/gameover.mp3")
gameloop_sound = pygame.mixer.Sound("Assets/Sounds/gameloop.mp3")
jump_sound = pygame.mixer.Sound("Assets/Sounds/jump.mp3")

# Sound channels
gameover_channel = None
gameloop_channel = None
gameloop_sound.set_volume(2)
walk_channel = None
menu_sound.set_volume(0.3)

# Menu background
menu = pygame.image.load("Assets/Menu/menu.jpg").convert_alpha()
menu_rect = menu.get_rect(topleft=(0,0))
menu = pygame.transform.scale(menu,(x,y))

# Math-runner title text
Title = pygame.image.load("Assets/Menu/title.png").convert_alpha()
Title_rect = Title.get_rect(topleft=(unitx*200, unity*40))
Title = pygame.transform.scale(Title,(600*unitx,200*unity))

# Scoreboard
scoreboard = pygame.image.load("Assets/Menu/scoreboard.png").convert_alpha()
scoreboard = pygame.transform.scale(scoreboard,(200*unitx,150*unity))
scoreboard_rect = scoreboard.get_rect(topleft=(400*unitx,20*unity))
scorefont = pygame.font.Font("Assets/Fonts/1.TTF",80)

# HighScore board
highscoreboard = pygame.image.load("Assets/Menu/highscoreboard.png").convert_alpha()
highscoreboard = pygame.transform.scale(highscoreboard,(200*unitx,150*unity))
highscoreboard_rect = highscoreboard.get_rect(topleft=(400*unitx,700*unity))
highscorefont = pygame.font.Font("Assets/Fonts/1.TTF",60)

# Mouse pointer
mouse_pointer = pygame.image.load("Assets/Menu/pointer2.png").convert_alpha()
mouse_pointer = pygame.transform.scale(mouse_pointer,(25*unitx,35*unity))
pointer_rect = mouse_pointer.get_rect(topleft=(0,0))

# About us screen elements
about_us_text = pygame.image.load("Assets/Menu/about us.png").convert_alpha()
aboutus_board = pygame.image.load("Assets/Menu/board.png").convert_alpha()
aboutus_board = pygame.transform.scale(aboutus_board,(860*unitx,910*unity))
about_us_text = pygame.transform.scale(about_us_text,(800*unitx,800*unity))
aboutus_board_rect = aboutus_board.get_rect(topleft=(80*unitx,70*unity))
about_us_text_rect = about_us_text.get_rect(topleft=(100*unitx,120*unity))

# Pause text
pausetext = pygame.image.load("Assets/Menu/pause.png").convert_alpha()
pausetext = pygame.transform.scale(pausetext,(800*unitx,400*unity))
pausetext_rect = pausetext.get_rect(topleft=(100*unitx,300*unity))

# Options screen background
option = pygame.image.load("Assets/option/option.png").convert_alpha()
option_rect = option.get_rect(topleft=(unitx*250, unity*100))
option = pygame.transform.scale(option,(500*unitx,800*unity))

# Initialize game variables
j = 0
cur_equation = ["","","","","","","","","","","","","",]
eqn_locx = [0,0,0,0,0,0,0,0,0,0,0,0,0]  # Fixed the typo here (was "极")
eqn_locy = [0,0,0,0,0,0,0,0,0,0,0,0,0]
player = Animation()
enemy1 = Enemy(key="enemy1")
enemy2 = Enemy(key="enemy2")
enemy3 = Enemy(key="enemy3") 
ground = player.playerrect.bottom
incomingwave = True
border = backgrounds[k].rect.left + (10 * unitx)
beginbackground = backgrounds[k].rect.left

# Hide default cursor
pygame.mouse.set_visible(False)

# Main game loop
while(True):
    rect = player.playerrect.bottomleft
    rectE1 = enemy1.enemyrect.bottomleft
    rectE2 = enemy2.enemyrect.bottomleft
    rectE3 = enemy3.enemyrect.bottomleft
    
    dt = clock.tick(60)  # Cap at 60 FPS
    mouse = pygame.mouse.get_pos() 
    testtext = font1.render(f"curemo {current_emotion} bad{bademotion}", False, "Black")
    kpressed = pygame.key.get_pressed()
    
    pointer_rect.topleft = mouse  # Update mouse pointer position
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        
        # Only allow pausing when not in question screen
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p and not menu_scrn and not question_scrn and not level_scrn and not gameover_scrn:
            # Toggle pause state when 'P' is pressed
            paused = not paused
        
        # Handle answer input in question screen
        if question_scrn and event.type == pygame.KEYDOWN and not answer_chosen:
            char = event.unicode
            if char.lower() in "abcd":
                answer = char.upper()
            if event.key == pygame.K_RETURN and answer != '':
                answer_chosen = True
    
    # Draw menu background
    screen.blit(menu, menu_rect)
    
    # If game is paused, display pause message and skip the rest of the loop
    if paused:
        screen.blit(pausetext, pausetext_rect)
        pygame.display.update()
        continue

    # Main menu screen
    if menu_scrn:
        # Play menu music if not already playing
        if(gameloop_channel is None or not gameloop_channel.get_busy()):
            gameloop_channel = menu_sound.play(-1)
        
        i = 0
        # Display and update equations in the background
        for equ in equations:
            wait = (random.randint(400,800))
            if not equ.active(wait, dt, cur_equation, eqn_locx, eqn_locy):
                if(j < 13):
                    cur_equation[i] = (equ.generate_equation(signs))
                    eqn_locx[i] = (random.randint(int(unitx*100), int(x-(unitx*100))))
                    eqn_locy[i] = (random.randint(int(unity*100), int(y-(unity*100))))
            i += 1
            j += 1
        
        # Display high score board
        screen.blit(highscoreboard, highscoreboard_rect)
        screen.blit(highscorefont.render(f"{highscore}", True, "Black"), (unitx*453, unity*735))
        
        # Handle menu buttons
        for button in buttons:
            button.draw(screen)
            button.handle_event(event, mouse)
            if(button.handle_event(event, mouse) == "exit"):
                pygame.quit()
                exit()
            if(button.handle_event(event, mouse) == "start"):
                menu_scrn = False
                level_scrn = True
                click_allowed = False
            if(button.handle_event(event, mouse) == "options"):
                menu_scrn = False
                options_scrn = True
                click_allowed = False 
            if(button.handle_event(event, mouse) == "reset"):
                highscore = 0
                with open("Assets/HighScore.txt", "w") as f:
                    f.write(f"{highscore}")
            if(button.handle_event(event, mouse) == "about us"):
                menu_scrn = False
                aboutus_scrn = True
                click_allowed = False
    
    # About us screen
    if aboutus_scrn:
        screen.blit(aboutus_board, aboutus_board_rect)
        screen.blit(about_us_text, about_us_text_rect)
    
    # Level selection screen
    if level_scrn:
        changeLevel = 0
        for button in level_buttons:
            button.draw(screen)
            button.handle_event(event, mouse)
            if(button.handle_event(event, mouse) == "easy"):
                questions = load_questions("Assets\Questions\easy.txt")
                level = "easy"
                initial_level = "easy"
                level_scrn = False
                start_scrn = True
            if(button.handle_event(event, mouse) == "medium"):
                questions = load_questions("Assets\Questions\medium.txt")
                level = "medium"
                initial_level = "medium"
                level_scrn = False
                start_scrn = True
            if(button.handle_event(event, mouse) == "high"):
                questions = load_questions("Assets\Questions\high.txt")
                level = "high"
                initial_level = "high"
                level_scrn = False
                start_scrn = True
    
    # Options screen
    if options_scrn == True:
        menu_scrn = False
        screen.blit(option, option_rect)
    
    # Allow clicking again after mouse button is released
    if event.type == pygame.MOUSEBUTTONUP:
        click_allowed = True
    
    # Check if player is on ground
    if(player.playerrect.bottom < ground):
        onground = False
    
    # Check for enemy collision to trigger question screen
    if((enemy1.enemyrect.colliderect(player.playerrect) or enemy2.enemyrect.colliderect(player.playerrect) or enemy3.enemyrect.colliderect(player.playerrect)) and not immortal and not playerattack and not enemyattack):
        if(not question_scrn):
            correction_delay = 0
            # Load questions based on difficulty level
            if level == "easy":
                questions = load_questions("Assets\Questions\easy.txt")
                timer = random.randrange(40,50,5)
            elif level == "medium":
                questions = load_questions("Assets\Questions\medium.txt")
                timer = random.randrange(40,60,10)
            elif level == "high":
                questions = load_questions("Assets\Questions\high.txt")
                timer = random.randrange(50,90,10)
            
            # Select random question
            question, options, correct_answer, hint = random.choice(questions)
            wrapped_lines = textwrap.wrap(question, width=35)
            question_scrn = True
            incomingwave = False
    
    # Check if all enemies in wave are defeated
    if wave == 3:
        incomingwave = True
    
    # Gameplay screen
    if start_scrn:
        menu_sound.stop()
        # Play game music if not already playing
        if(gameloop_channel is None or not gameloop_channel.get_busy()):
            gameloop_channel = gameloop_sound.play(-1)
        
        # Check for game over condition
        if(total_lives == 0):
            start_scrn = False
            gameover_scrn = True
            gameloop_sound.stop()
            gameloop_channel = menu_sound.play(-1)
       
        # Update high score if current score is higher
        if score >= highscore:
            highscore = score
            with open("Assets/HighScore.txt", "w") as f:
                f.write(f"{highscore}")

        # Render game elements if within background boundaries
        if backgrounds[k].rect.right >= x and backgrounds[k].rect.left <= border:
            screen.blit(backgrounds[k].img, backgrounds[k].rect)
            screen.blit(floors[l].img, floors[l].rect)
            
            # Update player and enemy animations
            onground = player.createanimation(rect, onground, kpressed, playerattack)
            enemy1.createanimation(rectE1)
            enemy2.createanimation(rectE2)
            enemy3.createanimation(rectE3)
            
            # Draw enemies
            screen.blit(enemy1.enemysuf, enemy1.enemyrect)
            screen.blit(enemy2.enemysuf, enemy2.enemyrect)
            screen.blit(enemy3.enemysuf, enemy3.enemyrect)
            
            # Draw HP and lives
            screen.blit(HP, (10*unitx, 50*unity))
            for i in range(total_lives):
                lives[i].draw(screen)
            
            # Draw player (with blinking effect if immortal)
            if(not immortal):
                screen.blit(player.playersuf, player.playerrect)
            elif(immortal and dt % 2 == 0):
                screen.blit(player.playersuf, player.playerrect)
            
            # Fade effect when approaching background edge
            if (backgrounds[k].rect.right <= x + 250 * unitx):
                fade_surface.set_alpha(alpha)
                alpha += 5
                screen.blit(fade_surface, (0, 0))
            
            # Display incoming wave warning
            if incomingwave:
                screen.blit(font4.render("INCOMING WAVE", True, "Yellow"), (unitx*200, unity*400))
            
            # Spawn new wave when interval is reached
            if wave_interval >= 2300 * unitx:
                enemy1.wave = wavesize 
                enemy2.wave = wavesize
                enemy3.wave = wavesize
                border += 2300 * unitx
                wave = (wavesize * 3)
                wave_interval = 0
        else:
            # Reset background and floor when reaching the end
            backgrounds[k].rect.bottomleft = (0, y)
            wave_interval = 0
            floors[l].rect.bottomleft = (0, y)
            k += 1
            l += 1
            k %= 4
            l %= 2
            border = backgrounds[k].rect.left
            alpha = 0
            player.playerrect.left = 10 * unitx

    # Set score increment based on difficulty level
    if level == "easy":
        scoreincrement = 5
    elif level == "medium":
        scoreincrement = 10
    elif level == "high":
        scoreincrement = 15    
    
    # Game over screen
    if gameover_scrn:
        # Play menu music if not already playing
        if(gameloop_channel is None or not gameloop_channel.get_busy()):
            gameloop_channel = menu_sound.play(-1)
        
        # Display game over elements
        screen.blit(font4.render("RESTART", True, "Yellow"), (350*unitx, 650*unity))
        screen.blit(gameover_background.frameF, gameover_background.rect)
        
        # Handle restart decision buttons
        for button in descions:
            button.draw(screen)
            button.handle_event(event, mouse)
            if(button.handle_event(event, mouse) == "yes"):
                # Reset game state for restart
                total_lives = 5
                menu_scrn = True
                gameover_scrn = False
                player.playerrect.left = 10*unitx
                enemy1.enemyrect.left = x+200*unitx
                enemy2.enemyrect.left = x+500*unitx
                enemy3.enemyrect.left = x+800*unitx
                changeLevel = 0
                k = 0
                score = 0  # Reset score
            if(button.handle_event(event, mouse) == "no"):
                # Return to main menu instead of exiting
                total_lives = 5
                menu_scrn = True
                gameover_scrn = False
                player.playerrect.left = 10*unitx
                enemy1.enemyrect.left = x+200*unitx
                enemy2.enemyrect.left = x+500*unitx
                enemy3.enemyrect.left = x+800*unitx
                changeLevel = 0
                k = 0
                score = 0  # Reset score

        # Play game over sound once
        if (gameover_channel == None):
            gameover_channel = gameover_sound.play()
    
    # Handle invincibility timer
    if immortal:
        if(immortaltime >= 2000):
            immortal = False
        immortaltime += dt
    
    # Handle player attack completion
    if playerattack:
        if player.index >= len(player_attack):
            immortal = True
            playerattack = False
    
    # Display title "MATH RUNNER" on menu and level selection screens
    if(menu_scrn or level_scrn):
        screen.blit(Title, Title_rect)
    
    # Display the score board during gameplay
    if(start_scrn or gameover_scrn or question_scrn):
        screen.blit(scoreboard, scoreboard_rect)
        screen.blit(scorefont.render(f"{score}", True, "Black"), (unitx*450, unity*60))    

    # Check if player faces 3 consecutive wrong answers and change level accordingly
    if changeLevel == 3:
        level = "easy"
    
    # Question screen
    if question_scrn:
        second += dt
        # Track negative emotions
        if(current_emotion != "Happy" and current_emotion != "Neutral"):
            bademotion += 1
        
        # Update question timer
        if second >= 1000 and timer > 0:
            timer -= 1
            second = 0
            seconds = timer % 60
            minutes = int(timer/60) % 60
        
        # Prepare text surfaces
        display_answer = font2.render(f"Your Answer (press 'Enter' to validate) : {answer.upper()}", True, "Black")
        display_correct = font2.render(f"CORRECT!!!", True, "Green")
        display_wrong = font2.render(f"FAILED!!! correct = {correct_answer.upper()}", True, "Red")
        display_timer = font3.render(f"Timer {minutes:02}:{seconds:02}", True, "White")
        
        # Display question board
        screen.blit(board.frameF, board.rect)
        question_posY = 230 * unity
        
        # Display question with word wrap
        for line in wrapped_lines:
            question_surface = font5.render(line, True, "Black")
            screen.blit(question_surface, (200*unitx, question_posY))
            question_posY += font5.get_height() + 5 * unity
        question_posY += 15 * unity
        
        # Display options
        for i, optio in enumerate(options):
            option_surface = font5.render(f"{optio}", True, "Black")
            screen.blit(option_surface, (200*unitx, question_posY + (i * (font5.get_height() + 20) * unity)))
        
        # Display answer and timer
        screen.blit(display_answer, (240*unitx, 620*unity))
        screen.blit(display_timer, (500*unitx, 400*unity))
        test = font2.render(f"{hint}", True, "Yellow")
        
        # Show hint button only when bademotion is 500 or more
        if(bademotion >= 500):
            if (kpressed[pygame.K_h] and pygame.KEYDOWN):
                screen.blit(hint_active.frameF, hint_active.rect)
                screen.blit(test, (40*unitx, 880*unity))
            else:
                screen.blit(hint_inactive.frameF, hint_inactive.rect)
        
        # Handle correct answer
        if(answer_chosen and answer.upper() == correct_answer):
            if(correction_delay == 0):
                changeLevel -= 1
                if level != initial_level:
                    level = initial_level
                    changeLevel = 0
                success_sound.play()
            screen.blit(display_correct, (240*unitx, 675*unity))
            correction_delay += dt
            if(correction_delay >= 2000):
                score += scoreincrement
                player.playerrect.bottom = ground
                player.index = 0
                correction_delay = 0
                playerattack = True
                attack_player_sound.play()
                immortaltime = 0
                question_scrn = False
                bademotion = 0 
                answer_chosen = False
                answer = ''
                timer = 30  # Reset timer for next question
        
        # Handle wrong answer or time out
        elif(answer_chosen and answer.upper() != correct_answer or timer <= 0):
            if(correction_delay == 0):
                changeLevel += 1
                if level != initial_level:
                    level = initial_level
                    changeLevel = 0
                fail_sound.play()
            screen.blit(display_wrong, (240*unitx, 670*unity))
            correction_delay += dt
            if(correction_delay >= 2000):
                # Reduce life for wrong answer OR for not answering (timer running out)
                if(answer_chosen and answer.upper() != correct_answer or timer <= 0):
                    total_lives -= 1
                correction_delay = 0
                enemy1.index = 0
                enemy2.index = 0
                enemy3.index = 0
                immortaltime = 0
                enemyattack = True
                attack_monster_sound.play()
                hurt_player_sound.play()
                question_scrn = False 
                answer_chosen = False
                bademotion = 0
                answer = ''
                timer = 30  # Reset timer for next question
    
    # Draw always-visible buttons (home and sound controls)
    home.draw(screen)
    if not sound_pause:
        sound_paused.draw(screen)
    elif sound_pause:
        sound_unpaused.draw(screen)
    
    # Handle home button click
    if home.handle_event(event, mouse) == "home":
        total_lives = 5
        gameover_channel = None
        menu_scrn = True
        level_scrn = False
        options_scrn = False
        question_scrn = False
        start_scrn = False
        aboutus_scrn = False
        bademotion = 0
        score = 0
        gameover_scrn = False
        gameloop_sound.stop()
        player.playerrect.left = 10*unitx
        enemy1.enemyrect.left = x+200*unitx
        enemy2.enemyrect.left = x+500*unitx
        enemy3.enemyrect.left = x+800*unitx
        changeLevel = 0
        k = 0
    
    # Handle sound pause/unpause buttons
    if sound_paused.handle_event(event, mouse) == "sound_paused" and click_allowed:
        sound_pause = True
        click_allowed = False
        sound_paused.rect.bottom = -100 * unity
        sound_unpaused.rect.top = 50 * unity
    if sound_unpaused.handle_event(event, mouse) == "sound_unpaused" and click_allowed:
        sound_pause = False
        click_allowed = False
        sound_unpaused.rect.bottom = -100 * unity
        sound_paused.rect.top = 50 * unity
    
    # Pause/unpause sound based on state
    if sound_pause:
        pygame.mixer.pause()
    elif not sound_pause:
        pygame.mixer.unpause()
    
    last_state = sound_pause
    
    # Debug text for emotion detection
    screen.blit(testtext, (10*unitx, 10*unity)) 
    
    # Draw custom mouse pointer
    screen.blit(mouse_pointer, pointer_rect)

    # Update display
    pygame.display.update()
