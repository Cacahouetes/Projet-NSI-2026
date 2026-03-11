import sqlite3
import json

def convert_to_json(database, output_json):
    # 1. Connexion à la base de données
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row  # Permet d'obtenir les noms de colonnes
    cursor = conn.cursor()

    # 2. Récupérer le nom de la table et les données
    try:
        cursor.execute("SELECT * FROM CARDS")
        rows = cursor.fetchall()

        # 3. Transformer les données en liste de dictionnaires
        cards_list = [dict(row) for row in rows]

        # 4. Sauvegarder en fichier JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(cards_list, f, indent=4, ensure_ascii=False)
        
        print(f"Succès ! {len(cards_list)} cartes converties dans {output_json}")

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        conn.close()

convert_to_json('database.db', 'database.json')