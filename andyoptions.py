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
pygame.display.update()