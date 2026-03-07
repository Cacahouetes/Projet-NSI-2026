import pygame
class ScreenEffects(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([1920, 1080]).convert_alpha()
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.tick = 0
        self.isPlDmgState = False
        

    def update(self):
        val = max(0, 255-self.tick**2)
        if self.isPlDmgState:
            self.image.fill((val,0,0, val))
        else:
            self.image.fill((val,val,val, val))

        self.tick += 1

    def eventGet(self, event):
        if event.value == 2000: #player fire event
            self.isPlDmgState = False
            self.tick = 10
        if event.value == 1: #player damage event
            self.isPlDmgState = True
            self.tick = 10