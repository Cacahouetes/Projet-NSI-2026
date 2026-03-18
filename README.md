# Card Opening Simulator — Trophées NSI 2026

## Prérequis

- Python 3.11 ou supérieur
- Système : Windows ou Linux

## Installation des dépendances

```bash
pip install -r requirements.txt
```

## Lancement du projet

```bash
python main.py
```

Le launcher s'ouvre et permet de choisir entre :
- **Card Simulator** : ouvrir des coffres, fusionner des cartes, gérer son inventaire
- **Arcade Game** : jeu de tir en vagues pour gagner des pièces
- **WebStats** : statistiques détaillées dans le navigateur (Flask)

## Structure du projet

```
sources/
├── main.py (launcher)
├── server.py (WebStats)
├── data/
│   └── database_manager.py (opérations SQLite)
├── apps/
│   ├── card_simulator/
│   │   ├── core/ (cartes, joueur, inventaire)
│   │   ├── engine/ (scènes, assets, UI)
│   │   ├── logic/ (générateur de coffres, shop, fusion, daily)
│   │   └── scenes/ (tous les écrans du jeu)
│   ├── arcade_game/
│   │   ├── engine/ (niveau, événements, sons, effets)
│   │   └── entities/ (joueur, ennemis, projectiles, collectibles)
│   └── web_stats/
│       ├── templates/ (pages HTML)
│       └── static/ (CSS)
└── assets/
    ├── Cards/ (756 illustrations de cartes)
    ├── card_game/ (sons, coffres, icônes UI)
    └── arcade_game/ (sprites, sons, niveau)
```

## Base de données

Le fichier `data/game.db` est une base SQLite fournir pour permettre le lancement.

## Notes importantes

- La base de données `game.db` doit être accessible en écriture.
- Le serveur WebStats (Flask) utilise le port 5000 par défaut.
- Les assets audio nécessitent un pilote son système (SDL2_mixer).

## Version Python testée

Python 3.11.x