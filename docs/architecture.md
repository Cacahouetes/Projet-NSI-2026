# Architecture du projet

## Vue d'ensemble

```
sources/
├── main.py (Launcher Pygame)
├── server.py (Serveur Flask, WebStats)
│
├── data/
│   └── database_manager.py (Toutes les opérations SQLite)
│
├── apps/
│   ├── card_simulator/ (Jeu de cartes)
│   ├── arcade_game/ (Jeu arcade)
│   └── web_stats/ (Interface web)
│
└── assets/ (Ressources (images, sons))
```

---

## main.py - Launcher

Point d'entrée unique. Lance les deux jeux via `subprocess.Popen()` et démarre
le serveur Flask en arrière-plan. Gère aussi le reset de sauvegarde (popup de
confirmation, recréation du joueur en DB).

---

## data/database_manager.py

Couche d'accès aux données. Toutes les fonctions publiques ouvrent et ferment
leur propre connexion. Les helpers internes (`_internal_*`) reçoivent un curseur
existant pour éviter les deadlocks dans les transactions multi-tables.

**Convention de nommage :**
- `fetch_*` -> lecture seule
- `db_*` -> écriture
- `_internal_*` -> helpers sans connexion propre
- `load_*` -> charge un objet complet

---

## apps/card_simulator/

### core/ - Logique métier pure (sans DB, sans Pygame)

| Fichier | Rôle |
|---------|------|
| `card.py` | Classe `Card`, enums `Rarity` et `Category`, valeurs de vente |
| `player.py` | Classes `Player` et `PlayerStats` |
| `inventory.py` | Inventaire, CardDex, règles de fusion (`FUSION_RULES`) |
| `achievements.py` | 27 succès définis par lambdas, `AchievementManager` |
| `card_repository.py` | Accès aux cartes en DB (pattern Repository) |
| `chest.py` | Classe `Chest`, enum `ChestType` |

### engine/ - Moteur Pygame

| Fichier | Rôle |
|---------|------|
| `scene_manager.py` | Boucle principale 60 FPS, pile de scènes, transitions, overlays |
| `asset_manager.py` | Cache d'images/sons, chargement lazy, polices |
| `ui_components.py` | Button, Panel, Label, CoinDisplay, ProgressBar, ScrollView, Toast, AchievementBanner, CardWidget |

### logic/ - Systèmes de jeu

| Fichier | Rôle |
|---------|------|
| `generator.py` | Génération probabiliste des coffres (slots fixes, GODPACK, DIVINE) |
| `shop_system.py` | Shop persistant avec cycle de restock (3h) |
| `fusion_system.py` | Mise en place d'une fusion (validation -> exécution -> DB) |
| `daily_manager.py` | Récompenses quotidiennes avec système de streak |

### scenes/ - Écrans du jeu (8 scènes)

| Scène | Description |
|-------|-------------|
| `loading_scene.py` | Chargement DB en thread, barre de progression |
| `menu_scene.py` | Menu principal, 7 boutons |
| `chest_scene.py` | Sélection coffre -> animation ouverture -> reveal cartes |
| `inventory_scene.py` | Grille filtrée, vente unitaire / par rareté |
| `shop_scene.py` | 3 slots avec timer restock, popup de confirmation |
| `fusion_scene.py` | Dépôt de 3 cartes, animation forge, résultat |
| `daily_scene.py` | 7 cases de récompenses, streak, particules |
| `carddex_scene.py` | 756 cartes, filtres, popup de détail |
| `achievements_scene.py` | Liste des 27 succès avec filtres et dates |

---

## apps/arcade_game/

### engine/

| Fichier | Rôle |
|---------|------|
| `level.py` | Boucle de jeu, gestion des vagues, collisions, spawn |
| `eventmanager.py` | Bus d'événements avec enum d'événements |
| `soundmanager.py` | Gestion des sons réactifs aux événements |
| `screeneffects.py` | Flash d'écran, affichage score, annonce de vague |
| `tile.py` | Tuile du niveau (mur, fond, bords) |

### entities/

| Fichier | Rôle |
|---------|------|
| `player.py` | Joueur : déplacement, animations, tir, dégâts, DB sync |
| `entity.py` | Ennemi : états (FOLLOW/ATTACK/HURT/DEAD), IA de poursuite |
| `gun.py` | Arme : rotation vers la souris, recul, déblocage |
| `bullet.py` | Projectile : trajectoire, collision raycasting |
| `collectible.py` | Collectible flottant (point, vie, arme) |

---

## apps/web_stats/

Serveur Flask minimal avec 3 routes HTML et 2 routes API :
- `/api/cards` -> JSON de toutes les cartes (pour CardDex JS)
- `/cards/<path>` -> images des cartes
- `/data/<path>` -> accès à game.db pour sql.js (stats côté client)

---

## Flux de données principal

```
Arcade Game
    │  (ramasse un point)
    ▼
PLAYER_STATS.coins += 1   (SQLite - game.db)
    │
    ▼
Card Simulator
    │  (charge le joueur)
    ▼
load_player(1) -> Player.coins = valeur DB
    │
    ▼
Achète un coffre (250 pièces)
    │
    ▼
db_open_chest() -> PLAYER_CARDS, PLAYER_CARDDEX,
                    PLAYER_RARITY_STATS mis à jour
```