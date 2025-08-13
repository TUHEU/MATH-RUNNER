import pygame
import random
from sys import exit

pygame.display.init()
window=pygame.display.Info()
x=window.current_w
y=window.current_h
screen=pygame.display.set_mode((x,y))
clock=pygame.time.Clock() 
unitx=x/1000
unity=y/1000

#pages booleans
menu_scrn=True
#font
# font1=pygame.font.Font("Fonts/1.TTF")
                       
# class animation:
#     def __init__(self,eqaution="",num1=0,num2=0,sign="",ans=0):
#         self.equation=eqaution
#         self.num1=num1
#         self.num2=num2
#         self.sign=sign
#         self.ans=ans

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

#sounds
pygame.mixer.init()
# pygame.mixer.music.load('Assets\Sounds\touch.mp3')
# pygame.mixer.music.play()
# pygame.mixer.music.set_volume(0.25)

touch_sound=pygame.mixer.Sound("Assets\Sounds\\touch.mp3")

#menu
menu=pygame.image.load("Assets/Menu/menu.jpg")
menu_rect=menu.get_rect(topleft=(0,0))
menu=pygame.transform.scale(menu,(x,y))
while(True):
    mouse = pygame.mouse.get_pos() 
    kpressed=pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            exit()
    if(kpressed[pygame.K_ESCAPE]):
        pygame.quit()
        exit()
    screen.blit(menu,menu_rect)
    for button in buttons:
        button.draw(screen)
        button.handle_event(event,mouse)
        if(button.handle_event(event,mouse)=="exit"):
            pygame.quit()
            exit()
    pygame.display.update()
    clock.tick(60)