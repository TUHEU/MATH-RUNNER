import pygame
import random
from sys import exit

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

#Creating background swap animation (Fadeout) variables
fade_surface = pygame.Surface((x,y))
fade_surface.fill((0, 0, 0)) 
fade_surface.set_alpha(0)
alpha=0


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


# player animations Frame class
class Frame:
    def __init__(self,size,path,pos_player):
        self.size=size
        self.path=path
        self.frame=pygame.image.load(path).convert_alpha()
        self.frame=pygame.transform.scale(self.frame,(self.frame.get_width()*size[0],self.frame.get_height()*size[1]))
        self.pos_player=pos_player
        self.rect=self.frame.get_rect(bottomleft=(0,y-100*unity))
    def flip(self):
        self.frame=pygame.transform.flip(self.frame,1,0)

#class background
class background:
    def __init__(self,path,speed,size):
        self.size=size
        self.speed=speed
        self.path=path
        self.img=pygame.image.load(path).convert_alpha()
        self.img=pygame.transform.scale(self.img,(size[0],size[1]))
        self.rect=self.img.get_rect(bottomleft=(0,y))
    def move(self):
        if(self.rect.right>=x):
            self.rect.left-=self.speed   

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
player_runF=[Frame((0.5,0.5),"Assets/Player/run/1.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/2.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/3.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/4.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/5.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/6.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/7.png",(0,0)),
            Frame((0.5,0.5),"Assets/Player/run/8.png",(0,0))]    
player_runB=[]
for fram in player_runF:
    player_runB.append(fram)

player_jumpF=[Frame((0.5,0.5),"Assets/Player/jump/1.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/2.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/3.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/4.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/5.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/6.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/7.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/8.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/jump/9.png",(0,0)),]
player_jumpB=[]
for fram in player_jumpF:
    player_jumpB.append(fram)


player_idleF=[Frame((0.5,0.5),"Assets/Player/idle/1.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/2.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/3.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/4.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/5.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/6.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/7.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/8.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/idle/8.png",(0,0))]
player_idleB=[]
for fram in player_idleF:
    player_idleB.append(fram)



player_shotF=[Frame((0.5,0.5),"Assets/Player/shot/1.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/2.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/3.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/4.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/5.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/6.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/7.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/8.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/9.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/10.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/11.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/12.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/shot/13.png",(0,0))]
player_shotB=[]
for fram in player_runF:
    player_shotB.append(fram)


player_hurtF=[Frame((0.5,0.5),"Assets/Player/hurt/1.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/hurt/2.png",(0,0)),
             Frame((0.5,0.5),"Assets/Player/hurt/3.png",(0,0))]
player_hurtB=[]
for fram in player_hurtF:
    player_hurtB.append(fram)


player_deathF=[Frame((0.5,0.5),"Assets/Player/death/1.png",(0,0)),
              Frame((0.5,0.5),"Assets/Player/death/2.png",(0,0)),
              Frame((0.5,0.5),"Assets/Player/death/3.png",(0,0)),
              Frame((0.5,0.5),"Assets/Player/death/4.png",(0,0)),
              Frame((0.5,0.5),"Assets/Player/death/5.png",(0,0))]
player_deathB=[]
for fram in player_deathF:
    player_deathB.append(fram)

                       
#animation class
class Animation:
    def __init__(self,index=0,front=True,playersuf=player_idleF[0]):
        self.index=index
        self.front=front
        self.playersuf=playersuf
    def createanimaion(self):
        if(kpressed[pygame.K_d]):
            self.front=True
            self.playersuf=player_runF[int(self.index)]
        elif(kpressed[pygame.K_a]):
            self.front= False
            self.playersuf=player_runB[int(self.index)]




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


while(True):
    dt=clock.tick(60)
    mouse = pygame.mouse.get_pos() 
    testtext=font1.render(f"alpha= {alpha}  b {backgrounds[k].rect.right}   mou{mouse}",False,"Black")
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

#start true
    if start_scrn:
          if backgrounds[k].rect.right>=x:
            backgrounds[k].move()
            floors[l].move()
            screen.blit(backgrounds[k].img,backgrounds[k].rect)
            screen.blit(floors[l].img,floors[l].rect)
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
    screen.blit(testtext,(10,10))

    pygame.display.update()