import time
from collections import defaultdict

from inventory import Inventory, CardDex
from achievements import AchievementManager


class PlayerStats:
    def __init__(self):
        # ── Méta ───────────────────────────────────────────────────────────
        self.created_at          = time.time()
        self.play_time           = 0
        self.achievements        = set()       # ensemble d'achievement_id débloqués
        self.achievements_unlocked = 0
        self._carddex_pct        = 0.0         # injecté par AchievementManager

        # ── Coffres ────────────────────────────────────────────────────────
        self.chests_opened       = 0
        self.chests_by_type      = defaultdict(int)
        self.cards_from_chests   = 0

        # ── Cartes ─────────────────────────────────────────────────────────
        self.cards_obtained      = 0
        self.cards_by_rarity     = defaultdict(int)
        self.cards_by_category   = defaultdict(int)
        self.divine_obtained     = 0

        # ── Shop ───────────────────────────────────────────────────────────
        self.shop_cards_bought   = 0
        self.coins_spent_shop    = 0

        # ── Économie ───────────────────────────────────────────────────────
        self.coins_earned        = 0
        self.coins_spent         = 0
        self.coins_from_sales    = 0

        # ── Ventes ─────────────────────────────────────────────────────────
        self.cards_sold          = 0
        self.cards_sold_by_rarity = defaultdict(int)

        # ── Fusions ────────────────────────────────────────────────────────
        self.fusions_attempted   = 0
        self.fusions_success     = 0
        self.fusions_failed      = 0
        self.fusions_by_rarity   = defaultdict(int)

        # ── Progression ────────────────────────────────────────────────────
        self.max_coins_held      = 0

        # ── Daily Rewards ──────────────────────────────────────────────────
        self.daily_claims_total      = 0
        self.daily_current_streak    = 0
        self.daily_best_streak       = 0
        self.daily_streak_breaks     = 0
        self.last_daily_timestamp    = 0

    # ── Métriques calculées ────────────────────────────────────────────────
    def fusion_success_rate(self) -> float:
        if self.fusions_attempted == 0:
            return 0.0
        return self.fusions_success / self.fusions_attempted

    def average_cards_per_chest(self) -> float:
        if self.chests_opened == 0:
            return 0.0
        return self.cards_from_chests / self.chests_opened

    def economy_balance(self) -> int:
        return self.coins_earned - self.coins_spent


class Player:
    def __init__(self, player_id=None, coins=0, total_cards_in_dex=756):
        self.id                  = player_id
        self.coins               = coins
        self.inventory           = Inventory()
        self.carddex             = CardDex(total_cards_in_dex)
        self.stats               = PlayerStats()
        self.achievement_manager = AchievementManager()

    # -----------------------------------------------------------------------
    # Utilitaires
    # -----------------------------------------------------------------------
    def can_buy(self, cost: int) -> bool:
        return self.coins >= cost

    def _update_max_coins(self):
        if self.coins > self.stats.max_coins_held:
            self.stats.max_coins_held = self.coins

    # -----------------------------------------------------------------------
    # Achat de coffre
    # -----------------------------------------------------------------------
    def buy_chest(self, chest) -> list:
        if not self.can_buy(chest.cost):
            raise ValueError("Pas assez de pièces pour acheter ce coffre.")

        # Snapshot max AVANT le débit (le solde actuel est le plus haut à cet instant)
        self._update_max_coins()
        self.coins -= chest.cost
        self.stats.coins_spent += chest.cost

        self.inventory.add_cards(chest.cards)

        self.stats.chests_opened       += 1
        self.stats.chests_by_type[chest.type] += 1
        self.stats.cards_from_chests   += len(chest.cards)

        for card in chest.cards:
            self.carddex.add_card(card)
            self.stats.cards_obtained += 1
            self.stats.cards_by_rarity[card.rarity] += 1
            if card.category:
                self.stats.cards_by_category[card.category] += 1
            from card import Rarity
            if card.rarity == Rarity.DIVINE:
                self.stats.divine_obtained += 1

        return self.check_achievements()

    # -----------------------------------------------------------------------
    # Vente d'une carte
    # -----------------------------------------------------------------------
    def player_sell_card(self, card) -> bool:
        value = self.inventory.sell_card(card)
        if value is False:
            return False

        self.coins += value
        self.stats.cards_sold          += 1
        self.stats.cards_sold_by_rarity[card.rarity] += 1
        self.stats.coins_from_sales    += value
        self.stats.coins_earned        += value
        self._update_max_coins()
        return True

    # -----------------------------------------------------------------------
    # Vente en masse par rareté
    # -----------------------------------------------------------------------
    def player_sell_all_by_rarity(self, rarity) -> int:
        # Compter AVANT la vente pour avoir le nombre exact de cartes vendues
        count  = sum(1 for c in self.inventory.cards if c.rarity == rarity)
        gained = self.inventory.sell_all_by_rarity(rarity)
        if gained is False:
            return 0

        self.coins                       += gained
        self.stats.coins_from_sales      += gained
        self.stats.coins_earned          += gained
        self.stats.cards_sold            += count
        self.stats.cards_sold_by_rarity[rarity] += count
        self._update_max_coins()
        return gained

    # -----------------------------------------------------------------------
    # Fusion
    # -----------------------------------------------------------------------
    def player_fuse_card(self, rarity) -> tuple[bool, int]:
        success, cost = self.inventory.fuse_cards(self.coins, rarity)

        if cost == 0:
            return False, 0

        self.coins -= cost
        self.stats.coins_spent         += cost
        self.stats.fusions_attempted   += 1
        self.stats.fusions_by_rarity[rarity] += 1

        if success:
            self.stats.fusions_success += 1
        else:
            self.stats.fusions_failed  += 1

        return success, cost

    # -----------------------------------------------------------------------
    # Succès
    # -----------------------------------------------------------------------
    def check_achievements(self) -> list:
        """Vérifie et débloque les succès. Retourne la liste des nouveaux succès."""
        return self.achievement_manager.check_all(self)

    # -----------------------------------------------------------------------
    # CardDex
    # -----------------------------------------------------------------------
    def check_carddex_completion(self) -> bool:
        if self.carddex.is_complete() and not self.carddex.diploma_unlocked:
            self.carddex.diploma_unlocked = True
            return True
        return False

    # -----------------------------------------------------------------------
    def __repr__(self):
        return (f"Player(id={self.id}, coins={self.coins}, "
                f"cards={len(self.inventory)}, "
                f"carddex={self.carddex.completion_percentage():.1f}%)")