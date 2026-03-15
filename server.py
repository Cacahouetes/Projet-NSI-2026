from flask import Flask, render_template, send_from_directory, jsonify
import os
import sqlite3

# os.path.dirname(__file__) retourne le dossier contenant ce fichier
BASE_DIR = os.path.dirname(__file__)

# Chemin vers la base de données SQLite
DB_PATH = os.path.join(BASE_DIR, 'data', 'game.db')


# template_folder → dossier où Flask cherche les fichiers HTML (render_template)
# static_folder   → dossier où Flask sert les fichiers CSS, JS, images statiques
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'apps', 'web_stats', 'templates'),
            static_folder=os.path.join(BASE_DIR,   'apps', 'web_stats', 'static'))


# Chaque @app.route() associe une URL à une fonction Python.
# render_template() cherche le fichier dans le template_folder défini et renvoie son contenu au navigateur.

@app.route('/')
def index():
    # Racine du site → redirige vers la page d'accueil
    return render_template('Accueil.html')

@app.route('/accueil')
def accueil():
    return render_template('Accueil.html')

@app.route('/carddex')
def carddex():
    return render_template('Card_Dex.html')

@app.route('/stats')
def stats():
    return render_template('stat.html')



# ROUTE API : /api/cards
# Renvoie toutes les cartes de la table CARDS au format JSON.
# Utilisée par Card_Dex.html via fetch('/api/cards') en JavaScript.
#
# sqlite3.connect() ouvre la base en lecture.
# conn.row_factory = sqlite3.Row permet d'accéder aux colonnes par nom
# dict(row) convertit chaque ligne en dictionnaire Python,
# que jsonify() sérialise ensuite en JSON pour le navigateur.


@app.route('/api/cards')
def api_cards():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        'SELECT card_id, name, rarity, category, stat1, stat2, stat3, '
        'description, author, image_path FROM CARDS ORDER BY card_id'
    )
    cards = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(cards)


# ROUTE IMAGES : /cards/<filename>
# Sert les images des cartes stockées dans assets/Cards/.
#
# <path:filename> est un paramètre de route Flask qui accepte des chemins
# avec des sous-dossiers (ex. "Commune/1.png", "Rare/71.png").
#
# send_from_directory() renvoie le fichier demandé en vérifiant qu'il
# se trouve bien dans le dossier autorisé.


@app.route('/cards/<path:filename>')
def serve_card_image(filename):
    cards_folder = os.path.join(BASE_DIR, 'assets', 'Cards')
    return send_from_directory(cards_folder, filename)


# ROUTE BASE DE DONNÉES : /data/<filename>
# Sert les fichiers du dossier data/.
# Utilisée par stat.html qui télécharge game.db via sql.js pour
# exécuter des requêtes SQLite directement dans le navigateur.

@app.route('/data/<path:filename>')
def serve_data(filename):
    data_folder = os.path.join(BASE_DIR, 'data')
    return send_from_directory(data_folder, filename)



# LANCEMENT DU SERVEUR
# Ce bloc ne s'exécute que si on lance directement "python server.py" dans le terminal,
# pas si server.py est importé comme module par un autre script.
#
# port=5000   → adresse d'accès : http://localhost:5000

if __name__ == '__main__':
    app.run(port=5000)