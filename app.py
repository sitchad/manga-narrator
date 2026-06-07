from flask import Flask
from models.db import init_db
import controllers.logic as controller

app = Flask(__name__)

# Initialisation automatique des tables au démarrage sans perte de données
init_db()

@app.route('/')
def index():
    return controller.liste_tous_les_mangas()

@app.route('/manga/<int:manga_id>')
def manga_detail(manga_id):
    return controller.afficher_manga(manga_id)

@app.route('/manga/<int:manga_id>/chapitre/<int:num_chapitre>/page/<int:numero_page>')
def lire_manga(manga_id, num_chapitre, numero_page):
    return controller.lire_page_manga(manga_id, num_chapitre, numero_page)

# Route raccourcie pour ouvrir directement la première page d'un chapitre
@app.route('/manga/<int:manga_id>/chapitre/<int:num_chapitre>')
def commencer_chapitre(manga_id, num_chapitre):
    return controller.lire_page_manga(manga_id, num_chapitre, 1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
