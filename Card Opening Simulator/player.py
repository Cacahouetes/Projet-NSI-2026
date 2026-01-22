from inventory import Inventory
from carddex import CardDex
from achievement_manager import AchievementManager
from achievement_check import check_after_chest, check_carddex_completion
from player_stats import PlayerStats

class Player:
    def __init__(self, coins=0, total_cards_in_dex=756):
        self.coins = coins
        self.inventory = Inventory()
        self.carddex = CardDex(total_cards_in_dex)
        self.achievements = set()
        self.stats = PlayerStats()
        self.achievement_manager = AchievementManager()

    def can_buy(self, cost):
        return self.coins >= cost

    def buy_chest(self, chest):
        if not self.can_buy(chest.cost):
            raise ValueError("Pas assez de pièces pour acheter ce coffre")

        self.coins -= chest.cost
        self.stats.coins_spent += chest.cost
        
        self.inventory.add_cards(chest.cards)
        
        self.stats.chests_opened += 1
        self.stats.chests_by_type[chest.type] += 1
        self.stats.cards_from_chests += len(chest.cards)
        
        for card in chest.cards:
            self.carddex.add_card(card)
            self.stats.cards_obtained += 1
            self.stats.cards_by_rarity[card.rarity] += 1
            
            if card.category:
                self.stats.cards_by_category[card.category] += 1
                
            if card.rarity.name == "DIVINE":
                self.stats.divine_obtained += 1
            
            check_after_chest(self, chest.cards)
            check_carddex_completion(self)
            
    def player_sell_card(self, card):
        value = self.inventory.sell_card(card)
        if value:
            self.coins += value
            self.stats.cards_sold += 1
            self.stats.cards_sold_by_rarity[card.rarity] += 1
            self.stats.coins_from_sales += value
            self.stats.coins_earned += value
            
    def player_fuse_card(self, rarity):
        success, cost = self.inventory.fuse_cards(self.coins, rarity)

        if cost:
            self.coins -= cost
            self.stats.coins_spent += cost
            self.stats.fusions_attempted += 1
            self.stats.fusions_by_rarity[rarity] += 1

            if success:
                self.stats.fusions_success += 1
            else:
                self.stats.fusions_failed += 1

    def check_achievement(self):
        return self.achievement_manager.check_all(self)
            
    def check_carddex_completion(self):
        if self.carddex.is_complete() and not self.carddex.diploma_unlocked:
            self.carddex.diploma_unlocked = True
            return True
        return False