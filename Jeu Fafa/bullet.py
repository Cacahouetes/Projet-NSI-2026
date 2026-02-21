import pygame 
from math import cos, sin
class Bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy, bDir):
        pygame.sprite.Sprite.__init__(self)
        self.type = 2 #bullet
        self.image = pygame.Surface([5, 5])
        self.image.fill((255,255,0))

        self.dir = bDir
        self.rect = self.image.get_rect()
        self.rectbefore = self.image.get_rect()
        self.vPos = [int(posx), int(posy)]
        self.velocity = [0,0]

    def update(self, delta, scroll):
    
        self.velocity[0] = 3 * delta * cos(self.dir)
        self.velocity[1] = 3 * delta * sin(self.dir)

        self.movewCollision(scroll)

        #self.image = pygame.Surface([5, 5])
        #self.image.fill((255,255,0))
        #self.image = pygame.transform.rotate(self.image, self.dir*180/3.14159265)
        
    def movewCollision(self,  scroll):

        self.rect.x = self.vPos[0] - scroll.x
        self.rect.y = self.vPos[1] - scroll.y

        self.rectbefore.x = self.rect.x 
        self.rectbefore.y = self.rect.y

        self.rect.x += self.velocity[0]
        self.rect.y -= self.velocity[1] 

        self.vPos[0] = self.rect.x + scroll.x
        self.vPos[1] = self.rect.y + scroll.y
            
