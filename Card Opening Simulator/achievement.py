from card import Rarity, Category

class Achievement:
    def __init__(self, id, name, description, condition):
        self.id = id
        self.name = name
        self.description = description
        self.condition = condition  # fonction(stats)

ACHIEVEMENTS = [
]