from flask import Flask, render_template, send_file, request, redirect, session
from models.db import init_db

app = Flask(__name__)
app.secret_key = "manga_cine_secret_key_2026"
ADMIN_PASSWORD = "AdminCine2026!"

import controllers.logic as controller

init_db()

@app.route('/')
def home():
    mangas = controller.fetch_all_mangas()
    return render_template('home.html', mangas=mangas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = ""
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect('/admin')
        erreur = "Mot de passe incorrect ❌"
    return render_template('login.html', erreur=erreur)

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin_manga():
    if not session.get('is_admin'):
        return redirect('/login')
    if request.method == 'POST':
        controller.insert_manga(
            request.form['titre'], request.form['cover'],
            request.form['desc'], request.form['note'], request.form['badge']
        )
        return redirect('/admin')
    return render_template('admin_manga.html')

@app.route('/admin/page', methods=['GET', 'POST'])
def admin_page():
    if not session.get('is_admin'):
        return redirect('/login')
    if request.method == 'POST':
        controller.insert_page(
            request.form['manga_id'], 
            request.form['num_chapitre'],
            request.form['num_case'], 
            request.form['image_url'], 
            request.form['texte_narration']
        )
        return redirect('/admin/page')
    mangas = controller.fetch_all_mangas()
    return render_template('admin_page.html', mangas=mangas)

@app.route('/manga/<int:manga_id>/chapitre/<int:num_chapitre>/case/<int:num_case>')
def lecteur(manga_id, num_chapitre, num_case):
    try:
        page = controller.fetch_manga_page(manga_id, num_chapitre, num_case)
        if not page:
            return render_template('error.html', message="Fin du Chapitre ! 🎉")
        return render_template('lecteur.html', image_url=page[0], texte=page[1], manga_id=manga_id, num_chapitre=num_chapitre, num_case=num_case)
    except Exception as e:
        return render_template('error.html', message=f"Erreur lecteur : {str(e)}")

@app.route('/audio/<int:manga_id>/<int:num_chapitre>/<int:num_case>')
def generer_audio(manga_id, num_chapitre, num_case):
    try:
        audio_stream = controller.create_audio_stream(manga_id, num_chapitre, num_case)
        return send_file(audio_stream, mimetype="audio/mp3")
    except Exception as e:
        return f"Erreur Audio : {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
