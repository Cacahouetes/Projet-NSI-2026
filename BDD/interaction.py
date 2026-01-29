import sqlite3
from BDD import connexion

def insert_user():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = "INSERT INTO (username, email) VALUES (?, ?)" #Exemple
            conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)
