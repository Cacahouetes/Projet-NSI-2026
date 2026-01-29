import sqlite3
from BDD import connexion

def select():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM "
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    except sqlite3.Error as e:
        print("An error occurred:", e)
        return None