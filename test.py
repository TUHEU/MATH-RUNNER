import pygame
import random
from sys import exit

import cv2 # OpenCV for computer vision tasks
import numpy as np #to handle arrays and matrices
from tensorflow.keras.models import load_model # Keras for loading the pre-trained model
import threading # For running emotion detection in a separate thread (simultaneous execution)


#EMOTION DETECTOR SETUP
# Load the pre-trained emotion recognition model
model = load_model("Assets/Emotion detection models/fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)

# List of emotions in the same order as the model's output neurons
Emotions_list = ['Angry','Disgust','Fear','Happy','Suprise','Sad','Neutral']

# Initialize webcam
cap = cv2.VideoCapture(0)

# Load face detection model (Caffe-based DNN)
net = cv2.dnn.readNetFromCaffe("Assets/Emotion detection models/dat.prototxt",
                               "Assets/Emotion detection models/caffe.caffemodel")

# Input size expected by the emotion model
input_height, input_width = 64, 64

# Contrast Limited Adaptive Histogram Equalization (CLAHE) for enhancing faces
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Shared variable for storing detected emotion (default = Neutral)
current_emotion = "Neutral"


def emotion_loop():
        #Continuously reads frames from webcam,
        #detects faces using Caffe DNN,
        #preprocesses the face,
    #and updates the global variable 'current_emotion'
    #with the detected emotion.
   
    global current_emotion
    
    while True:
        # Capture a frame from webcam
        ret, frame = cap.read()
        if not ret: 
            continue  # If frame not captured, skip this loop

        # Flip horizontally (like a mirror/selfie view)
        frame = cv2.flip(frame, 1)
        (h, w) = frame.shape[:2]

        # Prepare input blob for face detection
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),  # Resize frame for face detection model
            1.0,                            # Scale factor
            (300, 300),                     # Target size
            (104.0, 177.0, 123.0)           # Mean subtraction values
        )
        net.setInput(blob)
        detections = net.forward()  # Run face detection

        # Loop through detected faces
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # Only process strong detections
            if confidence > 0.3:
                # Get bounding box coordinates
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Extract face region of interest (ROI)
                face_roi = frame[startY:endY, startX:endX]

                # Skip if ROI is empty
                if face_roi.size == 0: 
                    continue

                # Convert to grayscale for emotion model
                gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                # Apply CLAHE to improve contrast
                enhanced_face = clahe.apply(gray_face)

                # Resize to match model input size
                resized = cv2.resize(enhanced_face, (input_width, input_height))

                # Normalize pixel values (0-1) and reshape for model
                normalized = resized.astype('float32') / 255.0
                input_tensor = normalized.reshape(1, input_height, input_width, 1)

                # Run emotion prediction
                predictions = model.predict(input_tensor, verbose=0)
                emotion_idx = np.argmax(predictions)   # Get emotion index
                current_emotion = Emotions_list[emotion_idx]  # Map index to label

                # Only process first detected face (break after detection)
                break

# Start emotion detection in background thread
#Normal (non-daemon) thread → the program will wait for it to finish before exiting.
#Daemon thread → the program will not wait for it. When the main program ends, daemon threads are killed automatically.
threading.Thread(target=emotion_loop, daemon=True).start()



pygame.init()
window=pygame.display.Info()
x=window.current_w
y=window.current_h
screen=pygame.display.set_mode((x,y))
clock=pygame.time.Clock() 
unitx=x/1000
unity=y/1000

#pages booleans
menu_scrn=True
start_scrn=False
question_scrn=False
#font
font1=pygame.font.Font("Assets/Fonts/1.TTF",50)

#physics variables
player_vel_y = 0  
gravity = 1 * unity  
jump_strength = -30 * unity

#Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x,y))
fade_surface.fill((0, 0, 0)) 
fade_surface.set_alpha(0)
alpha=0

#player variables
framesize=(1.7*unitx,2.6*unity)
immortal=False
immortaltime=0
playerattack=False
playerinjure=False

#Enemies variables
framesizeE=(.3*unitx,.6*unity)
Enemydead=False
enemyattack=False

#animation variables
signs=['+','-','/','*']

#backgrounds variables
sizebk=(7000*unitx,y)
speedbk=4*unitx
k=0

#floor variables
l=0
sizefl=(21000*unitx,200*unity)
speedfl=12*unitx

