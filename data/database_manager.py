import sqlite3
import time
import sys
import os
import sys
sys.path.append("./Card Opening Simulator")
from generation import generate_normal_chest

# Fonctions d'Initialisation et Connexion

def get_connection():
    '''
    Gère l'ouverture de la connexion à 'game.db'
    '''
    try:
        conn = sqlite3.connect('BDD\game.db')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        return conn
    except sqlite3.Error as e:
        raise ConnectionError(f"Erreur de connexion à la base de données : {e}")

def check_db_integrity():
    '''
    Vérifie si la base de données est présente et contient les données vitales.
    Renvoie True si tout est OK, False sinon.
    '''
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # 1. Vérifier que les tables existent
        tables_requises = [
            'ACHIEVEMENTS', 'CARDS', 'CHESTS', 'CHEST_CARDS', 'CHEST_OPENINGS', 'DAILY_HISTORY', 'DAILY_REWARDS', 'PLAYERS', 'PLAYER_ACHIEVEMENTS',
            'PLAYER_CARDDEX', 'PLAYER_FUSIONS', 'PLAYER_FUSIONS_CARDS', 'PLAYER_RARITY_STATS', 'PLAYER_STATS', 'SHOP_CARDS', 'SHOP_HISTORY'
            ]
        
        for table in tables_requises:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"ERREUR : La table '{table}' est manquante.")
                return False

        # 2. Vérifier le nombre de cartes (756)
        cursor.execute("SELECT COUNT(*) as total FROM CARDS")
        nb_cards = cursor.fetchone()['total']

        if nb_cards != 756:
            print(f"ATTENTION : Le nombre de cartes est incorrect (Trouvées: {nb_cards}/756).")
            return False

        # 3. Vérifier le nombre de daily rewards (7)
        cursor.execute("SELECT COUNT(*) as total FROM DAILY_REWARDS")
        nb_daily = cursor.fetchone()['total']

        if nb_daily != 7:
            print(f"ATTENTION : Le nombre de daily rewards est incorrect (Trouvés: {nb_daily}/7).")
            return False

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la vérification : {e}")
    
    finally:
        conn.close()

# Fonctions de Chargement (Load)

def fetch_player_profile(player_id):
    '''
    Récupère toutes les données d'un joueur et de ses statistiques.
    Renvoie un dictionnaire contenant les informations ou None si le joueur n'existe pas.
    '''
    conn = get_connection()
    
    try:
        cursor = conn.cursor()

        query = """
            SELECT p.username, p.created_at, s.*
            FROM PLAYERS p
            JOIN PLAYER_STATS s ON p.player_id = s.player_id
            WHERE p.player_id = ?
         """

        cursor.execute(query, (player_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)

        else:
            print(f"Joueur avec l'ID {player_id} non trouvé.")
            return None

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la récupération du profil : {e}")

    finally:
        conn.close()

def fetch_player_inventory(player_id):
    '''
    Récupère toutes les cartes possédées par un joueur avec leurs détails.
    Renvoie une liste de dictionnaires (un dico par carte).
    '''
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT c.*, pc.quantity
            FROM PLAYER_CARDS pc
            JOIN CARDS c ON pc.card_id = c.card_id
            WHERE pc.player_id = ?
            ORDER BY c.card_id ASC
        """

        cursor.execute(query, (player_id,))
        rows = cursor.fetchall()

        inventory = [dict(row) for row in rows]
        return inventory

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la récupération de l'inventaire : {e}")

    finally:
        conn.close()

def fetch_card_dex(player_id):
    '''
    Récupère la liste des cartes découvertes par le joueur.
    Renvoie une liste de dictionnaires (un dico par carte).
    '''
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT c.*, cd.discovered_at
            FROM PLAYER_CARDDEX cd
            JOIN CARDS c ON cd.card_id = c.card_id
            WHERE cd.player_id = ?
            ORDER BY c.card_id ASC
        """

        cursor.execute(query, (player_id,))
        rows = cursor.fetchall()
        card_dex = [dict(row) for row in rows]
        return card_dex

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la récupération du CardDex : {e}")

    finally:
        conn.close()

def fetch_unlocked_achievements(player_id):
    '''
    Récupère la liste des succès déjà obtenus par le joueur.
    Renvoie une liste de dictionnaires contenant les détails du succès et la date d'obtention.
    '''
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT a.*, pa.unlocked_at
            FROM PLAYER_ACHIEVEMENTS pa
            JOIN ACHIEVEMENTS a ON pa.achievement_id = a.achievement_id
            WHERE pa.player_id = ?
            ORDER BY pa.unlocked_at DESC
        """

        cursor.execute(query, (player_id,))
        rows = cursor.fetchall()
        achievements = [dict(row) for row in rows]
        return achievements

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la récupération des succès : {e}")

    finally:
        conn.close()


# Fonctions d'Action (Update/Save)

def create_new_player(username):
    conn = get_connection()
    rarities = ["Commune", "Rare", "Épique", "Légendaire", "Mythique", "Unique", "Divine"]
    
    try:
        with conn:
            cursor = conn.cursor()
            # 1. Création du profil
            cursor.execute("INSERT INTO PLAYERS (username, created_at) VALUES (?, ?)", (username, int(time.time())))
            player_id = cursor.lastrowid
            
            # 2. Création des stats de base
            cursor.execute(f"INSERT INTO PLAYER_STATS (player_id) VALUES ({player_id})")
            
            # 3. Pré-remplissage des raretés (La boucle magique)
            for r in rarities:
                cursor.execute("""
                    INSERT INTO PLAYER_RARITY_STATS (player_id, rarity, obtained, sold, fused)
                    VALUES (?, ?, 0, 0, 0)
                """, (player_id, r))
                
            return player_id

    except sqlite3.Error as e:
        raise Exception(f"Erreur création joueur : {e}")

def db_register_generated_chest(category, cost, chest_type, cards_list):
    """
    Enregistre le coffre généré et ses cartes associées.
    Retourne l'ID du coffre créé.
    """
    conn = get_connection()
    
    try:
        with conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO CHESTS (category, cost, type)
                VALUES (?, ?, ?)
            """, (category, cost, chest_type))

            chest_id = cursor.lastrowid
            
            for card in cards_list:
                cursor.execute("""
                    INSERT INTO CHEST_CARDS (chest_id, card_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(chest_id, card_id) DO UPDATE SET quantity = quantity + 1
                """, (chest_id, card.card_id, 1))
            
            return chest_id

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de l'enregistrement du coffre : {e}")
    finally:
        conn.close()

