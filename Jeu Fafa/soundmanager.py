import pygame
import os
from enum import Enum
from random import randint
def mksnd(path, vol):
    """Crée un nouveau objet son et le retourne. """
    snd = pygame.mixer.Sound(os.sep.join(["Assets","jeu arcade","sfx", f"{path}.wav"]))
    snd.set_volume(vol)
    return snd


class SoundManager:
    def PlaySound(self, soundfile):
        soundfile.stop()
        soundfile.play()

    def __init__(self, eventm):
        pygame.mixer.init()
        
        self.eventMan = eventm
        self.eventMan.eventObjects.append(self)

        self.dmgSFX = [mksnd("aie1", 0.4),mksnd("aie2", 0.4),mksnd("aie3", 0.4),mksnd("aie4", 0.4)]
        self.entdmgSFX = [mksnd("zombhurt1", 0.3),mksnd("zombhurt2", 0.3),mksnd("zombhurt3", 0.3),mksnd("zombhurt4", 0.3), mksnd("zombhurt5", 0.3)]
        
        self.getSFX = mksnd("point", 0.7)
        self.getHpSFX = mksnd("get_health", 1)
        self.landSFX = mksnd("land", 0.2)
        self.getGunSFX = mksnd("new_gun", 1)
        self.changeGunSFX = mksnd("change_gun", 0.5)

        self.fireSFX = mksnd("fire", 0.2)

        self.walkSFX = mksnd("walking", 0.8)
        self.jumpSFX = mksnd("jump", 0.4)
        
        self.wavendSFX = mksnd("new_wave", 1)

        self.dedSFX = mksnd("mort", 0.6)

        self.PlayMusic()
        
    
    def PlayMusic(self):
        pygame.mixer.music.load(os.sep.join(["Assets", "jeu arcade", "musique", "onlyvoicemusic.mp3"]))
        pygame.mixer.music.play(-1) #-1 pour mettre la musique en boucle

    def eventGet(self, event):

        match event:
            
            case self.eventMan.evts.PLAYER_TAKE_DAMAGE:
                r = randint(0,3)
                self.PlaySound(self.dmgSFX[r])
            
            case self.eventMan.evts.ENNEMY_TAKE_DAMAGE:
                r = randint(0,4)
                self.PlaySound(self.entdmgSFX[r])
            
            case self.eventMan.evts.PLAYER_GET_PT:
                self.PlaySound(self.getSFX)
            
            case self.eventMan.evts.PLAYER_GET_HEALTH:
                self.PlaySound(self.getHpSFX)
            
            case self.eventMan.evts.PLAYER_FIRE:
                self.PlaySound(self.fireSFX)
            
            case self.eventMan.evts.PLAYER_WALK_START:
                self.walkSFX.play()
            
            case self.eventMan.evts.PLAYER_LAND:
                self.PlaySound(self.landSFX)
            
            case self.eventMan.evts.PLAYER_JUMP:
                self.walkSFX.stop()
                self.PlaySound(self.jumpSFX)
            
            case self.eventMan.evts.PLAYER_DEAD:
                self.PlaySound(self.dedSFX)
            
            case self.eventMan.evts.WAVE_END:
                self.PlaySound(self.wavendSFX)
            
            case self.eventMan.evts.PLAYER_JUMP:
                self.PlaySound(self.jumpSFX)
            
            case self.eventMan.evts.PLAYER_DEAD:
                self.PlaySound(self.dedSFX)
            
            case self.eventMan.evts.WAVE_END:
                self.PlaySound(self.wavendSFX)
            
            case self.eventMan.evts.CHANGE_GUN:
                self.PlaySound(self.changeGunSFX)
        
        

