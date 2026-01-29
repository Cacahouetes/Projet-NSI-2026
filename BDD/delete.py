import sqlite3
from BDD import connexion

def delete():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = "DELETE FROM table_name WHERE condition"
            cursor.execute(sql)
            conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)