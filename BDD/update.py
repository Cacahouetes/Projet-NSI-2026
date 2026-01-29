import sqlite3
from BDD import connexion

def update():
    try:
        with connexion() as conn:
            cursor = conn.cursor()
            sql = "UPDATE table_name SET column1 = ? WHERE condition"
            cursor.execute(sql, (value1,))
            conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)
