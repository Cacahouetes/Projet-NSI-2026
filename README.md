# [Projet NSI 2026](https://docs.google.com/spreadsheets/d/1n4fikJw8G8MA9upVi2Dh-BntDpIMKS9zqnmdwYS13cg/edit?usp=sharing)

## Cahier des charges

## 1. Présentation générale du projet

Le projet consiste à développer un **jeu vidéo en Python** composé de **deux jeux interconnectés** :

1. **Un jeu arcade**, permettant au joueur de gagner des points.
2. **Un Card Opening Simulator**, dans lequel les points gagnés servent à ouvrir des boosters de cartes à collectionner.

## 2. Contraintes techniques

* **Langage** : Python
* **Bibliothèques principales** :

  * `pygame` : interface graphique, animations, sons
  * `sqlite3` : base de données locale
  * `json` : export et consultation des données (CardDex)
* **Plateforme** : PC
* **Création des cartes** : logiciel tiers

## 3. Structure globale du jeu

* **Menu principal** :

  * Lancer le jeu arcade
  * Accéder au Card Opening Simulator
  * Consulter le CardDex (collection)
  * Consulter les statistiques du joueur
* Interface claire et intuitive
* Sauvegarde automatique de la progression

## 4. Jeu 1 : Jeu Arcade

### Objectif

Permettre au joueur de gagner des **points**, utilisés comme monnaie pour ouvrir des boosters.

### Principe et fonctionnalités

* À définir
* Jeu en 2D en vagues
* Le joueur doit éliminer tous les ennemis afin de passer à la vague suivante
* Les ennemis deviennent de plus nombreux et plus forts 
* Le joueur peut obtenir des power-ups et de nouvelles armes
* Le joueur peut tirer et se battre sans armes (peut etre que j'ajouterai une grenade??)
* Il peut aussi sauter, s'accroupir et courir (et tirer simultanément)


### Lien avec le Card Opening Simulator

* Les points gagnés sont stockés dans le profil joueur
* Ils sont dépensés pour acheter des boosters

## 5. Jeu 2 : Card Opening Simulator

### Objectif

Collectionner des cartes en ouvrant des boosters obtenus grâce aux points.

---

### 5.1 Raretés

Le jeu comporte **7 niveaux de rareté** :

1. Commune
2. Rare
3. Épique
4. Légendaire
5. Mythique
6. Unique (1 par catégorie thématique)
7. Divine (hors-échelle)

---

### 5.2 Cartes et catégories

* **756 cartes** au total

  * **151 cartes** par catégorie thématique
  * **1 carte Divine** dans tout le jeu

Catégories thématiques :

* Meme
* Mots
* Objets
* Personnages
* Concepts

---

## 6. Système global de boosters

### Principes communs

* Un booster contient **10 cartes** par défaut
* Les cartes sont générées via un **tirage probabiliste pur**
* **Aucun système de pity** n’est présent

Avant toute génération de cartes, un **tirage préalable** détermine le **type de booster**.

## 7. Boosters de catégorie (**151 cartes**)

### 7.1 Répartition des cartes

* 70 Communes
* 40 Rares
* 20 Épiques
* 12 Légendaires
* 8 Mythiques
* 1 Unique

---

### 7.2 Tirage du type de booster

| Type de booster  | Probabilité                 |
| ---------------- | --------------------------- |
| Booster standard | ~99,499 %                   |
| **GODPACK**      | **1 / 200 (0,5 %)**         |
| **DIVINE PACK**  | **1 / 67 067 (~0,00149 %)** |
| **Total**        | **100 %**                   |

---

### 7.3 Booster standard (slots fixes)

Le booster standard utilise un **système de slots fixes**, inspiré des boosters Pokémon.

#### Composition (10 cartes)

* **Slots 1 à 6** : Commune (100 %)
* **Slots 7 à 9** :

  * Rare : 75 %
  * Épique : 25 %
* **Slot 10** :

  * Rare : 55 %
  * Épique : 30 %
  * Légendaire : 10 %
  * Mythique : 4,9 %
  * Unique : 0,1 %

Les cartes sont tirées uniformément dans la rareté obtenue. L’ordre des slots correspond à l’ordre d’affichage.

---

### 7.4 GODPACK

Booster ultra-rare ne contenant **que des cartes de haute rareté**.

| Rareté     | Probabilité |
| ---------- | ----------- |
| Légendaire | 70 %        |
| Mythique   | 29 %        |
| Unique     | 1 %         |

Chaque carte est tirée indépendamment.

---

### 7.5 DIVINE PACK

Booster extrêmement rare.

* Contient **10 cartes Divines**
* La rareté Divine est hors-pool et hors-équilibrage standard

## 8. Omni-Booster (**756 cartes**)

Booster premium permettant d’obtenir des cartes de **toutes les catégories**.

### Différences principales

* Pool global de 756 cartes
* Moins de communes garanties
* Plus forte exposition aux hautes raretés

### Slots (10 cartes)

* Slots 1 à 6 : Commune (100 %)
* Slots 6 à 8 : Rare (60 %) / Épique (40 %)
* Slots 10 :

  * Épique : 40 %
  * Légendaire : 35 %
  * Mythique : 24.5 %
  * Unique : 0.5 %

Le tirage GODPACK / DIVINE PACK est identique aux boosters de catégorie.

## 9. Carte Divine - Carte bonus universelle

Après la génération complète d’un booster, un **tirage bonus indépendant** est effectué.

| Événement              | Probabilité               |
| ---------------------- | ------------------------- |
| Aucune carte Divine    | 99,9967 %                 |
| **Carte Divine bonus** | **0,0033 % (1 / 30 000)** |

* La carte Divine s’ajoute comme **11ᵉ carte**
* Applicable à **tous les boosters**
* Les cas extrêmes (DIVINE PACK + carte Divine bonus) sont volontairement possibles

## 10. Ordre logique complet de génération d’un booster

1. Tirage du type de booster
2. Génération des 10 cartes selon le type
3. Tirage bonus de la Carte Divine
4. Ajout éventuel d’une 11ᵉ carte

## 11. Base de données (CardDex)

### Données des cartes

* ID
* Nom
* Catégorie
* Rareté
* Description
* Image
* Probabilité

### Données joueur

* Pseudo
* Points
* Cartes possédées
* Boosters ouverts
* Statistiques

## 12. Statistiques

* Taux de drop par rareté
* Nombre de doublons
* Progression de collection
* Historique des ouvertures

## 13. Répartition du travail

* **Fafa** : jeu arcade, menu, musiques
* **Thyraël** : Card Opening Simulator, logique des boosters
* **Tristan & Augustin** : base de données, CardDex, statistiques

## 14. Évolutions possibles

* Échanges de cartes
* Événements temporaires
* Nouveaux boosters
* Classements joueurs
