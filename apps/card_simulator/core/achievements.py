from card import Rarity, Category

class Achievement:
    def __init__(self, id, name, description, condition):
        self.id = id
        self.name = name
        self.description = description
        self.condition = condition  # fonction(stats)

ACHIEVEMENTS = [
]

class AchievementManager:
    def check_all(self, player):
        unlocked = []
        
        for achievement in ACHIEVEMENTS:
            if achievement.id in player.stats.achievements:
                continue
            
            if achievement.condition(player.stats):
                player.stats.achievements.add(achievement.id)
                player.stats.achievements_unlocked += 1
                unlocked.append(achievement)

        return unlocked

def after_chest(player):
    return player.check_achievements()

def after_fusion(player):
    return player.check_achievements()

def after_sale(player):
    return player.check_achievements()