def db_open_chest(player_id, chest_id, cost, cards_list):
    '''
    Gère l'achat et l'obtention des cartes d'un booster.
    1. Débite les pièces et met à jour les stats de dépenses.
    2. Enregistre l'ouverture dans l'historique.
    3. Ajoute les cartes à l'inventaire et au CardDex.
    4. Met à jour les compteurs de rareté.
    '''
    conn = get_connection()

    now = int(time.time())

    try:
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE PLAYER_STATS 
                SET coins = coins - ?, 
                    coins_spent = coins_spent + ?
                WHERE player_id = ? AND coins >= ?
            """, (cost, cost, player_id, cost))

            cursor.execute("""
                INSERT INTO CHEST_OPENINGS (player_id, chest_id, opened_at)
                VALUES (?, ?, ?)
            """, (player_id, chest_id, now))

        db_add_to_inventory(player_id, cards_list)

        print(f"Booster ouvert avec succès pour le joueur {player_id}.")
        return True

    except sqlite3.Error as e:
        raise Exception(f"Erreur SQL lors de l'ouverture du coffre : {e}")
    finally:
        conn.close()


def db_add_to_inventory(player_id, cards_list):
    '''
    Ajoute une liste de cartes à l'inventaire et au CardDex du joueur.
    Gère aussi l'incrémentation des statistiques de rareté.
    '''
    conn = get_connection()

    now = int(time.time())
    try:
        with conn:
            cursor = conn.cursor()

            for card in cards_list:
                rarity_name = card.rarity.name.capitalize()

                cursor.execute("""
                    INSERT INTO PLAYER_CARDS (player_id, card_id, quantity)
                    VALUES (?, ?, 1)
                    ON CONFLICT(player_id, card_id) DO UPDATE SET quantity = quantity + 1
                """, (player_id, card.card_id))

                cursor.execute("""
                    INSERT OR IGNORE INTO PLAYER_CARDDEX (player_id, card_id, discovered_at)
                    VALUES (?, ?, ?)
                """, (player_id, card.card_id, now))

            db_update_rarity_stats(player_id, cards_list, 'obtained')

        return True

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de l'ajout à l'inventaire : {e}")
    finally:
        conn.close()

def db_update_rarity_stats(player_id, cards_list, action_type):
    """
    Met à jour les compteurs de rareté pour un joueur.
    action_type peut être : 'obtained', 'sold', ou 'fused'.
    """
    conn = get_connection()
    
    allowed_columns = ['obtained', 'sold', 'fused']
    if action_type not in allowed_columns:
        raise Exception(f"Erreur : Type d'action '{action_type}' non valide.")

    try:
        with conn:
            cursor = conn.cursor()
            
            for card in cards_list:
                rarity_name = card.rarity.name.capitalize()
                
                query = f"""
                    UPDATE PLAYER_RARITY_STATS 
                    SET {action_type} = {action_type} + 1
                    WHERE player_id = ? AND rarity = ?
                """
                
                cursor.execute(query, (player_id, rarity_name))
                
        return True

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors de la mise à jour des stats de rareté : {e}")
    finally:
        conn.close()

def db_update_daily(player_id, new_stats_dict, reward_coins, reward_card=None):
    """
    Synchronise les résultats du DailyRewardManager avec la DB.
    """
    conn = get_connection()
    
    try:
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE PLAYER_STATS 
                SET coins = ?, 
                    coins_earned = ?,
                    last_daily_timestamp = ?,
                    daily_current_streak = ?,
                    daily_best_streak = ?,
                    daily_streak_breaks = ?,
                    daily_claims_total = ?
                WHERE player_id = ?
            """, (
                new_stats_dict['coins'], new_stats_dict['coins_earned'],
                new_stats_dict['last_ts'], new_stats_dict['current_streak'],
                new_stats_dict['best_streak'], new_stats_dict['streak_breaks'],
                new_stats_dict['total_claims'], player_id
            ))


            card_id = reward_card.card_id if reward_card else None
            cursor.execute("""
                INSERT INTO DAILY_HISTORY (player_id, day_index, coins, card_id, claimed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, new_stats_dict['current_streak'], reward_coins, card_id, new_stats_dict['last_ts']))


            if reward_card:
                db_add_to_inventory(player_id, [reward_card])
                
        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur SQL Daily : {e}")

def db_register_fusion(player_id, fusion_data):
    """
    Enregistre une tentative de fusion dans la base de données.
    fusion_data contient : 
    - 'cards_used': liste d'objets Card sacrifiés
    - 'result_card': l'objet Card obtenu (ou None si échec)
    - 'is_success': booléen
    - 'cost': coût en pièces
    """
    conn = get_connection()
    
    now = int(time.time())
    
    try:
        with conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE PLAYER_STATS 
                SET coins = coins - ?,
                    coins_spent = coins_spent + ?
                WHERE player_id = ?
            """, (fusion_data['cost'], fusion_data['cost'], player_id, fusion_data['cost']))

            for card in fusion_data['cards_used']:
                cursor.execute("""
                    UPDATE PLAYER_CARDS 
                    SET quantity = quantity - 1 
                    WHERE player_id = ? AND card_id = ?
                """, (player_id, card.card_id))
                
                cursor.execute("""
                    DELETE FROM PLAYER_CARDS 
                    WHERE player_id = ? AND card_id = ? AND quantity <= 0
                """, (player_id, card.card_id))

            db_update_rarity_stats(player_id, fusion_data['cards_used'], 'fused')

            result_card_id = None
            if fusion_data['is_success'] and fusion_data['result_card']:
                result_card = fusion_data['result_card']
                result_card_id = result_card.card_id
                db_add_to_inventory(player_id, [result_card])

            cursor.execute("""
                INSERT INTO PLAYER_FUSIONS (player_id, result_card_id, cost, is_success, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, result_card_id, fusion_data['cost'], 1 if fusion_data['is_success'] else 0, now))
            
            fusion_id = cursor.lastrowid
            
            for card in fusion_data['cards_used']:
                cursor.execute("""
                    INSERT INTO PLAYER_FUSION_CARDS (fusion_id, card_id)
                    VALUES (?, ?)
                """, (fusion_id, card.card_id))

        return True
    except sqlite3.Error as e:
        raise Exception(f"Erreur SQL Fusion : {e}")
    finally:
        conn.close()

def db_unlock_achievement(player_id, achievement_id):
    """
    Déverrouille un succès pour le joueur s'il ne l'a pas déjà.
    Renvoie True si le succès vient d'être débloqué, False sinon.
    """
    conn = get_connection()
    
    now = int(time.time())
    
    try:
        with conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO PLAYER_ACHIEVEMENTS (player_id, achievement_id, unlocked_at)
                VALUES (?, ?, ?)
            """, (player_id, achievement_id, now))
            
            if cursor.rowcount > 0:
                print(f"Succès {achievement_id} débloqué pour le joueur {player_id} !")
                return True
            
            return False

    except sqlite3.Error as e:
        raise Exception(f"Erreur lors du déverrouillage du succès : {e}")
    finally:
        conn.close()