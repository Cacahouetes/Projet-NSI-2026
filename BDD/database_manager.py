import sqlite3

# Fonctions d'Initialisation et Connexion

def get_connection():
    with sqlite3.connect('BDD/game.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM PLAYERS")
        résultats = cur.fetchall()
        for row in résultats:
            print(row)

def check_db_integrity():
    pass

# Fonctions de Chargement (Load)

def fetch_player_profile(player_id):
    pass

def fetch_player_inventory(player_id):
    pass

def fetch_card_dex(player_id):
    pass

def fetch_unlocked_achievements(player_id):
    pass


# Fonctions d'Action (Update/Save)

def db_open_chest(player_id, chest_id, cost, cards_list):
    pass

def db_add_to_inventory(player_id, cards_list):
    pass

def db_update_rarity_stats(player_id, cards_list, action_type):
    pass

def db_update_daily(player_id, new_streak, coins_reward, card_reward):
    pass

def db_register_fusion(player_id, fusion_data):
    pass

def db_unlock_achievement(player_id, achievement_id):
    pass

print(get_connection())