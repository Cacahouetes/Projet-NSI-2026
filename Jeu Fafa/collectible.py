import pygame
from math import sin 
class Collectible(pygame.sprite.Sprite):
    def loadimg(self, path):
        return pygame.image.load("Assets/jeu arcade/collec/"+path).convert_alpha()

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
