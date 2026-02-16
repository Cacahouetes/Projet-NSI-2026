import sqlite3
import csv

conn = sqlite3.connect("BDD/database.db")
cursor = conn.cursor()

with open("BDD/cards.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cursor.execute("""
            INSERT OR REPLACE INTO CARDS
            (card_id, name, rarity, category, stat1, stat2, stat3, description, autor, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["card_id"],
            row["name"],
            row["rarity"],
            row["category"],
            row["stat1"],
            row["stat2"],
            row["stat3"],
            row["description"],
            row["autor"],
            row["image_path"]
        ))

conn.commit()
conn.close()