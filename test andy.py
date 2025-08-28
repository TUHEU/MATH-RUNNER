import pygame
from sys import exit
import random

pygame.init()
window=pygame.display.Info()
x=window.current_w
y=window.current_h
screen=pygame.display.set_mode((x,y))
clock=pygame.time.Clock() 
unitx=x/1000
unity=y/1000
font1=pygame.font.Font("Assets/Fonts/1.TTF",50)
font2=pygame.font.Font("Assets/Fonts/2.TTF",50)
font3=pygame.font.Font("Assets/Fonts/3.fon",150)


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


#Questions variables
questionsize=(unitx*1.2,2*unity)
position_question=(200*unitx,600*unity)
answer=''
answer_chosen=False
correction_delay=0
timer=30
second=0
seconds=0
minutes=0

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


#pages booleans
menu_scrn=True

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

equations=[equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC(),equationC()]

backgrounds=[background("Assets/Backgrounds/1.png",speedbk,sizebk),
             background("Assets/Backgrounds/2.png",speedbk,sizebk),
             background("Assets/Backgrounds/3.png",speedbk,sizebk),
             background("Assets/Backgrounds/4.png",speedbk,sizebk),]


#sounds
pygame.mixer.init()
# pygame.mixer.music.load('Assets\Sounds\touch.mp3')
# pygame.mixer.music.play()
# pygame.mixer.music.set_volume(0.25)

touch_sound=pygame.mixer.Sound("Assets/Sounds/touch.mp3")

menu=pygame.image.load("Assets/Menu/menu.jpg")
menu_rect=menu.get_rect(topleft=(0,0))
menu=pygame.transform.scale(menu,(x,y))
cur_equation=["","","","","","","","","","","","","",]
eqn_locx=[0,0,0,0,0,0,0,0,0,0,0,0,0]
eqn_locy=[0,0,0,0,0,0,0,0,0,0,0,0,0]
j=0
while True:
    dt=clock.tick(60)
    mouse = pygame.mouse.get_pos() 
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            exit
            pygame.quit
    screen.blit(menu,menu_rect)
    kpressed=pygame.key.get_pressed()
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
        if(kpressed==pygame.K_ESCAPE):
            pygame.quit()
            exit()
        for button in buttons:
            button.draw(screen)
            button.handle_event(event,mouse)
            if(button.handle_event(event,mouse)=="exit"):
                pygame.quit()
                exit()
            if(button.handle_event(event,mouse)=="start"):
                menu_scrn=False
                start_scrn=True
    pygame.display.update()


    ljsf;oiEOFGEJ