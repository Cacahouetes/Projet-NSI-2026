import pygame
from enum import Enum
class ScreenEffects(pygame.sprite.Sprite):

    def __init__(self, eventman, lvl):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([1920, 1080]).convert_alpha()
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.tick = 100
        self.eventman = eventman
        self.level = lvl

        self.fontBig = pygame.font.Font("Assets/jeu arcade/FONT.ttf", 80)
        self.fontSmall = pygame.font.Font("Assets/jeu arcade/FONT.ttf", 25)
        self.isNewWave = False        
        self.flashType =  Enum('flashType', [('dmg',0),('new_gun',1), ('hp',2), ('dead', 3)])
        self.currFlash = self.flashType['dmg']

    def update(self):
        
        self.tick += 1
        self.image.fill((0,0,0,0))
        if self.isNewWave:
            txt = self.fontBig.render(f"Vague {self.level.waveN+1}.", True, (222,222,222))
            
            txt.fill((255, 255, 255, min(255,self.tick**1.5)), None, pygame.BLEND_RGBA_MULT)
            self.image.blit(txt, (1280/2-txt.get_width()/2, 720/2-txt.get_height()/2))
        else:
            val = max(0, 255-self.tick**2)

            match self.currFlash.value:

                case 0: #j'etais obligé d'utiliser des chiffres, sinon ça faisait un bug bizarre
                    self.image.fill((val,0,0, val))

                case 1:
                    self.image.fill((0,0,50, val))
                
                case 2:
                    self.image.fill((0,150,0, val))
                
                case 3:
                    self.image.fill((124,54,54, 100))
                    ded = self.fontBig.render(f"Vous êtes mort.", True, (220,175,175))
                    self.image.blit(ded, (1280/2-ded.get_width()/2, 720/2 - ded.get_height()/2))

                    ded = self.fontSmall.render(f"R pour rejouer. ", True, (175,150,150))
                    self.image.blit(ded, (1280/2-ded.get_width()/2, 720/2 - ded.get_height()/2+50))
        
        scr = self.fontSmall.render(f"Score: {self.level.player.score}", True, (222,222,0))
        self.image.blit(scr, (1280-scr.get_width()*1.2, 60))


    def eventGet(self, event):
        if event.value == self.eventman.evts['WAVE_END'].value:
            self.isNewWave = True
            self.tick = 0
        if event.value == self.eventman.evts['NEW_WAVE'].value:
            self.isNewWave = False

        if event.value == self.eventman.evts['PLAYER_TAKE_DAMAGE'].value:
            self.currFlash = self.flashType['dmg']
            self.tick = 10
        
        if event.value == self.eventman.evts['PLAYER_GET_HEALTH'].value:
            self.currFlash = self.flashType['hp']
            self.tick = 10

        if event.value == self.eventman.evts['PLAYER_GET_NEW_AK'].value or event.value == self.eventman.evts['PLAYER_GET_NEW_FLY'].value:
            self.currFlash = self.flashType['new_gun']
            self.tick = 10

        if event.value == self.eventman.evts['PLAYER_DEAD'].value:
            self.currFlash = self.flashType['dead']
