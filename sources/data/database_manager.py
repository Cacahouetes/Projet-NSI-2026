"""
database_manager.py
Toutes les opérations SQLite du jeu.
"""

import sqlite3
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")


# Connexion

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        # Timeout pour éviter un blocage silencieux sur Windows
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn
    except sqlite3.Error as e:
        raise ConnectionError(f"Erreur de connexion à la base de données : {e}")


# Helpers internes (reçoivent un cursor, ne créent PAS de connexion)

def _internal_add_to_inventory(cursor, player_id: int, cards_list: list):
    """Ajoute des cartes à l'inventaire et au CardDex. Utilise un cursor existant."""
    now = int(time.time())
    for card in cards_list:
        cursor.execute("""
            INSERT INTO PLAYER_CARDS (player_id, card_id, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(player_id, card_id) DO UPDATE SET quantity = quantity + 1
        """, (player_id, card.card_id))

        cursor.execute("""
            INSERT OR IGNORE INTO PLAYER_CARDDEX (player_id, card_id, discovered_at)
            VALUES (?, ?, ?)
        """, (player_id, card.card_id, now))

    _internal_update_rarity_stats(cursor, player_id, cards_list, 'obtained')


def _internal_update_rarity_stats(cursor, player_id: int, cards_list: list, action_type: str):
    """Met à jour les compteurs de rareté. Utilise un cursor existant."""
    allowed = {'obtained', 'sold', 'fused'}
    if action_type not in allowed:
        raise ValueError(f"action_type invalide : '{action_type}' (attendu : {allowed})")

    for card in cards_list:
        rarity_name = card.rarity.name.capitalize()
        # Capitalize gère "Commune", mais pas "Épique" ou "Légendaire"
        # On utilise le mapping explicite pour être sûr
        rarity_name = _rarity_to_db_str(card.rarity)
        cursor.execute(f"""
            UPDATE PLAYER_RARITY_STATS
            SET {action_type} = {action_type} + 1
            WHERE player_id = ? AND rarity = ?
        """, (player_id, rarity_name))


def _internal_unlock_achievement(cursor, player_id: int, achievement_id: str, now: int):
    """Déverrouille un succès. Utilise un cursor existant."""
    cursor.execute("""
        INSERT OR IGNORE INTO PLAYER_ACHIEVEMENTS (player_id, achievement_id, unlocked_at)
        VALUES (?, ?, ?)
    """, (player_id, achievement_id, now))

    if cursor.rowcount > 0:
        cursor.execute("""
            UPDATE PLAYER_STATS
            SET achievements_unlocked = achievements_unlocked + 1
            WHERE player_id = ?
        """, (player_id,))
        return True
    return False


# Mapping rareté ↔ chaîne DB

def _rarity_to_db_str(rarity) -> str:
    from card import Rarity
    mapping = {
        Rarity.COMMUNE:    "Commune",
        Rarity.RARE:       "Rare",
        Rarity.ÉPIQUE:     "Épique",
        Rarity.LÉGENDAIRE: "Légendaire",
        Rarity.MYTHIQUE:   "Mythique",
        Rarity.UNIQUE:     "Unique",
        Rarity.DIVINE:     "Divine",
    }
    return mapping.get(rarity, "Commune")


def _db_str_to_rarity(rarity_str: str):
    from card import Rarity
    mapping = {
        "Commune":    Rarity.COMMUNE,
        "Rare":       Rarity.RARE,
        "Épique":     Rarity.ÉPIQUE,
        "Légendaire": Rarity.LÉGENDAIRE,
        "Mythique":   Rarity.MYTHIQUE,
        "Unique":     Rarity.UNIQUE,
        "Divine":     Rarity.DIVINE,
    }
    return mapping.get(rarity_str, Rarity.COMMUNE)


def _db_str_to_category(cat_str):
    if cat_str is None:
        return None
    from card import Category
    try:
        return Category[cat_str.upper()]
    except KeyError:
        return None


# Vérification d'intégrité

