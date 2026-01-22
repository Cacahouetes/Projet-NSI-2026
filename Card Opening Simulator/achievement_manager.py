from achievement import ACHIEVEMENTS

class AchievementManager:
    def check_all(self, player):
        unlocked = []
        
        for achievement in ACHIEVEMENTS:
            if achievement.id in player.achievements:
                continue
            
            if achievement.condition(player.stats):
                player.achievements.add(achievement.id)
                player.stats.achievements_unlocked += 1
                unlocked.append(achievement)

        return unlocked