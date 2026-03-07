import pygame
from math import sin 
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([10,10])
        self.image.fill((40,40,40, 255))
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
