# Projet NSI 2026

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
    * `json` : export et consultation des données (CardDex en ligne)
* **Plateforme** : PC
* **Création des cartes** :
    * Utilisation d’un logiciel tiers

## 3. Structure globale du jeu

* **Menu principal** :
  * Lancer le jeu arcade
  * Accéder au Card Opening Simulator
  * Consulter la collection de cartes (CardDex)
  * Voir les statistiques du joueur
* Interface claire et intuitive
* Sauvegarde automatique de la progression du joueur

## 4. Jeu 1 : Jeu Arcade

### Objectif

Permettre au joueur de gagner des **points**, utilisés comme monnaie pour ouvrir des boosters.

### Principe du jeu

* à developper
* à developper
* à developper

### Fonctionnalités

* à developper
* à developper
* à developper

### Lien avec le Card Opening Simulator

* Les points gagnés sont stockés dans le profil du joueur
* Ils peuvent être dépensés pour acheter des boosters

## 5. Jeu 2 : Card Opening Simulator

### Objectif

Collectionner des cartes en ouvrant des boosters obtenus grâce aux points.

### Catégories de cartes

#### Raretés (7 niveaux)

* Commune
* Rare
* Épique
* Légendaire
* Mythique
* Unique (1 carte par catégorie thématique)
* Divine (1 seule carte dans tout le jeu)

#### Nombres de cartes
* **756 cartes**
    * **151 cartes** par catégorie
    * **1 cartes** divine

#### Catégories thématiques (CardDex)

* Meme
* Mots
* Objets
* Personnages
* Concepts

Chaque catégorie thématique possède :

* **151 cartes**
    * 70 Communes
    * 40 Rares
    * 20 Épiques
    * 12 Légendaires
    * 8 Mythiques
    * 1 Unique
* une identité visuelle propre

---

### Système de rareté
#### Boosters de catégorie (**151 cartes**)
Proba à définir

#### Omni-Booster (**756 cartes**)
Proba à définir

### Boosters

* Prix en points
* Contiennent un nombre fixe de cartes (**10**)
* Animation d’ouverture
* Cartes triée par rareté
* Révélation des cartes une par une
* Effets visuels et sonores selon la rareté

## 6. Base de données (CardDex)

### Objectif

Centraliser toutes les informations liées aux cartes et aux joueurs.

### Données des cartes

* ID unique
* Nom
* Catégorie thématique
* Rareté
* Description
* Image
* Probabilité d’apparition

### Données joueur

* Pseudo
* Nombre de points
* Cartes possédées
* Nombre de boosters ouverts
* Statistiques globales

### Accès

* Consultation locale via le jeu
* Option : accès via Internet (lecture seule) pour afficher la collection complète

## 7. Statistiques et suivi

* Taux de drop par rareté
* Nombre de doublons
* Progression de la collection (% complété)
* Historique des ouvertures de boosters

## 8. Direction artistique et son

* **Direction artistique (DA)** :

  * Design des cartes
  * Interface du menu
  * Interface du CardDex
* **Musique d’ambiance** :

  * Fafa le fé
* **Effets sonores** :

  * Ouverture de booster
  * Cartes de rareté élevée

## 9. Répartition du travail (cohérente et équilibrée)

* **Fafa**

  * Jeu arcade
  * Menu principal
  * Musiques

* **Thyraël**

  * Card Opening Simulator
  * Logique des boosters et raretés

* **Tristan & Augustin**

  * Base de données
  * Statistiques
  * CardDex

* **Direction artistique**

  * Cartes : Tristan, Thyraël & Augustin
  * Menu & musique : Fafa
  * CardDex : Tristan & Augustin

## 10. Évolutions possibles

* Système d’échange de cartes
* Événements temporaires
* Nouveaux boosters
* Classement des joueurs