import pygame
from enum import Enum
from random import randint
def mksnd(path, vol):
    snd = pygame.mixer.Sound(f"Assets/jeu arcade/sfx/{path}.wav")
    snd.set_volume(vol)
    return snd
class SoundManager:
    def __init__(self, eventm):
        self.eventman = eventm
        self.dmgsfx = [mksnd("aie1", 0.4),mksnd("aie2", 0.4),mksnd("aie3", 0.4),mksnd("aie4", 0.4)]
        self.entdmgsfx = [mksnd("zombhurt1", 0.3),mksnd("zombhurt2", 0.3),mksnd("zombhurt3", 0.3),mksnd("zombhurt4", 0.3), mksnd("zombhurt5", 0.3)]
        
        self.getsfx = mksnd("land", 0.4)
        self.firesfx = mksnd("fire", 0.2)

        self.walksfx = mksnd("walking", 0.8)

    def eventGet(self, event):

        if event.value == self.eventman.evts['PLAYER_TAKE_DAMAGE'].value:
            r = randint(0,3)
            self.dmgsfx[r].stop()
            self.dmgsfx[r].play()
        
        elif event.value == self.eventman.evts['ENNEMY_TAKE_DAMAGE'].value:
            r = randint(0,4)
            self.entdmgsfx[r].stop()
            self.entdmgsfx[r].play()
        
        elif event.value == self.eventman.evts['PLAYER_GET_THING'].value:
            self.getsfx.stop()
            self.getsfx.play()
        
        elif event.value == self.eventman.evts['PLAYER_FIRE'].value:
            self.firesfx.stop()
            self.firesfx.play()
        
        elif event.value == self.eventman.evts['PLAYER_WALK_START'].value:
            self.walksfx.play()
            
        elif event.value == self.eventman.evts['PLAYER_WALK_STOP'].value:
            self.walksfx.stop()
