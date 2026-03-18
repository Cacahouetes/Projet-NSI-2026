## Nature du code et usage de l'IA

### Degré de création originale

L'intégralité du code a été écrite par les membres de l'équipe. Les seuls éléments externes sont les bibliothèques listées dans `requirements.txt` (pygame, flask) et la bibliothèque JavaScript sql.js utilisée côté client pour lire la base de données SQLite dans le navigateur sans serveur intermédiaire.

Aucun code existant n'a été copié ou adapté depuis des tutoriels, dépôts GitHub ou autres sources. Les algorithmes (générateur probabiliste de coffres, moteur de scènes Pygame, système de fusion, gestion des streaks daily) sont des conceptions originales de l'équipe.

### Citation des sources externes

- **pygame 2.5+** : bibliothèque graphique et sonore ([pygame.org](https://www.pygame.org))
- **Flask 3.0+** : micro-framework web Python ([flask.palletsprojects.com](https://flask.palletsprojects.com))
- **sql.js 1.10** : port WebAssembly de SQLite pour le navigateur ([sql.js.org](https://sql.js.org))

### Utilisation de pygame - justification

Le règlement déconseille l'usage de pygame pour deux raisons : incompatibilités entre versions et problèmes potentiels à l'exécution sur différentes plateformes. Nous avons conscience de ce risque et avons pris les mesures suivantes pour le limiter :

**Pourquoi pygame malgré tout.** Le cœur de notre projet est un jeu vidéo avec animations, gestion des événements en temps réel, rendu graphique et sons. Aucune bibliothèque Python explicitement au programme ne permet de réaliser cela. Tkinter ne gère pas les animations fluides ni le son. pygame est la seule option raisonnable pour un projet de cette nature en Python.

**Mesures prises pour garantir la reproductibilité.**
- La version minimale requise est spécifiée dans `requirements.txt` (`pygame>=2.5.0`), ce qui évite d'installer une ancienne version incompatible.
- Le projet a été testé sur Windows 11 et Linux avec Python 3.11 et Python 3.12.
- Les sons utilisent uniquement le format `.wav` et `.mp3`, qui sont les formats les plus universellement supportés par SDL2_mixer.
- Aucun appel à des fonctionnalités dépréciées de pygame n'est effectué.
- `pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)` est appelé avec des paramètres explicites pour éviter les variations de configuration par défaut selon les plateformes.

### Usage de l'intelligence artificielle

L'IA (Claude, Anthropic) a été utilisée ponctuellement comme outil d'aide au développement, de manière réfléchie et limitée, dans les cas suivants :

- **Débogage** : soumission de messages d'erreur pour identifier rapidement la cause de bugs (erreurs SQLite de concurrence, imports circulaires Python).
- **Revue de code** : vérification de la cohérence de certaines requêtes SQL complexes (notamment les transactions multi-tables dans `database_manager.py`).
- **Documentation** : aide à la rédaction de certaines docstrings et commentaires en français.

L'IA n'a pas généré de logique métier, d'algorithmes, ni de code d'interface. Toutes les décisions d'architecture (structure de la base de données, moteur de scènes, système probabiliste de coffres) ont été conçues et implémentées par l'équipe.