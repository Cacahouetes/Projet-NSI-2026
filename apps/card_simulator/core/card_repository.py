import os
import random as rd
import sqlite3

from card import Card, Category, Rarity

DB_PATH = os.path.join(os.path.dirname(__file__), "../../../data/game.db")

RARITY_TO_DB = {
    Rarity.COMMUNE:    "Commune",
    Rarity.RARE:       "Rare",
    Rarity.ÉPIQUE:     "Épique",
    Rarity.LÉGENDAIRE: "Légendaire",
    Rarity.MYTHIQUE:   "Mythique",
    Rarity.UNIQUE:     "Unique",
    Rarity.DIVINE:     "Divine",
}
DB_TO_RARITY = {v: k for k, v in RARITY_TO_DB.items()}


class CardRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = os.path.abspath(db_path)

    def _row_to_card(self, row) -> Card:
        return Card(
            card_id    = row["card_id"],
            name       = row["name"],
            rarity     = DB_TO_RARITY.get(row["rarity"], Rarity.COMMUNE),
            category   = row["category"],
            stat1      = row["stat1"],
            stat2      = row["stat2"],
            stat3      = row["stat3"],
            description= row["description"],
            author     = row["author"],
            image_path = row["image_path"],
        )

    def normalize_rarity(self, rarity) -> Rarity:
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

    def normalize_category(self, category):
        if category is None:
            return None
        if isinstance(category, Category):
            return category.name
        if isinstance(category, str):
            if category.upper() in Category.__members__:
                return category.upper()
            raise ValueError(f"Catégorie invalide : {category}")
        raise TypeError("category doit être un Category, une chaîne ou None")

    def get_random_card(self, rarity, category=None) -> Card:
        rarity_enum = self.normalize_rarity(rarity)
        rarity_db   = RARITY_TO_DB[rarity_enum]
        category_db = self.normalize_category(category)

        query  = ("SELECT * FROM CARDS WHERE rarity = ?")
        params = [rarity_db]
        if category_db is not None:
            query += " AND category = ?"
            params.append(category_db)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

        if not rows:
            raise ValueError(f"Aucune carte {rarity_db} en DB (category={category_db})")
        return self._row_to_card(rd.choice(rows))

    def get_card_by_id(self, card_id: int) -> Card | None:
        """Charge une carte précise par son card_id. Retourne None si introuvable."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM CARDS WHERE card_id = ?", (card_id,)
            ).fetchone()
        return self._row_to_card(row) if row else None