import pygame
from enum import Enum
class SoundManager:
    def __init__(self):
        self.evts = Enum('evts', [('ENNEMY_TAKE_DAMAGE', 0), ('PLAYER_TAKE_DAMAGE', 1)])
        self.dmgsfx = pygame.mixer.Sound("Assets/jeu arcade/sfx/no.wav")
        self.ensfx =  pygame.mixer.Sound("Assets/jeu arcade/sfx/yes.wav")

    def play_sfx(self, val):

        if val.value == self.evts['PLAYER_TAKE_DAMAGE'].value:
            self.dmgsfx.play()
        
        elif val.value == self.evts['ENNEMY_TAKE_DAMAGE'].value:
            self.ensfx.play()