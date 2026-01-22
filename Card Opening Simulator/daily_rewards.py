import random as rd
import time
from card import Rarity, Card

# Durée d'un jour en secondes
DAY_DURATION = 86400

class DailyReward:
    def __init__(self, coins=0, cards=None, description=""):
        self.coins = coins
        self.cards = cards
        self.description = description
        
DAILY_REWARDS = [
    DailyReward(coins=100, description="Jour 1 : 100 pièces"),
    DailyReward(coins=150, description="Jour 2 : 150 pièces"),
    DailyReward(coins=200, cards=[Card(Rarity.COMMON)], description="Jour 3 : 200 pièces + 1 carte COMMON"),
    DailyReward(coins=250, cards=[Card(Rarity.RARE)], description="Jour 4 : 250 pièces + 1 carte RARE"),
    DailyReward(coins=300, cards=[Card(Rarity.EPIC)], description="Jour 5 : 300 pièces + 1 carte EPIC"),
    DailyReward(coins=350, cards=[Card(Rarity.LEGENDARY)], description="Jour 6 : 350 pièces + 1 carte LEGENDARY"),
    DailyReward(coins=500, cards=[Card(Rarity.MYTHIC)], description="Jour 7 : 500 pièces + 1 carte MYTHIC"),
]

class DailyRewardManager:
    def __init__(self):
        self.last_claim_time = 0
        self.day_index = 0

    def can_claim(self):
        return time.time() - self.last_claim_time >= DAY_DURATION

    def claim_reward(self, player):
        if not self.can_claim():
            remaining = DAY_DURATION - (time.time() - self.last_claim_time)
            raise ValueError(f"Récompense déjà réclamée. Reviens dans {int(remaining)} secondes.")

        reward = DAILY_REWARDS[self.day_index]
        player.coins += reward.coins
        for card in reward.cards:
            player.inventory.add_card(card)

        self.last_claim_time = time.time()
        self.day_index = (self.day_index + 1) % len(DAILY_REWARDS)
        return reward