#animation variables
ground=y-(200*unity)
onground=True

# player animations Frame class
class Frame:
    def __init__(self,size,path,pos=(0,ground)):
        self.size=size
        self.path=path
        self.frameF=pygame.image.load(path).convert_alpha()
        self.frameF=pygame.transform.scale(self.frameF,(self.frameF.get_width()*size[0],self.frameF.get_height()*size[1]))
        self.frameB=pygame.transform.flip(self.frameF,1,0)
        self.rect=self.frameF.get_rect(bottomleft=pos)

#class background
class background:
    def __init__(self,path,speed,size):
        self.size=size
        self.speed=speed
        self.path=path
        self.img=pygame.image.load(path).convert_alpha()
        self.img=pygame.transform.scale(self.img,(size[0],size[1]))
        self.rect=self.img.get_rect(bottomleft=(0,y))
    def move(self,front):
        #if(self.rect.right>=x):
        if front :self.rect.left-=self.speed   
        else: self.rect.left+=self.speed

#equation                       
class equationC:
    def __init__(self,eqaution="",sign="",ans=0,isactive=False,delay=0):
        self.equation=eqaution
        self.isactive=isactive
        self.sign=sign
        self.ans=ans
        self.delay=delay
    def generate_equation(self,signs):
        self.equation=str(random.randint(1,50))+signs[random.randint(0,3)]+str(random.randint(1,50))
        self.ans=str(int(eval(self.equation)))
        self.delay=0
        self.equation=self.equation+"="+self.ans
        return self.equation
    def active(self,wait,dt,cur_equation,eqn_locx,eqn_locy):
        if(self.delay<wait):
                    equationText=font1.render(f"{cur_equation[i]}",True,"Black")
                    #equationText=pygame.transform.rotate(equationText,random.randint(0,45))
                    screen.blit(equationText,(eqn_locx[i],eqn_locy[i]))
                    self.delay+=dt
                    self.isactive=True
        else:
            cur_equation[i]=(equ.generate_equation(signs))
            eqn_locx[i]=(random.randint(int(unitx*100),int(x-(unitx*200))))
            eqn_locy[i]=(random.randint(int(unity*100),int(y-(unity*150))))
            self.isactive=False
        return self.isactive


#button class
class button:
    def __init__(self,default_path,size,rect_pos,key=""):
        self.size=size
        self.default_img=pygame.image.load(default_path).convert_alpha()
        self.default_img=pygame.transform.scale(self.default_img,self.size)
        self.touched_img=pygame.transform.scale(self.default_img,(self.size[0]*.8,self.size[1]*.8))
        self.rect=self.default_img.get_rect(topleft=rect_pos)
        self.touched=False
        self.touching=True
        self.key=key
    def draw(self,screen):
        if self.touched: img=self.touched_img 
        else:img=self.default_img
        screen.blit(img, self.rect)
    def handle_event(self, event, mouse_pos):
        self.touched = self.rect.collidepoint(mouse_pos)
        if self.touched and self.touching:
            touch_sound.play()
        self.touching=False
        if(not self.touched):self.touching=True
        if self.touched and event.type == pygame.MOUSEBUTTONDOWN: 
            return self.key    
        return None

