from flask import Flask, render_template
from models.db import init_db
from controllers.logic import (
    liste_tous_les_mangas, afficher_manga, lire_page_manga,
    ajouter_nouveau_manga, ajouter_nouveau_chapitre, ajouter_cases_chapitre
)

app = Flask(__name__)
init_db()

# --- CLIENT ---
@app.route('/')
def index():
    return liste_tous_les_mangas()

@app.route('/manga/<int:manga_id>')
def manga_detail(manga_id):
    return afficher_manga(manga_id)

@app.route('/manga/<int:manga_id>/<int:chapitre_id>/<int:numero_page>')
def manga_reader(manga_id, chapitre_id, numero_page):
    return lire_page_manga(manga_id, chapitre_id, numero_page)

# --- ADMIN ---
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/ajouter-manga', methods=['POST'])
def admin_add_manga():
    return ajouter_nouveau_manga()

@app.route('/admin/ajouter-chapitre', methods=['POST'])
def admin_add_chapitre():
    return ajouter_nouveau_chapitre()

@app.route('/admin/ajouter-cases', methods=['POST'])
def admin_add_cases():
    return ajouter_cases_chapitre()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