def check_db_integrity() -> bool:
    """Vérifie la présence des tables et des données vitales."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        tables_requises = [
            'ACHIEVEMENTS', 'CARDS', 'CHESTS', 'CHEST_CARDS', 'CHEST_OPENINGS',
            'DAILY_HISTORY', 'DAILY_REWARDS', 'PLAYERS',
            'PLAYER_ACHIEVEMENTS', 'PLAYER_CARDDEX', 'PLAYER_CARDS',
            'PLAYER_FUSIONS', 'PLAYER_FUSION_CARDS',
            'PLAYER_RARITY_STATS', 'PLAYER_STATS',
            'SHOP_CARDS', 'SHOP_HISTORY',
        ]
        for table in tables_requises:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
            )
            if not cursor.fetchone():
                print(f"ERREUR : table manquante → '{table}'")
                return False

        cursor.execute("SELECT COUNT(*) as total FROM CARDS")
        if cursor.fetchone()["total"] != 756:
            print("ATTENTION : nombre de cartes incorrect (attendu : 756).")
            return False

        cursor.execute("SELECT COUNT(*) as total FROM DAILY_REWARDS")
        if cursor.fetchone()["total"] != 7:
            print("ATTENTION : nombre de daily rewards incorrect (attendu : 7).")
            return False

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur check_db_integrity : {e}")
    finally:
        conn.close()


# Chargement complet d'un joueur

def load_player(player_id: int):
    """
    Charge toutes les données d'un joueur et reconstruit l'objet Player complet.
    Retourne un Player prêt à l'emploi, ou None si le joueur n'existe pas.
    Une seule connexion est utilisée pour toutes les lectures.
    """
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
    from player import Player
    from card import Card

    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Profil + stats
        cursor.execute("""
            SELECT p.player_id, p.username, p.created_at, s.*
            FROM PLAYERS p
            JOIN PLAYER_STATS s ON p.player_id = s.player_id
            WHERE p.player_id = ?
        """, (player_id,))
        profile_row = cursor.fetchone()
        if profile_row is None:
            return None
        profile = dict(profile_row)

        player = Player(player_id=player_id, coins=profile["coins"])
        s = player.stats
        s.created_at             = profile.get("created_at", 0)
        s.coins_earned           = profile.get("coins_earned", 0)
        s.coins_spent            = profile.get("coins_spent", 0)
        s.coins_from_sales       = profile.get("coins_from_sales", 0)
        s.coins_spent_shop       = profile.get("coins_spent_shop", 0)
        s.cards_obtained         = profile.get("cards_obtained", 0)
        s.divine_obtained        = profile.get("divine_obtained", 0)
        s.chests_opened          = profile.get("chests_opened", 0)
        s.cards_from_chests      = profile.get("cards_from_chests", 0)
        s.cards_sold             = profile.get("cards_sold", 0)
        s.fusions_attempted      = profile.get("fusions_attempted", 0)
        s.fusions_success        = profile.get("fusions_success", 0)
        s.fusions_failed         = profile.get("fusions_failed", 0)
        s.shop_cards_bought      = profile.get("shop_cards_bought", 0)
        s.max_coins_held         = profile.get("max_coins_held", 0)
        s.achievements_unlocked  = profile.get("achievements_unlocked", 0)
        s.daily_claims_total     = profile.get("daily_claims_total", 0)
        s.daily_current_streak   = profile.get("daily_current_streak", 0)
        s.daily_best_streak      = profile.get("daily_best_streak", 0)
        s.daily_streak_breaks    = profile.get("daily_streak_breaks", 0)
        s.last_daily_timestamp   = profile.get("last_daily_timestamp", 0)

        # Inventaire
        cursor.execute("""
            SELECT c.*, pc.quantity
            FROM PLAYER_CARDS pc
            JOIN CARDS c ON pc.card_id = c.card_id
            WHERE pc.player_id = ?
            ORDER BY c.card_id ASC
        """, (player_id,))
        for row in cursor.fetchall():
            card = Card(
                card_id=row["card_id"], name=row["name"],
                rarity=_db_str_to_rarity(row["rarity"]),
                category=_db_str_to_category(row["category"]),
                stat1=row["stat1"], stat2=row["stat2"], stat3=row["stat3"],
                description=row["description"], author=row["author"],
                image_path=row["image_path"],
            )
            for _ in range(row["quantity"]):
                player.inventory.add_card(card)

        # cards_by_rarity (depuis PLAYER_RARITY_STATS)
        # Nécessaire pour que les succès de type "first_rare" ne se redéclenchent pas à chaque démarrage de session.
        cursor.execute("""
            SELECT rarity, obtained FROM PLAYER_RARITY_STATS WHERE player_id = ?
        """, (player_id,))
        for row in cursor.fetchall():
            rarity_enum = _db_str_to_rarity(row["rarity"])
            player.stats.cards_by_rarity[rarity_enum] = row["obtained"]

        # CardDex
        cursor.execute("""
            SELECT card_id FROM PLAYER_CARDDEX WHERE player_id = ?
        """, (player_id,))
        for row in cursor.fetchall():
            player.carddex.collected_cards.add(row["card_id"])

        # Succès déjà débloqués
        cursor.execute("""
            SELECT achievement_id FROM PLAYER_ACHIEVEMENTS WHERE player_id = ?
        """, (player_id,))
        for row in cursor.fetchall():
            player.stats.achievements.add(row["achievement_id"])

        return player

    except sqlite3.Error as e:
        raise Exception(f"Erreur load_player : {e}")
    finally:
        conn.close()


# Fonctions de lecture (fetch_*)

def fetch_player_profile(player_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.player_id, p.username, p.created_at, s.*
            FROM PLAYERS p
            JOIN PLAYER_STATS s ON p.player_id = s.player_id
            WHERE p.player_id = ?
        """, (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        raise Exception(f"Erreur fetch_player_profile : {e}")
    finally:
        conn.close()


def fetch_player_inventory(player_id: int) -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, pc.quantity
            FROM PLAYER_CARDS pc
            JOIN CARDS c ON pc.card_id = c.card_id
            WHERE pc.player_id = ?
            ORDER BY c.card_id ASC
        """, (player_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Erreur fetch_player_inventory : {e}")
    finally:
        conn.close()


def fetch_card_dex(player_id: int) -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, cd.discovered_at
            FROM PLAYER_CARDDEX cd
            JOIN CARDS c ON cd.card_id = c.card_id
            WHERE cd.player_id = ?
            ORDER BY c.card_id ASC
        """, (player_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Erreur fetch_card_dex : {e}")
    finally:
        conn.close()


def fetch_unlocked_achievements(player_id: int) -> list:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, pa.unlocked_at
            FROM PLAYER_ACHIEVEMENTS pa
            JOIN ACHIEVEMENTS a ON pa.achievement_id = a.achievement_id
            WHERE pa.player_id = ?
            ORDER BY pa.unlocked_at DESC
        """, (player_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Erreur fetch_unlocked_achievements : {e}")
    finally:
        conn.close()


# Création de joueur

def create_new_player(username: str) -> int:
    rarities = ["Commune", "Rare", "Épique", "Légendaire", "Mythique", "Unique", "Divine"]
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PLAYERS (username, created_at) VALUES (?, ?)",
                (username, int(time.time()))
            )
            player_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO PLAYER_STATS (player_id) VALUES (?)", (player_id,)
            )
            for r in rarities:
                cursor.execute("""
                    INSERT INTO PLAYER_RARITY_STATS (player_id, rarity, obtained, sold, fused)
                    VALUES (?, ?, 0, 0, 0)
                """, (player_id, r))

            return player_id
    except sqlite3.Error as e:
        raise Exception(f"Erreur create_new_player : {e}")
    finally:
        conn.close()


# Pièces

def db_update_coins(player_id: int, new_coins: int,
                    delta_earned: int = 0, delta_spent: int = 0):
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE PLAYER_STATS
                SET coins        = ?,
                    coins_earned = coins_earned + ?,
                    coins_spent  = coins_spent  + ?
                WHERE player_id = ?
            """, (new_coins, delta_earned, delta_spent, player_id))
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_update_coins : {e}")
    finally:
        conn.close()


# Coffres

def db_register_generated_chest(category, cost: int, chest_type: str, cards_list: list) -> int:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO CHESTS (category, cost, type) VALUES (?, ?, ?)
            """, (category, cost, chest_type))
            chest_id = cursor.lastrowid

            for card in cards_list:
                cursor.execute("""
                    INSERT INTO CHEST_CARDS (chest_id, card_id, quantity)
                    VALUES (?, ?, 1)
                    ON CONFLICT(chest_id, card_id) DO UPDATE SET quantity = quantity + 1
                """, (chest_id, card.card_id))

            return chest_id
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_register_generated_chest : {e}")
    finally:
        conn.close()


def db_open_chest(player_id: int, chest_id: int, cost: int, cards_list: list) -> bool:
    """
    Toute la logique d'ouverture de coffre en une seule connexion :
    débit pièces + enregistrement + ajout inventaire + stats rareté.
    """
    conn = get_connection()
    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()

            # Débit + compteur coffres
            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins         = coins - ?,
                    coins_spent   = coins_spent + ?,
                    chests_opened = chests_opened + 1,
                    cards_from_chests = cards_from_chests + ?
                WHERE player_id = ? AND coins >= ?
            """, (cost, cost, len(cards_list), player_id, cost))

            if cursor.rowcount == 0:
                raise ValueError("Pièces insuffisantes ou joueur introuvable.")

            cursor.execute("""
                INSERT INTO CHEST_OPENINGS (player_id, chest_id, opened_at)
                VALUES (?, ?, ?)
            """, (player_id, chest_id, now))

            # Inventaire + carddex + rarity stats (même cursor, même transaction)
            _internal_add_to_inventory(cursor, player_id, cards_list)

            # Compteurs cartes obtenues + divines
            from card import Rarity
            divine_count = sum(1 for c in cards_list if c.rarity == Rarity.DIVINE)
            cursor.execute("""
                UPDATE PLAYER_STATS
                SET cards_obtained  = cards_obtained  + ?,
                    divine_obtained = divine_obtained + ?
                WHERE player_id = ?
            """, (len(cards_list), divine_count, player_id))

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_open_chest : {e}")
    finally:
        conn.close()


