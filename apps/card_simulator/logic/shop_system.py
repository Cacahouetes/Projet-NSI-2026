import random as rd
import time

from card import Rarity, Card, RARITY_SELL_VALUE
from card_repository import CardRepository

SHOP_PRICE_MULTIPLIER = 2
SHOP_RESTOCK_HOURS    = 24        # durée d'un stock en heures
SHOP_SIZE             = 3

SHOP_RARITY_WEIGHTS = [
    (0.02, Rarity.UNIQUE),
    (0.06, Rarity.MYTHIQUE),
    (0.12, Rarity.LÉGENDAIRE),
    (0.20, Rarity.ÉPIQUE),
    (0.30, Rarity.RARE),
    (1.00, Rarity.COMMUNE),
]

_REPOSITORY = CardRepository()


def _roll_shop_rarity() -> Rarity:
    roll = rd.random()
    cumul = 0.0
    for threshold, rarity in SHOP_RARITY_WEIGHTS:
        cumul += threshold
        if roll < cumul:
            return rarity
    return Rarity.COMMUNE


class ShopCard:
    def __init__(self, slot: int, card: Card, price: int):
        self.slot  = slot
        self.card  = card
        self.price = price


class Shop:
    """
    Le shop persiste ses cartes dans SHOP_CARDS en DB.
    À l'instanciation :
      1. Charge les slots existants depuis la DB (si encore valides)
      2. Si vides ou expirés → génère de nouvelles cartes et les écrit en DB
    """

    def __init__(self, player_id: int = None):
        self.player_id   = player_id
        self.last_restock = time.time()
        self.shop_cards: list[ShopCard] = []
        self._load_or_generate()

    # ── Chargement / génération ──────────────────────────────────────────
    def _load_or_generate(self):
        import database_manager as db
        rows = db.db_load_shop() if self.player_id is not None else []

        now = int(time.time())

        if rows:
            # Des lignes existent → un cycle est en cours ou vient d expirer
            any_expired = any(r["available_until"] <= now for r in rows)

            if any_expired:
                # Toutes les lignes partagent le même available_until → cycle expiré → restock
                self._generate_and_save()
            else:
                # Cycle actif : charger uniquement les slots non encore vendus
                self.last_restock = rows[0]["available_until"] - SHOP_RESTOCK_HOURS * 3600
                for row in rows:
                    if row["sold"] == 0:
                        card = _REPOSITORY.get_card_by_id(row["card_id"])
                        if card:
                            self.shop_cards.append(ShopCard(row["shop_slot"], card, row["price"]))
                # Si tous sold=1 → shop vide pour ce cycle, on ne restock PAS
        else:
            # Aucune ligne → premier lancement
            self._generate_and_save()

    def _generate_and_save(self):
        import database_manager as db
        self.shop_cards   = []
        self.last_restock = time.time()
        available_until   = int(self.last_restock + SHOP_RESTOCK_HOURS * 3600)

        new_slots = []
        for slot in range(SHOP_SIZE):
            rarity = _roll_shop_rarity()
            if rarity == Rarity.DIVINE:
                rarity = Rarity.UNIQUE
            card  = _REPOSITORY.get_random_card(rarity)
            price = self._card_price(card)
            self.shop_cards.append(ShopCard(slot, card, price))
            new_slots.append({"slot": slot, "card_id": card.card_id,
                               "price": price, "available_until": available_until})

        db.db_save_shop(new_slots)

    def restock(self):
        import database_manager as db
        db.db_clear_shop()
        self._generate_and_save()

    # ── Prix ─────────────────────────────────────────────────────────────
    def _card_price(self, card: Card) -> int:
        value = RARITY_SELL_VALUE.get(card.rarity)
        if value is None:
            raise ValueError(f"{card.rarity.name} est invendable.")
        return int(value * SHOP_PRICE_MULTIPLIER)

    # ── Achat ────────────────────────────────────────────────────────────
    def buy_card(self, player, index: int) -> tuple:
        """
        Retourne (card, price).
        Lève IndexError ou ValueError en cas d'échec.
        """
        if index < 0 or index >= len(self.shop_cards):
            raise IndexError(f"Index invalide : {index} (shop size={len(self.shop_cards)})")

        sc    = self.shop_cards[index]
        price = sc.price

        if not player.can_buy(price):
            raise ValueError(f"Pas assez de pièces (besoin: {price}, dispo: {player.coins}).")

        # Mise à jour mémoire joueur
        player.coins                   -= price
        player.stats.coins_spent       += price
        player.stats.coins_spent_shop  += price
        player.stats.shop_cards_bought += 1
        player.inventory.add_card(sc.card)
        player.carddex.add_card(sc.card)
        player.stats.cards_obtained        += 1
        player.stats.cards_by_rarity[sc.card.rarity] += 1
        player._update_max_coins()

        self.shop_cards.pop(index)
        return sc.card, price

    # ── Affichage ────────────────────────────────────────────────────────
    def display(self):
        print(f"\n{'═'*40}")
        print(f"  🛒  SHOP  (restock : {time.strftime('%H:%M:%S', time.localtime(self.last_restock))})")
        print(f"{'═'*40}")
        for i, sc in enumerate(self.shop_cards):
            print(f"  [{i}] {sc.card.name:<12} ({sc.card.rarity.name})  –  {sc.price:>6} 🪙")
        print(f"{'─'*40}\n")

    def __repr__(self):
        return f"Shop({len(self.shop_cards)} cartes)"