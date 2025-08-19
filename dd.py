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
#font
font1=pygame.font.Font("Assets/Fonts/1.TTF",50)

#physics variables
player_vel_y = 0  
gravity = 1 * unity  
jump_strength = -25 * unity

#Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x,y))
fade_surface.fill((0, 0, 0)) 
fade_surface.set_alpha(0)
alpha=0

#player variables
framesize=(1.7*unitx,2.6*unity)


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
    def __init__(self,size,path):
        self.size=size
        self.path=path
        self.frameF=pygame.image.load(path).convert_alpha()
        self.frameF=pygame.transform.scale(self.frameF,(self.frameF.get_width()*size[0],self.frameF.get_height()*size[1]))
        self.frameB=pygame.transform.flip(self.frameF,1,0)
        self.rect=self.frameF.get_rect(bottomleft=(0,ground))

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

#player animations lists
player_run=[Frame(framesize,"Assets/Player/run/1.png"),
            Frame(framesize,"Assets/Player/run/2.png"),
            Frame(framesize,"Assets/Player/run/3.png"),
            Frame(framesize,"Assets/Player/run/4.png"),
            Frame(framesize,"Assets/Player/run/5.png"),
            Frame(framesize,"Assets/Player/run/6.png"),
            Frame(framesize,"Assets/Player/run/7.png"),
            Frame(framesize,"Assets/Player/run/8.png")]    

player_jump=[Frame(framesize,"Assets/Player/jump/1.png"),
             Frame(framesize,"Assets/Player/jump/2.png"),
             Frame(framesize,"Assets/Player/jump/3.png"),
             Frame(framesize,"Assets/Player/jump/4.png"),
             Frame(framesize,"Assets/Player/jump/5.png"),
             Frame(framesize,"Assets/Player/jump/6.png"),
             Frame(framesize,"Assets/Player/jump/7.png"),
             Frame(framesize,"Assets/Player/jump/8.png"),
            ]

player_idle=[Frame(framesize,"Assets/Player/idle/1.png"),
             Frame(framesize,"Assets/Player/idle/2.png"),
             Frame(framesize,"Assets/Player/idle/3.png"),
             Frame(framesize,"Assets/Player/idle/4.png"),
             Frame(framesize,"Assets/Player/idle/5.png"),
             Frame(framesize,"Assets/Player/idle/6.png"),
             Frame(framesize,"Assets/Player/idle/7.png"),
             Frame(framesize,"Assets/Player/idle/8.png"),
             Frame(framesize,"Assets/Player/idle/8.png")]

player_shot=[Frame(framesize,"Assets/Player/shot/1.png"),
             Frame(framesize,"Assets/Player/shot/2.png"),
             Frame(framesize,"Assets/Player/shot/3.png"),
             Frame(framesize,"Assets/Player/shot/4.png"),
             Frame(framesize,"Assets/Player/shot/5.png"),
             Frame(framesize,"Assets/Player/shot/6.png"),
             Frame(framesize,"Assets/Player/shot/7.png"),
             Frame(framesize,"Assets/Player/shot/8.png"),
             Frame(framesize,"Assets/Player/shot/9.png"),
             Frame(framesize,"Assets/Player/shot/10.png"),
             Frame(framesize,"Assets/Player/shot/11.png"),
             Frame(framesize,"Assets/Player/shot/12.png"),
             Frame(framesize,"Assets/Player/shot/13.png")]

player_hurt=[Frame(framesize,"Assets/Player/hurt/1.png"),
             Frame(framesize,"Assets/Player/hurt/2.png"),
             Frame(framesize,"Assets/Player/hurt/3.png")]

player_death=[Frame(framesize,"Assets/Player/death/1.png"),
              Frame(framesize,"Assets/Player/death/2.png"),
              Frame(framesize,"Assets/Player/death/3.png"),
              Frame(framesize,"Assets/Player/death/4.png"),
              Frame(framesize,"Assets/Player/death/5.png")]

player_knee=[Frame(framesize,"Assets/Player/knee/1.png"),
             Frame(framesize,"Assets/Player/knee/2.png")]        


#animation class
class Animation:
    def __init__(self,index=0,front=True,playersuf=player_idle[0].frameF,playerrect=player_idle[0].rect):
        self.index=index
        self.front=front
        self.playersuf=playersuf
        self.playerrect=playerrect
        self.vel_y = 0
    def createanimaion(self, rect,onground,kpressed):

        if(kpressed[pygame.K_d] ):
            self.front=True
            self.playersuf=player_run[int(self.index)].frameF
            self.playerrect=self.playersuf.get_rect(bottomleft=rect)
            backgrounds[k].move(True)
            floors[l].move(True)
            if self.playerrect.right<=x-(unitx*150):self.playerrect.left+=5

        elif(kpressed[pygame.K_a]):
            self.front= False
            self.playersuf=player_run[int(self.index)].frameB
            self.playerrect=self.playersuf.get_rect(bottomleft=rect)
            if self.playerrect.left>x-980*unitx:
                backgrounds[k].move(False)
                floors[l].move(False)
                self.playerrect.left-=5

        elif(kpressed[pygame.K_s]):
            self.index-=.02
            self.index%=len(player_knee)
            if(self.front):self.playersuf=player_knee[int(self.index)].frameF
            else:self.playersuf=player_knee[int(self.index)].frameB
            self.playerrect=self.playersuf.get_rect(bottomleft=rect)

        elif(onground):
            if(self.front):self.playersuf=player_idle[int(self.index)].frameF
            else: self.playersuf=player_idle[int(self.index)].frameB
            self.playerrect=self.playersuf.get_rect(bottomleft=rect)
            
        if(kpressed[pygame.K_w] and onground):
            self.vel_y=jump_strength
            self.index=0
            onground=False
            self.playerrect=player_jump[1].frameF.get_rect(bottomleft=rect)

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
        
        self.index+=0.1
        self.index%= len(player_run)
        return onground


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
q=600
while(True):
    rect=player.playerrect.bottomleft
    if(player.playerrect.bottom<q):q=player.playerrect.bottom
    dt=clock.tick(60)
    mouse = pygame.mouse.get_pos() 
    testtext=font1.render(f"curemo {current_emotion}  {unity}  {gravity} groun {ground} vbot {player.playerrect.bottom} ong {onground} b {backgrounds[k].rect.right}   mou{mouse}",False,"Black")
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
   
    # testtext = font1.render(
    # f"Emotion: {current_emotion}", 
    # True, 
    # "Black"
    # )
    # screen.blit(testtext, (10, 50))


    if start_scrn:
          if backgrounds[k].rect.right>=x:
            screen.blit(backgrounds[k].img,backgrounds[k].rect)
            screen.blit(floors[l].img,floors[l].rect)
            onground=player.createanimaion(rect,onground,kpressed)
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
    screen.blit(testtext,(10,10))


    pygame.display.update()