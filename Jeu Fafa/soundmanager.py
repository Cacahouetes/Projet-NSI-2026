import pygame
from enum import Enum
class SoundManager:
    def __init__(self):
        self.evts = Enum('evts', [('ENNEMY_TAKE_DAMAGE', 0), ('PLAYER_TAKE_DAMAGE', 1)])
        #self.dmgsfx = pygame.mixer.Sound("Assets/jeu arcade/sfx/no.wav")
        #self.ensfx =  pygame.mixer.Sound("Assets/jeu arcade/sfx/yes.wav")

    def eventGet(self, event):

        if event.value == self.evts['PLAYER_TAKE_DAMAGE'].value:
            pass
            #self.dmgsfx.play()
        
        elif event.value == self.evts['ENNEMY_TAKE_DAMAGE'].value:
            pass
            #self.ensfx.play()