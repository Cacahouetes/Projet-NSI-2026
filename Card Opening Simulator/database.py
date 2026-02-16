import os
import random
import sqlite3

from card import Card, Category, Rarity

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "BDD", "database.db")

RARITY_TO_DB = {
    Rarity.COMMON: "Commune",
    Rarity.RARE: "Rare",
    Rarity.EPIC: "Épique",
    Rarity.LEGENDARY: "Légendaire",
    Rarity.MYTHIC: "Mythique",
    Rarity.UNIQUE: "Unique",
    Rarity.DIVINE: "Divine",
}

DB_TO_RARITY = {value: key for key, value in RARITY_TO_DB.items()}


class CardRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = os.path.abspath(db_path)

    def _normalize_rarity(self, rarity):
        if isinstance(rarity, Rarity):
            return rarity
        if isinstance(rarity, str):
            if rarity in DB_TO_RARITY:
                return DB_TO_RARITY[rarity]
            try:
                return Rarity[rarity.upper()]
            except KeyError as exc:
                raise ValueError(f"Rareté inconnue: {rarity}") from exc
        raise TypeError("rarity doit être un Rarity ou une chaîne")

    def _normalize_category(self, category):
        if category is None:
            return None
        if isinstance(category, Category):
            return category.name
        if isinstance(category, str):
            return category.upper()
        raise TypeError("category doit être un Category, une chaîne ou None")

    def get_random_card(self, rarity, category=None):
        rarity_enum = self._normalize_rarity(rarity)
        rarity_db = RARITY_TO_DB[rarity_enum]
        category_db = self._normalize_category(category)

        query = (
            "SELECT card_id, name, rarity, category, stat1, stat2, stat3, description, autor, image_path "
            "FROM CARDS WHERE rarity = ?"
        )
        params = [rarity_db]

        if category_db is not None:
            query += " AND category = ?"
            params.append(category_db)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

        if not rows:
            return Card(rarity=rarity_enum, category=category)

        row = random.choice(rows)
        category_value = row["category"]
        try:
            category_value = Category[category_value]
        except KeyError:
            pass

        return Card(
            rarity=rarity_enum,
            category=category_value,
            card_id=row["card_id"],
            name=row["name"],
            stat1=row["stat1"],
            stat2=row["stat2"],
            stat3=row["stat3"],
            description=row["description"],
            author=row["autor"],
            image_path=row["image_path"],
        )
