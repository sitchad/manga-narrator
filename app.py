from flask import Flask, render_template
from models.db import init_db
from controllers.logic import (
    liste_tous_les_mangas, afficher_manga, lire_page_manga, charger_panel_admin,
    ajouter_nouveau_manga, ajouter_nouveau_chapitre, ajouter_cases_chapitre,
    supprimer_manga_action, supprimer_chapitre_action, vider_cases_action,
    api_prochain_chapitre_numero
)

app = Flask(__name__)

try:
    init_db()
except Exception as e:
    print(f"Alerte démarrage database: {e}")

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
    return charger_panel_admin()

@app.route('/admin/api/prochain-chapitre/<int:manga_id>')
def admin_api_next_chap(manga_id):
    return api_prochain_chapitre_numero(manga_id)

@app.route('/admin/ajouter-manga', methods=['POST'])
def admin_add_manga():
    return ajouter_nouveau_manga()

@app.route('/admin/ajouter-chapitre', methods=['POST'])
def admin_add_chapitre():
    return ajouter_nouveau_chapitre()

@app.route('/admin/ajouter-cases', methods=['POST'])
def admin_add_cases():
    return ajouter_cases_chapitre()

@app.route('/admin/supprimer-manga/<int:manga_id>')
def admin_delete_manga(manga_id):
    return supprimer_manga_action(manga_id)

@app.route('/admin/supprimer-chapitre/<int:chapitre_id>')
def admin_delete_chapitre(chapitre_id):
    return supprimer_chapitre_action(chapitre_id)

@app.route('/admin/vider-cases/<int:chapitre_id>')
def admin_clear_cases(chapitre_id):
    return vider_cases_action(chapitre_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
