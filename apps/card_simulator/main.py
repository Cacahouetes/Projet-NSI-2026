"""
main.py
=======
Point d'entrée du jeu.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "logic"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../data"))

import database_manager as db
from player import Player
from generator import generate_normal_chest, generate_omni_chest
from shop_system import Shop
from daily_manager import DailyRewardManager
from fusion_system import FusionSystem
from card import Rarity, Category


def _notify_achievements(new_achievements: list):
    for ach in new_achievements:
        print(f"\n🏆  Succès débloqué : [{ach.name}] — {ach.description}")


def action_open_chest(player: Player, category=None, omni: bool = False):
    chest = generate_omni_chest() if omni else generate_normal_chest(category)
    if not player.can_buy(chest.cost):
        print(f"Pas assez de pièces (besoin : {chest.cost}, dispo : {player.coins}).")
        return
    cat_str  = category.name if category else None
    chest_id = db.db_register_generated_chest(cat_str, chest.cost, chest.type.name, chest.cards)
    new_ach  = player.buy_chest(chest)
    db.db_open_chest(player.id, chest_id, chest.cost, chest.cards)
    db.db_update_max_coins(player.id, player.stats.max_coins_held)
    db.db_sync_achievements(player.id, new_ach)
    _notify_achievements(new_ach)
    print(f"\n📦  Coffre ouvert ! ({len(chest.cards)} cartes)")
    for card in chest.cards:
        print(f"   ✦ {card}")


def action_sell_card(player: Player, card):
    if not player.player_sell_card(card):
        print(f"Impossible de vendre {card}.")
        return
    from card import RARITY_SELL_VALUE
    db.db_sell_card(player.id, card, player.coins)
    new_ach = player.check_achievements()
    db.db_sync_achievements(player.id, new_ach)
    _notify_achievements(new_ach)
    print(f"💰  {card.name} vendue pour {RARITY_SELL_VALUE[card.rarity]} pièces. Solde : {player.coins} 🪙")


def action_sell_all_by_rarity(player: Player, rarity: Rarity):
    cards_to_sell = [c for c in player.inventory.cards if c.rarity == rarity]
    if not cards_to_sell:
        print(f"Aucune carte {rarity.name} à vendre.")
        return
    gained = player.player_sell_all_by_rarity(rarity)
    db.db_sell_all_by_rarity(player.id, rarity, player.coins, cards_to_sell)
    new_ach = player.check_achievements()
    db.db_sync_achievements(player.id, new_ach)
    _notify_achievements(new_ach)
    print(f"💰  {len(cards_to_sell)} carte(s) {rarity.name} → {gained} pièces. Solde : {player.coins} 🪙")


def action_buy_shop_card(player: Player, shop: Shop, index: int):
    try:
        card, price = shop.buy_card(player, index)
    except (IndexError, ValueError) as e:
        print(f"Achat impossible : {e}")
        return
    db.db_register_shop_purchase(player.id, card, price, player.coins)
    db.db_remove_shop_slot(shop.player_id, index)
    new_ach = player.check_achievements()
    db.db_sync_achievements(player.id, new_ach)
    _notify_achievements(new_ach)
    print(f"🛍️  Carte achetée dans le shop : {card}")


def action_claim_daily(player: Player):
    manager = DailyRewardManager()
    try:
        reward = manager.claim_reward(player)
        print(f"\n🎁  {reward.description}")
        db.db_update_max_coins(player.id, player.stats.max_coins_held)
        new_ach = player.check_achievements()
        db.db_sync_achievements(player.id, new_ach)
        _notify_achievements(new_ach)
    except ValueError as e:
        print(f"⏳  {e}")


def action_fuse(player: Player, rarity: Rarity):
    system = FusionSystem()
    result = system.fuse(player, rarity)
    print(result["message"])
    _notify_achievements(result.get("new_achievements", []))


def save_session(player: Player, session_start: float):
    elapsed = int(time.time() - session_start)
    db.db_update_play_time(player.id, elapsed)
    print(f"\n⏱️  Session : {elapsed // 60}m {elapsed % 60}s")


def main():
    session_start = time.time()

    if not db.check_db_integrity():
        print("❌  DB corrompue. Arrêt.")
        sys.exit(1)

    player_id = 1
    player    = db.load_player(player_id)
    if player is None:
        print(f"Joueur {player_id} introuvable. Création...")
        player_id = db.create_new_player("Joueur1")
        player    = db.load_player(player_id)

    print(f"\n👤  Bienvenue, joueur #{player.id}")
    print(f"    Solde : {player.coins} 🪙")
    print(f"    Inventaire : {len(player.inventory)} cartes")
    print(f"    CardDex : {player.carddex.completion_percentage():.1f} %")

    shop = Shop(player_id=player_id)

    action_claim_daily(player)
    action_open_chest(player, category=Category.MEME)
    action_open_chest(player, omni=True)
    shop.display()
    action_buy_shop_card(player, shop, 0)
    action_fuse(player, Rarity.COMMUNE)
    action_sell_all_by_rarity(player, Rarity.COMMUNE)

    print(f"\n📊  Stats finales")
    print(f"    Coffres ouverts  : {player.stats.chests_opened}")
    print(f"    Fusions tentées  : {player.stats.fusions_attempted}")
    print(f"    Succès débloqués : {player.stats.achievements_unlocked}")
    print(f"    Solde            : {player.coins} 🪙")
    print(f"    Max coins held   : {player.stats.max_coins_held} 🪙")

    save_session(player, session_start)


if __name__ == "__main__":
    main()