# Vente

def db_sell_card(player_id: int, card, new_coins: int):
    from card import RARITY_SELL_VALUE
    value = RARITY_SELL_VALUE.get(card.rarity)
    if value is None:
        raise ValueError(f"La carte {card.rarity.name} est invendable.")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE PLAYER_CARDS SET quantity = quantity - 1
                WHERE player_id = ? AND card_id = ?
            """, (player_id, card.card_id))

            cursor.execute("""
                DELETE FROM PLAYER_CARDS
                WHERE player_id = ? AND card_id = ? AND quantity <= 0
            """, (player_id, card.card_id))

            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins            = ?,
                    coins_earned     = coins_earned     + ?,
                    coins_from_sales = coins_from_sales + ?,
                    cards_sold       = cards_sold       + 1
                WHERE player_id = ?
            """, (new_coins, value, value, player_id))

            _internal_update_rarity_stats(cursor, player_id, [card], 'sold')

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_sell_card : {e}")
    finally:
        conn.close()


def db_sell_all_by_rarity(player_id: int, rarity, new_coins: int, cards_sold: list):
    from card import RARITY_SELL_VALUE
    value = RARITY_SELL_VALUE.get(rarity)
    if value is None:
        raise ValueError(f"Rareté invendable : {rarity.name}")

    total_gained = len(cards_sold) * value
    rarity_str   = _rarity_to_db_str(rarity)

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM PLAYER_CARDS
                WHERE player_id = ?
                  AND card_id IN (SELECT card_id FROM CARDS WHERE rarity = ?)
            """, (player_id, rarity_str))

            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins            = ?,
                    coins_earned     = coins_earned     + ?,
                    coins_from_sales = coins_from_sales + ?,
                    cards_sold       = cards_sold       + ?
                WHERE player_id = ?
            """, (new_coins, total_gained, total_gained, len(cards_sold), player_id))

            _internal_update_rarity_stats(cursor, player_id, cards_sold, 'sold')

        return total_gained
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_sell_all_by_rarity : {e}")
    finally:
        conn.close()


