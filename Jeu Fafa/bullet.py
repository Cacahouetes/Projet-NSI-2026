import pygame 

class Bullet(pygame.sprite.Sprite):
    def __init__(self, posx, posy, bDir):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([15, 5])
        self.image.fill((255,255,0))

        self.dir = bDir
        self.rect = self.image.get_rect()
        self.vPos = [posx, posy]

    def update(self, delta):
        self.vPos[0] += 3 * delta * self.dir
        self.rect.centerx = self.vPos[0]
        self.rect.centery = self.vPos[1]
        #if abs(self.vPos[0]) > 10000:
            
