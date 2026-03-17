import pygame
import os
from math import sin

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "assets", "arcade_game"))


class Collectible(pygame.sprite.Sprite):
    def loadimg(self, name):
        return pygame.image.load(os.path.join(ASSETS_DIR, "collec", name)).convert_alpha()

    def __init__(self, x, y, ctype):
        pygame.sprite.Sprite.__init__(self)

        self.imgs = [self.loadimg("point.png"), self.loadimg("health.png"), self.loadimg("flyg.png"), self.loadimg("akgun.png")]

        self.ctype = ctype
        self.image = self.imgs[self.ctype]
        self.rect = self.image.get_rect()

        self.posX = x 
        self.posY = y
        self.posYbase = self.posY
        self.tick = 0
        self.velocity = [0,0]

    def update(self, scroll, delta):
        self.posY = self.posYbase + sin(self.tick/10) * 8
        self.move(scroll,delta)
        self.tick += 1

    def move(self, scroll, delta):
        
        self.rect.centerx = self.posX - scroll.x
        self.rect.centery = self.posY - scroll.y
        
        self.posX = self.rect.centerx + scroll.x
        self.posY = self.rect.centery + scroll.y
