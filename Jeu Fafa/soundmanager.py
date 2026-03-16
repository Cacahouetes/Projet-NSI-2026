import pygame
from enum import Enum
from random import randint
def mksnd(path, vol):
    """Crée un nouveau objet son et le retourne. """
    snd = pygame.mixer.Sound(f"Assets/jeu arcade/sfx/{path}.wav")
    snd.set_volume(vol)
    return snd


class SoundManager:
    def PlaySound(self, soundfile):
        soundfile.stop()
        soundfile.play()

    def __init__(self, eventm):
        self.eventMan = eventm
        self.dmgsfx = [mksnd("aie1", 0.4),mksnd("aie2", 0.4),mksnd("aie3", 0.4),mksnd("aie4", 0.4)]
        self.entdmgsfx = [mksnd("zombhurt1", 0.3),mksnd("zombhurt2", 0.3),mksnd("zombhurt3", 0.3),mksnd("zombhurt4", 0.3), mksnd("zombhurt5", 0.3)]
        
        self.getsfx = mksnd("point", 0.7)
        self.getHpSFX = mksnd("get_health", 1)
        self.getGunSFX = mksnd("new_gun", 1)
        self.changeGunSFX = mksnd("change_gun", 0.5)

        self.firesfx = mksnd("fire", 0.2)

        self.walksfx = mksnd("walking", 0.8)
        self.jumpsfx = mksnd("jump", 0.4)
        
        self.wavendsfx = mksnd("new_wave", 1)

        self.dedsfx = mksnd("mort", 0.6)

    def eventGet(self, event):

        match event:
            
            case self.eventMan.evts.PLAYER_TAKE_DAMAGE:
                r = randint(0,3)
                self.PlaySound(self.dmgsfx[r])
            
            case self.eventMan.evts.ENNEMY_TAKE_DAMAGE:
                r = randint(0,4)
                self.PlaySound(self.entdmgsfx[r])
            
            case self.eventMan.evts.PLAYER_GET_PT:
                self.PlaySound(self.getsfx)
            
            case self.eventMan.evts.PLAYER_GET_HEALTH:
                self.PlaySound(self.getHpSFX)
            
            case self.eventMan.evts.PLAYER_FIRE:
                self.PlaySound(self.firesfx)
            
            case self.eventMan.evts.PLAYER_WALK_START:
                self.walksfx.play()
                
            case self.eventMan.evts.PLAYER_WALK_STOP:
                self.walksfx.stop()
            
            case self.eventMan.evts.PLAYER_LAND:
                self.PlaySound(self.getsfx)
            
            case self.eventMan.evts.PLAYER_JUMP:
                self.PlaySound(self.jumpsfx)
            
            case self.eventMan.evts.PLAYER_DEAD:
                self.PlaySound(self.dedsfx)
            
            case self.eventMan.evts.WAVE_END:
                self.PlaySound(self.wavendsfx)
            
            case self.eventMan.evts.PLAYER_JUMP:
                self.PlaySound(self.jumpsfx)
            
            case self.eventMan.evts.PLAYER_DEAD:
                self.PlaySound(self.dedsfx)
            
            case self.eventMan.evts.WAVE_END:
                self.PlaySound(self.wavendsfx)
            
            case self.eventMan.evts.CHANGE_GUN:
                self.PlaySound(self.changeGunSFX)
        
        

