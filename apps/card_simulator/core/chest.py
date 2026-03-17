from enum import Enum

class ChestType(Enum):
    NORMAL = 1
    GOD = 2
    DIVINE = 3

class Chest:
    def __init__(self, type, category, cards, cost):
        self.type = type
        self.category = category
        self.cards = cards
        self.cost = cost

    def __len__(self):
        return len(self.cards)
    
    def __repr__(self):
        cat = self.category if self.category else "OMNI"
        return f"Chest type={self.type} category={cat} cost={self.cost} cards={len(self.cards)}"