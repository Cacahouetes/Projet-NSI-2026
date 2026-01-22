from collections import defaultdict
import time

class PlayerStats:
    def __init__(self):
        # Global
        self.created_at = time.time()
        self.play_time = 0

        # Coffres
        self.chests_opened = 0
        self.chests_by_type = defaultdict(int)
        self.cards_from_chests = 0

        # Cartes
        self.cards_obtained = 0
        self.cards_by_rarity = defaultdict(int)
        self.cards_by_category = defaultdict(int)
        self.divine_obtained = 0

        # Shop
        self.shop_cards_bought = 0
        self.coins_spent_shop = 0

        # Économie
        self.coins_earned = 0
        self.coins_spent = 0
        self.coins_from_sales = 0

        # Ventes
        self.cards_sold = 0
        self.cards_sold_by_rarity = defaultdict(int)

        # Fusions
        self.fusions_attempted = 0
        self.fusions_success = 0
        self.fusions_failed = 0
        self.fusions_by_rarity = defaultdict(int)

        # Progression
        self.max_coins_held = 0
        self.achievements_unlocked = 0
        
    def fusion_success_rate(self):
        if self.fusions_attempted == 0:
            return 0
        return self.fusions_success / self.fusions_attempted

    def average_cards_per_chest(self):
        if self.chests_opened == 0:
            return 0
        return self.cards_from_chests / self.chests_opened

    def economy_balance(self):
        return self.coins_earned - self.coins_spent