#button list
buttons=[button("Assets\Buttons\Default\start.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*300)),"start"),
         button("Assets\Buttons\Default\options.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity*150)),"options"),
         button("Assets\Buttons\Default\custom level.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)-(unity)),"custom level"),
         button("Assets\Buttons\Default\exit.png",(x/4,y/8),((x/2)-(unitx*120),(y/2)+(unity*150)),"exit")]

#equations list
equations=[equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC()]

#background list
backgrounds=[background("Assets/Backgrounds/1.png",speedbk,sizebk),
             background("Assets/Backgrounds/2.png",speedbk,sizebk),
             background("Assets/Backgrounds/3.png",speedbk,sizebk),
             background("Assets/Backgrounds/4.png",speedbk,sizebk),]

#floor list
floors=[background("Assets/Floor/1.png",speedfl,sizefl),background("Assets/Floor/2.png",speedfl,sizefl)]


#question images
board=Frame((unitx*.8,unity*1.5),f"Assets/Questtions/board.png",(150*unitx,800*unity))


#player animations lists
player_run=[Frame(framesize,f"Assets/Player/run/{i}.png") for i in range(1,9)]    
player_jump=[Frame(framesize,f"Assets/Player/jump/{i}.png") for i in range(1,9)]
player_idle=[Frame(framesize,f"Assets/Player/idle/{i}.png") for i in range(1,9)]
player_shot=[Frame(framesize,f"Assets/Player/shot/{i}.png") for i in range(1,15)]
player_hurt=[Frame(framesize,f"Assets/Player/hurt/{i}.png") for i in range(1,4)]
player_death=[Frame(framesize,f"Assets/Player/death/{i}.png") for i in range(1,6)]
player_attack=[Frame(framesize,f"Assets/Player/attack/{i}.png") for i in range(1,7)]
player_knee=[Frame(framesize,f"Assets/Player/knee/{i}.png") for i in range(1,3)]      


#Enemy1 Lists
enemy1_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy1/attack/{i}.png") for i in range(0,12)]
enemy1_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Dying/{i}.png") for i in range(0,15)]
enemy1_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Hurt/{i}.png") for i in range(0,12)]
enemy1_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Idle/{i}.png") for i in range(0,12)]
enemy1_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Idle Blink/{i}.png") for i in range(0,12)]
enemy1_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy1/Walk/{i}.png") for i in range(0,12)]

#Enemy2 Lists
enemy2_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy2/attack/{i}.png") for i in range(0,12)]
enemy2_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Dying/{i}.png") for i in range(0,15)]
enemy2_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Hurt/{i}.png") for i in range(0,12)]
enemy2_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Idle/{i}.png") for i in range(0,12)]
enemy2_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Idle Blink/{i}.png") for i in range(0,12)]
enemy2_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy2/Walk/{i}.png") for i in range(0,12)]

#Enemy3 Lists
enemy3_attack=[Frame(framesizeE,f"Assets/Enemy/Enemy3/attack/{i}.png") for i in range(0,12)]
enemy3_dying=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Dying/{i}.png") for i in range(0,15)]
enemy3_hurt=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Hurt/{i}.png") for i in range(0,12)]
enemy3_idle=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Idle/{i}.png") for i in range(0,12)]
enemy3_idleBlink=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Idle Blink/{i}.png") for i in range(0,12)]
enemy3_Walk=[Frame(framesizeE,f"Assets/Enemy/Enemy3/Walk/{i}.png") for i in range(0,12)]

#animation enemy class
class Enemy:
    active_attacker = None  # Class-level: only one enemy can attack at once

    def __init__(self, index=0, enemysuf=enemy1_idle[0].frameF, key=""):
        self.index = index
        self.frontE = False
        self.attack = False
        self.enemysuf = enemysuf
        self.key = key

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
        global playerattack, question_scrn, immortal, enemyattack 

        # Movement & idle animations when no attack is happening
        if not question_scrn and not playerattack and not self.attack:
            if self.index >= len(enemy1_Walk):
                self.index = 0

            # Movement left/right
            if not self.frontE and not self.attack:
                if self.key == "enemy1":
                    self.enemysuf = enemy1_Walk[int(self.index)].frameB
                elif self.key == "enemy2":
                    self.enemysuf = enemy2_Walk[int(self.index)].frameB
                elif self.key == "enemy3":
                    self.enemysuf = enemy3_Walk[int(self.index)].frameB
                self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
                self.enemyrect.left -= 3 * unitx

            elif self.frontE and not self.attack:
                if self.key == "enemy1":
                    self.enemysuf = enemy1_Walk[int(self.index)].frameF
                elif self.key == "enemy2":
                    self.enemysuf = enemy2_Walk[int(self.index)].frameF
                elif self.key == "enemy3":
                    self.enemysuf = enemy3_Walk[int(self.index)].frameF
                self.enemyrect = self.enemysuf.get_rect(bottomleft=rectE1)
                self.enemyrect.left += 3 * unitx

            # Boundaries
            if(self.enemyrect.left<0):self.frontE=True
            if(self.enemyrect.right>=x):self.frontE=False
            self.index += 0.4

            # Start attack if collides with player and no other enemy is attacking
            if enemyattack and Enemy.active_attacker is None:
                self.attack = True
                Enemy.active_attacker = self
                question_scrn = False
        # ATTACK animation phase
        elif self.attack:
            self.index += 0.2
            if self.index >= len(enemy1_attack):
                # Reset attack state once animation completes
                self.index = 0
                self.attack = False
                immortal=True
                enemyattack=False
                Enemy.active_attacker = None
                #question_scrn = False  # Close question screen when done
                return

            # Select attack frame based on position relative to player
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
#animation player class
class Animation:
    def __init__(self,index=0,front=True,playersuf=player_idle[0].frameF,playerrect=player_idle[0].rect):
        self.index=index
        self.front=front
        self.playersuf=playersuf
        self.playerrect=playerrect
        self.vel_y = 0
    def createanimation(self, rect,onground,kpressed,playerattack):
        if not question_scrn and not  playerattack:
            if(self.index >=len(player_jump)):self.index=0
            if(kpressed[pygame.K_d] ):
                self.front=True
                self.playersuf=player_run[int(self.index)].frameF
                self.playerrect=self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width=self.playerrect.width-(91*unitx)
                self.playerrect.bottomleft=rect
                backgrounds[k].move(True)
                floors[l].move(True)
                if self.playerrect.right<=x-(unitx*150):self.playerrect.left+=5*unitx

            elif(kpressed[pygame.K_a]):
                self.front= False
                self.playersuf=player_run[int(self.index)].frameB
                self.playerrect=self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width=self.playerrect.width-(91*unitx)
                if self.playerrect.left>x-980*unitx:
                    backgrounds[k].move(False)
                    floors[l].move(False)
                    self.playerrect.left-=5*unitx

            elif(kpressed[pygame.K_s]):
                self.index-=.02
                self.index%=len(player_knee)
                if(self.front):self.playersuf=player_knee[int(self.index)].frameF
                else:self.playersuf=player_knee[int(self.index)].frameB
                self.playerrect=self.playersuf.get_rect(bottomleft=rect)
                self.playerrect.width=self.playerrect.width-(91*unitx)

            elif(onground):
                if(self.front):self.playersuf=player_idle[int(self.index)].frameF
                else: self.playersuf=player_idle[int(self.index)].frameB
                self.playerrect=self.playersuf.get_rect(bottomleft=rect)
                
            if(kpressed[pygame.K_w] and onground):
                self.vel_y=jump_strength
                self.index=0
                onground=False
                self.playerrect=player_jump[1].frameF.get_rect(bottomleft=rect)
                self.playerrect.width=self.playerrect.width-(91*unitx)

            self.vel_y+=gravity
            self.playerrect.bottom+=self.vel_y

            if(self.playerrect.bottom>=ground):
                self.playerrect.bottom=ground
                self.vel_y = 0
                onground = True
            if not onground:
                self.index+=.07
                if(self.index >=len(player_jump)):self.index=7
                if self.front:
                    self.playersuf = player_jump[int(self.index)].frameF
                else:
                    self.playersuf = player_jump[int(self.index)].frameB
            self.index+=0.2
            self.index%= len(player_run)
            return onground
        elif playerattack:
            self.index+=.2
            if self.index >= len(player_attack):
                playerattack = False
                return 
            if self.playerrect.colliderect (enemy1.enemyrect):
                if enemy1.enemyrect.right>=self.playerrect.right:
                    self.playersuf=player_attack[int(self.index)].frameF
                else:
                    self.playersuf=player_attack[int(self.index)].frameB
            if self.playerrect.colliderect (enemy2.enemyrect):
                if enemy2.enemyrect.right>=self.playerrect.right:
                    self.playersuf=player_attack[int(self.index)].frameF
                else:
                    self.playersuf=player_attack[int(self.index)].frameB
            if self.playerrect.colliderect (enemy3.enemyrect):
                if enemy3.enemyrect.right>=self.playerrect.right:
                    self.playersuf=player_attack[int(self.index)].frameF
                else:
                    self.playersuf=player_attack[int(self.index)].frameB
            self.playerrect=player_attack[int(self.index)].frameF.get_rect(bottomleft=rect)


#sounds
pygame.mixer.init()
# pygame.mixer.music.load('Assets\Sounds\touch.mp3')
# pygame.mixer.music.play()
# pygame.mixer.music.set_volume(0.25)

touch_sound=pygame.mixer.Sound("Assets/Sounds/touch.mp3")

#menu
menu=pygame.image.load("Assets/Menu/menu.jpg")
menu_rect=menu.get_rect(topleft=(0,0))
menu=pygame.transform.scale(menu,(x,y))
j=0
cur_equation=["","","","","","","","","","","","","",]
eqn_locx=[0,0,0,0,0,0,0,0,0,0,0,0,0]
eqn_locy=[0,0,0,0,0,0,0,0,0,0,0,0,0]
player=Animation()
enemy1=Enemy(key="enemy1")
enemy2=Enemy(key="enemy2")
enemy3=Enemy(key="enemy3") 
ground=player.playerrect.bottom
while(True):
    rect=player.playerrect.bottomleft
    rectE1=enemy1.enemyrect.bottomleft
    rectE2=enemy2.enemyrect.bottomleft
    rectE3=enemy3.enemyrect.bottomleft
    
    dt=clock.tick(60)
    mouse = pygame.mouse.get_pos() 
    testtext=font1.render(f"curemo {current_emotion} ply {player.playerrect.width} immt {immortaltime} ques {question_scrn} {enemy1.frontE} ",False,"Black")
    kpressed=pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT or kpressed[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
    screen.blit(menu,menu_rect)
#menu true  
    if menu_scrn:
        i=0
        for equ in equations:
            print(equ.isactive)
            wait=(random.randint(400,800))
            if not equ.active(wait,dt,cur_equation,eqn_locx,eqn_locy):
                if(j<13):
                    cur_equation[i]=(equ.generate_equation(signs))
                    eqn_locx[i]=(random.randint(int(unitx*100),int(x-(unitx*100))))
                    eqn_locy[i]=(random.randint(int(unity*100),int(y-(unity*100))))
            i+=1
            j+=1
        for button in buttons:
            button.draw(screen)
            button.handle_event(event,mouse)
            if(button.handle_event(event,mouse)=="exit"):
                pygame.quit()
                exit()
            if(button.handle_event(event,mouse)=="start"):
                menu_scrn=False
                start_scrn=True
    if(player.playerrect.bottom<ground):onground=False
    if((enemy1.enemyrect.colliderect(player.playerrect) or enemy2.enemyrect.colliderect(player.playerrect) or enemy3.enemyrect.colliderect(player.playerrect)) and not immortal and not playerattack):question_scrn=True
    if start_scrn:
          if backgrounds[k].rect.right>=x:
            screen.blit(backgrounds[k].img,backgrounds[k].rect)
            screen.blit(floors[l].img,floors[l].rect)
            onground=player.createanimation(rect,onground,kpressed,playerattack)
            enemy1.createanimation(rectE1)
            enemy2.createanimation(rectE2)
            enemy3.createanimation(rectE3)
            screen.blit(enemy1.enemysuf,enemy1.enemyrect)
            screen.blit(enemy2.enemysuf,enemy2.enemyrect)
            screen.blit(enemy3.enemysuf,enemy3.enemyrect)
            if(not immortal):
                screen.blit(player.playersuf,player.playerrect)
            elif(immortal and dt%2==0):
                screen.blit(player.playersuf,player.playerrect)
            if (backgrounds[k].rect.right <= x + 250 * unitx):
                fade_surface.set_alpha(alpha)
                alpha += 5
                screen.blit(fade_surface, (0, 0))
            
          else:
              backgrounds[k].rect.bottomleft=(0,y)
              floors[l].rect.bottomleft=(0,y)
              k+=1
              l+=1
              k%=4
              l%=2
              alpha=0
              player.playerrect.left=10*unitx
    if immortal:
        if(immortaltime>=2000):immortal=False
        immortaltime+=dt
    if playerattack:
        if player.index>=len(player_attack):
            immortal=True
            playerattack=False    
    if question_scrn:
        screen.blit(board.frameF,board.rect)
        if(kpressed[pygame.K_o]):
            player.playerrect.bottom=ground
            player.index=0
            playerattack=True
            immortaltime=0
            question_scrn=False 
        elif(kpressed[pygame.K_i]):
            #enemy1.enemyrect.bottom=ground
            enemy1.index=0
            enemy2.index=0
            enemy3.index=0
            immortaltime=0
            enemyattack=True
            question_scrn=False 
    screen.blit(testtext,(10,10))

    pygame.display.update()