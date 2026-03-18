# Schéma de la base de données

La base `game.db` est une base SQLite avec 17 tables réparties en 3 catégories.

## Tables de référence (données immuables)

### CARDS
756 cartes du jeu. Jamais modifiée après initialisation.

| Colonne | Type | Description |
|---------|------|-------------|
| card_id | INT PK | Identifiant unique |
| name | TEXT | Nom de la carte |
| rarity | TEXT | Commune / Rare / Épique / Légendaire / Mythique / Unique / Divine |
| category | TEXT | MEME / MOTS / OBJETS / PERSONNAGES / CONCEPTS |
| stat1, stat2, stat3 | INT | Statistiques de la carte |
| description | TEXT | Description |
| author | TEXT | Auteur |
| image_path | TEXT | Chemin relatif vers l'image (ex: `Cards/Commune/1.png`) |

### ACHIEVEMENTS
27 succès définis. Jamais modifiée.

### DAILY_REWARDS
7 lignes (Jour 1 à Jour 7). Jamais modifiée.

---

## Tables de session jeu (vidées entre les parties)

### CHESTS
Coffres générés pour la session en cours.

### CHEST_CARDS
Cartes associées à chaque coffre.

### SHOP_CARDS
3 slots du shop avec timer d'expiration (`available_until`).

---

## Tables joueur (progression)

### PLAYERS
| Colonne | Type | Description |
|---------|------|-------------|
| player_id | INT PK AUTO | Identifiant du joueur |
| username | TEXT | Nom du joueur |
| created_at | INT | Timestamp de création |

### PLAYER_STATS
Une ligne par joueur. Toutes les statistiques agrégées.

| Colonne | Description |
|---------|-------------|
| coins | Pièces actuelles |
| coins_earned / coins_spent | Économie totale |
| chests_opened / cards_obtained | Progression coffres |
| fusions_attempted / success / failed | Statistiques fusion |
| daily_current_streak / best_streak | Streak quotidien |
| play_time_seconds | Temps de jeu total (Card + Arcade) |

### PLAYER_CARDS
Inventaire : une ligne par (joueur, carte) avec quantité.

### PLAYER_CARDDEX
Cartes découvertes (même si vendues).

### PLAYER_RARITY_STATS
Compteurs par rareté : obtenues / vendues / fusionnées.

### PLAYER_ACHIEVEMENTS
Succès débloqués avec timestamp.

### PLAYER_FUSIONS + PLAYER_FUSION_CARDS
Historique de chaque tentative de fusion.

### CHEST_OPENINGS
Historique de chaque ouverture de coffre.

### DAILY_HISTORY
Historique de chaque récompense quotidienne réclamée.

### SHOP_HISTORY
Historique de chaque achat dans le shop.

---

## Règles de fusion (FUSION_RULES dans inventory.py)

| Rareté source | Cartes nécessaires | Taux de réussite | Coût | Résultat |
|---------------|-------------------|------------------|------|----------|
| Commune | 3 | 100% | 20 pièces | Rare |
| Rare | 3 | 90% | 200 pièces | Épique |
| Épique | 3 | 25% | 320 pièces | Légendaire |
| Légendaire | 3 | 15% | 1 200 pièces | Mythique |
| Mythique | 3 | 5% | 4 800 pièces | Unique |

---

## Probabilités des coffres

### Type de coffre (tirage préalable)
| Type | Probabilité |
|------|-------------|
| Normal | ~99,499% |
| GODPACK | 1/200 (0,5%) |
| DIVINE PACK | 1/67 067 (~0,00149%) |

### Bonus Divine (indépendant)
Après génération : 1/30 000 d'ajouter une 11ᵉ carte Divine.

### Coffre Normal - slots
| Slots | Contenu |
|-------|---------|
| 1–6 | Commune (100%) |
| 7–9 | Rare (75%) / Épique (25%) |
| 10 | Rare 55% · Épique 30% · Légendaire 10% · Mythique 4,9% · Unique 0,1% |