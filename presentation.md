# Card Opening Simulator - Présentation du projet

## 1. Présentation globale

### Naissance de l'idée

L'idée est née de notre passion commune pour les jeux de cartes à collectionner (Pokémon, Clash Royale...) et les jeux vidéo arcade. Nous voulions recréer la sensation d'ouvrir un booster et compléter une collection, en y ajoutant une dimension de jeu pour gagner les ressources nécessaires.

### Problématique initiale

Comment concevoir un système de jeu complet en Python avec deux mécaniques différentes, un jeu d'action et un simulateur de collection avec une base de données partagée tout en proposant une interface graphique fluide et une visualisation web des statistiques ?

### Objectifs

- Développer un **jeu arcade 2D** en vagues progressives avec système d'armes et d'ennemis
- Concevoir un **simulateur de coffres** avec 756 cartes, 7 raretés et probabilités réalistes
- Relier les deux jeux via une **base de données SQLite partagée** (pièces gagnées en arcade = monnaie du simulateur)
- Proposer une **interface web** (Flask) pour consulter ses statistiques
- Implémenter des systèmes de jeu complets : fusions, shop, daily rewards, succès, CardDex

---

## 2. Organisation du travail

### Présentation de l'équipe

Équipe de 4 élèves de Terminale NSI.

### Répartition des tâches

| Membre | Rôle principal |
|--------|----------------|
| Fahreddin | Jeu arcade (engine, entités, effets) · Musiques, sons et texture|
| Thyraël | Card Opening Simulator · Générateur de coffres · Logique de probabilités |
| Tristan | Base de données SQLite · CardDex · Statistiques web |
| Augustin | Base de données SQLite · Interface Flask · Statistiques web |

Chaque membre a réalisé une partie technique significative du projet. Les décisions d'architecture (structure de la DB, API entre les jeux, choix des bibliothèques) ont été prises collectivement.

### Temps passé

- Conception et architecture : ~10h (équipe complète)
- Développement jeu arcade : ~20h (Fahreddin)
- Développement card simulator : ~35h (Thyraël)
- Base de données et web : ~10h (Tristan + Augustin)
- Tests, débogage, intégration : ~4h (équipe complète)
- Documentation : ~4h (équipe complète)

---

## 3. Étapes du projet

### Phase 1 - Conception (septembre–octobre 2025)
Définition du périmètre, choix des librairies (Pygame, SQLite, Flask), conception du schéma de base de données (17 tables).

### Phase 2 - Développement parallèle (novembre 2025–janvier 2026)
- Fahreddin développe le moteur arcade (déplacement, collisions, vagues d'ennemis)
- Thyraël construit le moteur de scènes Pygame et le système de coffres
- Tristan et Augustin construisent `database_manager.py` et les requêtes SQL

### Phase 3 - Intégration (mars 2026)
Connexion des deux jeux via la DB partagée, ajout du launcher, synchronisation des pièces entre arcade et card simulator.

### Phase 4 - Finitions (mi-mars 2026)
Système de réinitialisation de sauvegarde, corrections de bugs, documentation, tests.

---

## 4. Validation du fonctionnement

### État d'avancement au dépôt

Le projet est **fonctionnel dans son intégralité** :
- Jeu arcade : vagues infinies, 3 armes, système de collectibles 
- Card simulator : 756 cartes, 7 scènes, coffres/fusion/shop/daily
- Liaison DB partagée : pièces synchronisées entre les deux jeux
- WebStats : 3 pages (accueil, CardDex interactif, statistiques par joueur)
- Reset de sauvegarde avec recréation du joueur

### Difficultés rencontrées et solutions

**Gestion des imports circulaires (card simulator)**
Le card simulator utilise ~15 modules Python qui s'importent mutuellement. Solution : imports locaux à l'intérieur des fonctions pour casser les cycles.

**Synchronisation DB entre les deux jeux**
Les deux jeux accèdent à la même DB simultanément. Solution : une seule connexion par opération avec les transactions atomiques (`with conn:`).

**Chemins de fichiers multi-plateforme**
Utilisation systématique de `os.path.join()` et `os.sep.join()` pour garantir la compatibilité Windows/macOS/Linux.

---

## 5. Ouverture

### Idées d'amélioration

- Système d'échange de cartes entre joueurs
- Événements temporaires (boosters saisonniers)
- Mode multijoueur local pour l'arcade
- Export des statistiques en CSV/PDF
- Application mobile (interface web responsive)

### Analyse critique

Le choix de Pygame est assumé malgré la déconseillation du règlement : aucune bibliothèque Python au programme ne permet de créer des interfaces graphiques animées aussi facilement. Nous avons pris soin de tester sur Windows et Linux pour garantir la reproductibilité.

L'utilisation de Flask pour la partie web est marginale par rapport au cœur Python/Pygame/SQLite du projet.

### Compétences développées

- Conception de bases de données relationnelles (17 tables, contraintes FK)
- Programmation orientée objet avancée (héritage, composition, patterns)
- Algorithmique probabiliste (système de tirages pondérés)
- Développement web minimal (Flask, JavaScript vanilla, SQL.js)

### Démarche d'inclusion

L'équipe est composée de 4 garçons. Nous avons veillé à une répartition équilibrée des tâches techniques : chaque membre a contribué à des aspects backend (DB, logique) et frontend (interface).