from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'apps', 'web_stats', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'apps', 'web_stats', 'static'))

# Sert les pages HTML
@app.route('/')
def index():
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

# Sert la base de données depuis data/
@app.route('/data/<path:filename>')
def serve_data(filename):
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    return send_from_directory(data_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
