import pygame
from enum import Enum
class SoundManager:
    def __init__(self, eventm):
        self.eventman = eventm
        #self.dmgsfx = pygame.mixer.Sound("Assets/jeu arcade/sfx/no.wav")
        #self.ensfx =  pygame.mixer.Sound("Assets/jeu arcade/sfx/yes.wav")

    def eventGet(self, event):

        if event.value == self.eventman.evts['PLAYER_TAKE_DAMAGE'].value:
            pass
            #self.dmgsfx.play()
        
        elif event.value == self.eventman.evts['ENNEMY_TAKE_DAMAGE'].value:
            pass
            #self.ensfx.play()
        
        elif event.value == self.eventman.evts['PLAYER_GET_THING'].value:
            pass
            #self.ensfx.play()