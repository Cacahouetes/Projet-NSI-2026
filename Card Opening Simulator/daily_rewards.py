import time
from card import Rarity, Card

# Durée d'un jour en secondes
DAY_DURATION = 86400

class DailyReward:
    def __init__(self, coins=0, card=None, description=""):
        self.coins = coins
        self.card = card
        self.description = description
        
DAILY_REWARDS = [
    DailyReward(coins=100, description="Jour 1 : 100 pièces"),
    DailyReward(coins=150, description="Jour 2 : 150 pièces"),
    DailyReward(coins=200, card=Card(Rarity.COMMON), description="Jour 3 : 200 pièces + 1 carte COMMON"),
    DailyReward(coins=250, card=Card(Rarity.RARE), description="Jour 4 : 250 pièces + 1 carte RARE"),
    DailyReward(coins=300, card=Card(Rarity.EPIC), description="Jour 5 : 300 pièces + 1 carte EPIC"),
    DailyReward(coins=350, card=Card(Rarity.LEGENDARY), description="Jour 6 : 350 pièces + 1 carte LEGENDARY"),
    DailyReward(coins=500, card=Card(Rarity.MYTHIC), description="Jour 7 : 500 pièces + 1 carte MYTHIC"),
]

class DailyRewardManager:
    def can_claim(self, player):
        return time.time() - player.stats.last_daily_timestamp >= DAY_DURATION

    def claim_reward(self, player):
        now = time.time()

        if not self.can_claim(player):
            remaining = int(DAY_DURATION - (now - player.stats.last_daily_timestamp))
            raise ValueError(f"Récompense déjà réclamée. Reviens dans {remaining} secondes.")
        
        if now - player.stats.last_daily_timestamp >= DAY_DURATION * 2:
            if player.stats.daily_current_streak > 0:
                player.stats.daily_streak_breaks += 1
            player.stats.daily_current_streak = 1

        else:
            player.stats.daily_current_streak += 1

        player.stats.daily_best_streak = max(player.stats.daily_best_streak, player.stats.daily_current_streak)

        player.stats.daily_claims_total += 1
        player.stats.last_daily_timestamp = now


        reward_index = (player.stats.daily_current_streak - 1) % len(DAILY_REWARDS)
        reward = DAILY_REWARDS[reward_index]

        player.coins += reward.coins
        player.stats.coin_earned += reward.coins

        player.inventory.add_card(reward.card)
        player.carddex.add_card(reward.card)
        player.stats.cards_obtained += 1
        player.stats.cards_by_rarity[reward.card.rarity] += 1
        player.stats.cards_by_category[reward.card.category] += 1

        return reward