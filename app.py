from flask import Flask, render_template
from models.db import init_db
import controllers.logic as controller

app = Flask(__name__)

# Initialisation de la base sans écraser les données
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

@app.route('/manga/<int:manga_id>/chapitre/<int:num_chapitre>')
def commencer_chapitre(manga_id, num_chapitre):
    return controller.lire_page_manga(manga_id, num_chapitre, 1)

@app.route('/manga/voter', methods=['POST'])
def manga_voter():
    return controller.voter_pour_manga()

# --- ROUTES ADMIN ---
@app.route('/admin')
def page_admin():
    conn = controller.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre FROM mangas ORDER BY id DESC;")
    mangas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", mangas=mangas)

@app.route('/admin/manga/add', methods=['POST'])
def admin_add_manga():
    return controller.ajouter_nouveau_manga()

@app.route('/admin/chapitre/add', methods=['POST'])
def admin_add_chapitre():
    return controller.ajouter_cases_chapitre()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
