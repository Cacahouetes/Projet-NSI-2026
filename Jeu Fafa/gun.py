import pygame
from math import sin, cos

class Gun():
    def loadimg(self, path):
        return pygame.image.load("Assets/jeu arcade/guns/"+path).convert_alpha()

    def __init__(self, evtm):
        self.imgs = [self.loadimg("gun.png"), self.loadimg("flygun.png"), self.loadimg("akgun.png")]
        self.currGunID = 2

        self.img = self.imgs[self.currGunID]

        self.rect = self.img.get_rect()
        self.tipx = 0
        self.tipy = 0
        self.angleOffset = 0
        self.eventman = evtm
        self.lastFireTime = -10000
        

    def eventGet(self, event):
        if event.value == self.eventman.evts['PLAYER_FIRE'].value:
            self.angleOffset = 20

    def update(self):
        pass

    def draw(self, win, player, angleDeg):
        self.rect.centerx = player.rect.centerx - self.img.get_width()/2
        self.rect.centery = player.rect.centery - self.img.get_height()/2

        rotated_gun = self.img.copy()

        if abs(angleDeg) > 90:
            rotated_gun = pygame.transform.flip(rotated_gun, False, True)
        rotated_gun = pygame.transform.rotate(rotated_gun, angleDeg + self.angleOffset * (-1 if abs(angleDeg) > 90 else 1))
        
        rot_gun_rect = rotated_gun.get_rect()
        
        offsetx = 0
        if abs(angleDeg) > 90:
            offsetx = -24
        else:
            offsetx = 24

        win.blit(rotated_gun, (player.rect.centerx - rotated_gun.get_width()/2 + offsetx, player.rect.centery - rotated_gun.get_height()/2))
        self.tipx = player.rect.centerx + 1*cos(angleDeg)
        self.tipy = player.rect.centery + 1*sin(angleDeg)
        
        self.angleOffset *= 0.8