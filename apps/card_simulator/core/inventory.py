import random as rd
from collections import defaultdict

from card import Card, Rarity, RARITY_SELL_VALUE

# ---------------------------------------------------------------------------
# Table de fusion
# needed  : nombre de cartes nécessaires
# success : probabilité de réussite (0-1)
# cost    : coût en pièces (4× valeur de revente)
# result  : rareté obtenue en cas de succès
# ---------------------------------------------------------------------------
FUSION_RULES = {
    Rarity.COMMUNE:    {"needed": 3, "success": 1.00, "cost": 4 * RARITY_SELL_VALUE[Rarity.COMMUNE],    "result": Rarity.RARE},
    Rarity.RARE:       {"needed": 3, "success": 0.90, "cost": 4 * RARITY_SELL_VALUE[Rarity.RARE],       "result": Rarity.ÉPIQUE},
    Rarity.ÉPIQUE:     {"needed": 3, "success": 0.25, "cost": 4 * RARITY_SELL_VALUE[Rarity.ÉPIQUE],     "result": Rarity.LÉGENDAIRE},
    Rarity.LÉGENDAIRE: {"needed": 3, "success": 0.15, "cost": 4 * RARITY_SELL_VALUE[Rarity.LÉGENDAIRE], "result": Rarity.MYTHIQUE},
    Rarity.MYTHIQUE:   {"needed": 3, "success": 0.05, "cost": 4 * RARITY_SELL_VALUE[Rarity.MYTHIQUE],   "result": Rarity.UNIQUE},
}


class CardDex:
    """Suivi des cartes découvertes au moins une fois."""

    def __init__(self, total_cards: int):
        self.total_cards       = total_cards
        self.collected_cards   = set()   # ensemble de card_id
        self.diploma_unlocked  = False

    def add_card(self, card: Card):
        self.collected_cards.add(card.card_id)

    def completion_percentage(self) -> float:
        return (len(self.collected_cards) / self.total_cards) * 100

    def is_complete(self) -> bool:
        return len(self.collected_cards) == self.total_cards

    def __repr__(self):
        return (f"CardDex({len(self.collected_cards)}/{self.total_cards} "
                f"– {self.completion_percentage():.1f}%)")


class Inventory:
    """Inventaire des cartes possédées par le joueur."""

    def __init__(self):
        self.cards: list[Card] = []

    # -----------------------------------------------------------------------
    # Ajout
    # -----------------------------------------------------------------------
    def add_card(self, card: Card):
        self.cards.append(card)

    def add_cards(self, cards: list[Card]):
        self.cards.extend(cards)

    # -----------------------------------------------------------------------
    # Vente unitaire
    # Retourne la valeur obtenue ou False en cas d'échec
    # -----------------------------------------------------------------------
    def sell_card(self, card: Card):
        if card not in self.cards:
            return False
        value = RARITY_SELL_VALUE.get(card.rarity)
        if value is None:          # DIVINE → invendable
            return False
        self.cards.remove(card)
        return value

    # -----------------------------------------------------------------------
    # Vente en masse par rareté
    # Retourne le total de pièces obtenu ou False si rareté invendable
    # -----------------------------------------------------------------------
    def sell_all_by_rarity(self, rarity: Rarity):
        value = RARITY_SELL_VALUE.get(rarity)
        if value is None:
            return False
        to_sell = [c for c in self.cards if c.rarity == rarity]
        gained  = len(to_sell) * value
        self.cards = [c for c in self.cards if c.rarity != rarity]
        return gained

    # -----------------------------------------------------------------------
    # Statistiques
    # -----------------------------------------------------------------------
    def count_by_rarity(self) -> dict:
        counts = defaultdict(int)
        for card in self.cards:
            counts[card.rarity] += 1
        return counts

    def total_value(self) -> int:
        return sum(
            RARITY_SELL_VALUE[c.rarity]
            for c in self.cards
            if RARITY_SELL_VALUE.get(c.rarity) is not None
        )

    # -----------------------------------------------------------------------
    # Fusion
    # Retourne (success: bool, cost: int)
    # cost == 0 signifie que la fusion n'a pas pu être lancée
    # -----------------------------------------------------------------------
    def fuse_cards(self, coins_available: int, rarity: Rarity):
        if rarity not in FUSION_RULES:
            raise ValueError(f"Impossible de fusionner la rareté : {rarity.name}")

        rule         = FUSION_RULES[rarity]
        needed       = rule["needed"]
        cost         = rule["cost"]
        success_rate = rule["success"]
        result_rarity = rule["result"]

        available = [c for c in self.cards if c.rarity == rarity]
        if len(available) < needed:
            return False, 0

        if coins_available < cost:
            return False, 0

        # Retirer les cartes utilisées
        for _ in range(needed):
            self.cards.remove(available.pop())

        # Résoudre le succès
        if rd.random() < success_rate:
            # Tirer une vraie carte depuis la DB (card_id réel requis pour PLAYER_FUSIONS)
            try:
                from card_repository import CardRepository
                new_card = CardRepository().get_random_card(result_rarity)
            except Exception:
                # Fallback carte fantôme si la DB est inaccessible
                new_card = Card(
                    card_id=None, name="???", rarity=result_rarity,
                    category=None, stat1=0, stat2=0, stat3=0,
                    description="", author="", image_path=""
                )
            self.cards.append(new_card)
            return True, cost

        return False, cost

    # -----------------------------------------------------------------------
    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Inventory({len(self.cards)} cartes)"