# Shop

def db_register_shop_purchase(player_id: int, card, price: int, new_coins: int):
    conn = get_connection()
    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins             = ?,
                    coins_spent       = coins_spent      + ?,
                    coins_spent_shop  = coins_spent_shop + ?,
                    shop_cards_bought = shop_cards_bought + 1,
                    cards_obtained    = cards_obtained   + 1
                WHERE player_id = ?
            """, (new_coins, price, price, player_id))

            cursor.execute("""
                INSERT INTO SHOP_HISTORY (player_id, card_id, price, purchased_at)
                VALUES (?, ?, ?, ?)
            """, (player_id, card.card_id, price, now))

            _internal_add_to_inventory(cursor, player_id, [card])

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_register_shop_purchase : {e}")
    finally:
        conn.close()


# Daily rewards
 
def db_update_daily(player_id: int, new_stats_dict: dict,
                    reward_coins: int, reward_card=None) -> bool:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
 
            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins                = ?,
                    coins_earned         = ?,
                    last_daily_timestamp = ?,
                    daily_current_streak = ?,
                    daily_best_streak    = ?,
                    daily_streak_breaks  = ?,
                    daily_claims_total   = ?
                WHERE player_id = ?
            """, (
                new_stats_dict['coins'],
                new_stats_dict['coins_earned'],
                new_stats_dict['last_ts'],
                new_stats_dict['current_streak'],
                new_stats_dict['best_streak'],
                new_stats_dict['streak_breaks'],
                new_stats_dict['total_claims'],
                player_id,
            ))
 
            card_id = reward_card.card_id if reward_card else None
            # day_index est 0-based (0=Jour1 … 6=Jour7)
            # Si absent du dict (ancienne version), calculer depuis current_streak
            day_index = new_stats_dict.get('day_index',
                        (new_stats_dict['current_streak'] - 1) % 7)
            cursor.execute("""
                INSERT INTO DAILY_HISTORY (player_id, day_index, coins, card_id, claimed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                player_id,
                day_index,
                reward_coins,
                card_id,
                new_stats_dict['last_ts'],
            ))
 
            # Carte de récompense dans la même transaction
            if reward_card and reward_card.card_id is not None:
                _internal_add_to_inventory(cursor, player_id, [reward_card])
                cursor.execute("""
                    UPDATE PLAYER_STATS
                    SET cards_obtained = cards_obtained + 1
                    WHERE player_id = ?
                """, (player_id,))
 
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_update_daily : {e}")
    finally:
        conn.close()


# Fusions

def db_register_fusion(player_id: int, fusion_data: dict) -> bool:
    """
    fusion_data : {cards_used, result_card, is_success, cost}
    Toute l'opération dans une seule connexion.
    """
    conn = get_connection()
    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE PLAYER_STATS
                SET coins              = coins - ?,
                    coins_spent        = coins_spent + ?,
                    fusions_attempted  = fusions_attempted + 1,
                    fusions_success    = fusions_success   + ?,
                    fusions_failed     = fusions_failed    + ?
                WHERE player_id = ?
            """, (
                fusion_data['cost'], fusion_data['cost'],
                1 if fusion_data['is_success'] else 0,
                0 if fusion_data['is_success'] else 1,
                player_id,
            ))

            # Regrouper par card_id : 3 cartes identiques = 1 UPDATE avec qty=3
            # Evite le UNIQUE constraint sur PLAYER_FUSION_CARDS(fusion_id, card_id)
            from collections import Counter
            cards_count = Counter(c.card_id for c in fusion_data['cards_used'])

            for card_id, qty in cards_count.items():
                cursor.execute("""
                    UPDATE PLAYER_CARDS SET quantity = quantity - ?
                    WHERE player_id = ? AND card_id = ?
                """, (qty, player_id, card_id))
                cursor.execute("""
                    DELETE FROM PLAYER_CARDS
                    WHERE player_id = ? AND card_id = ? AND quantity <= 0
                """, (player_id, card_id))

            _internal_update_rarity_stats(cursor, player_id, fusion_data['cards_used'], 'fused')

            result_card_id = None
            if fusion_data['is_success'] and fusion_data['result_card']:
                result_card    = fusion_data['result_card']
                result_card_id = result_card.card_id
                if result_card_id is not None:
                    _internal_add_to_inventory(cursor, player_id, [result_card])
                    cursor.execute("""
                        UPDATE PLAYER_STATS SET cards_obtained = cards_obtained + 1
                        WHERE player_id = ?
                    """, (player_id,))

            cursor.execute("""
                INSERT INTO PLAYER_FUSIONS (player_id, result_card_id, cost, is_success, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, result_card_id, fusion_data['cost'],
                  1 if fusion_data['is_success'] else 0, now))
            fusion_id = cursor.lastrowid

            # Une ligne par card_id distinct, avec la quantite utilisee
            for card_id, qty in cards_count.items():
                cursor.execute("""
                    INSERT INTO PLAYER_FUSION_CARDS (fusion_id, card_id, quantity)
                    VALUES (?, ?, ?)
                """, (fusion_id, card_id, qty))

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_register_fusion : {e}")
    finally:
        conn.close()


# Succès

def db_unlock_achievement(player_id: int, achievement_id: str) -> bool:
    conn = get_connection()
    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()
            return _internal_unlock_achievement(cursor, player_id, achievement_id, now)
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_unlock_achievement : {e}")
    finally:
        conn.close()


def db_sync_achievements(player_id: int, new_achievements: list) -> None:
    """Sauvegarde en DB tous les nouveaux succès en une seule connexion."""
    if not new_achievements:
        return
    conn = get_connection()
    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()
            for ach in new_achievements:
                _internal_unlock_achievement(cursor, player_id, ach.id, now)
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_sync_achievements : {e}")
    finally:
        conn.close()


# Fonctions publiques d'inventaire (pour usages directs si besoin)

def db_add_to_inventory(player_id: int, cards_list: list) -> bool:
    """Version publique : ouvre sa propre connexion."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            _internal_add_to_inventory(cursor, player_id, cards_list)
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_add_to_inventory : {e}")
    finally:
        conn.close()


def db_update_rarity_stats(player_id: int, cards_list: list, action_type: str) -> bool:
    """Version publique : ouvre sa propre connexion."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            _internal_update_rarity_stats(cursor, player_id, cards_list, action_type)
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_update_rarity_stats : {e}")
    finally:
        conn.close()


# max_coins_held

def db_update_max_coins(player_id: int, max_coins: int) -> bool:
    """Met à jour max_coins_held si la nouvelle valeur est superieure (MAX() cote SQL)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE PLAYER_STATS
                SET max_coins_held = MAX(max_coins_held, ?)
                WHERE player_id = ?
            """, (max_coins, player_id))
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_update_max_coins : {e}")
    finally:
        conn.close()


# Play time

def db_update_play_time(player_id: int, seconds_to_add: int) -> bool:
    """Ajoute la duree de la session au compteur total."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                UPDATE PLAYER_STATS
                SET play_time_seconds = play_time_seconds + ?
                WHERE player_id = ?
            """, (seconds_to_add, player_id))
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_update_play_time : {e}")
    finally:
        conn.close()


# Shop persistance
 
def db_load_shop() -> list:
    """
    Charge TOUS les slots du cycle en cours (sold=0 et sold=1).
    Retourne [] seulement si aucune ligne n existe (1er lancement ou apres expiration).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT shop_slot, card_id, price, available_until, sold "
            "FROM SHOP_CARDS ORDER BY shop_slot ASC"
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_load_shop : {e}")
    finally:
        conn.close()
 
 
def db_save_shop(slots: list) -> bool:
    """Ecrase le shop complet. slots : list of {slot, card_id, price, available_until}"""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM SHOP_CARDS")
            for s in slots:
                cursor.execute(
                    "INSERT INTO SHOP_CARDS (shop_slot, card_id, price, available_until, sold) "
                    "VALUES (?, ?, ?, ?, 0)",
                    (s["slot"], s["card_id"], s["price"], s["available_until"])
                )
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_save_shop : {e}")
    finally:
        conn.close()
 
 
def db_clear_shop() -> bool:
    """Vide SHOP_CARDS (avant un restock)."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM SHOP_CARDS")
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_clear_shop : {e}")
    finally:
        conn.close()
 
 
def db_remove_shop_slot(player_id: int, shop_slot: int) -> bool:
    """
    Marque le slot shop_slot (0, 1 ou 2) comme vendu (sold=1).
    shop_slot est la valeur directe de la colonne SHOP_CARDS.shop_slot,
    pas un index dans une liste filtrée.
    """
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE SHOP_CARDS SET sold = 1 WHERE shop_slot = ?",
                (shop_slot,)
            )
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur db_remove_shop_slot : {e}")
    finally:
        conn.close()