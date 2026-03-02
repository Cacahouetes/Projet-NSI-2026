from soundmanager import SoundManager
from enum import Enum

class EventManager:
    def __init__(self):
        self.evts = Enum('evts', [('ENNEMY_TAKE_DAMAGE', 0), ('PLAYER_TAKE_DAMAGE', 1)])
        self.soundman = SoundManager()
        self.currEvts = [False, False]
    
    def broadcast(self, event):
        self.currEvts[event.value] = True
        self.soundman.play_sfx(event)


