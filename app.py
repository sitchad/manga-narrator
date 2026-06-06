from flask import Flask, render_template_string, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from gtts import gTTS
import io

app = Flask(__name__)

# ⚠️ REMPLACE CETTE ADRESSE PAR TON VRAI LIEN SUPABASE MAIS EN REMPLAÇANT "postgresql://" PAR "postgresql+psycopg2://"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000:19902450aA@zZ#@db.liiyfrmmwqsbsjbnmrwj.supabase.co:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🗂️ MODÈLES DE BASE DE DONNÉES
class Manga(db.Model):
    __tablename__ = 'mangas'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    cover_url = db.Column(db.Text)
    description = db.Column(db.Text)
    note = db.Column(db.String(50))
    badge = db.Column(db.String(50))

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer)
    numero_page = db.Column(db.Integer)
    image_url = db.Column(db.Text)
    texte_narration = db.Column(db.Text)

with app.app_context():
    db.create_all()

# 🏠 ACCUEIL STYLE NETFLIX
@app.route('/')
def home():
    mangas = Manga.query.all()
    mangas_html = ""
    for m in mangas:
        mangas_html += f"""
        <div class="card">
            <div class="cover-container" style="background-image: url('{m.cover_url}');">
                <span class="badge">{m.badge}</span>
            </div>
            <div class="card-body">
                <h3>{m.titre}</h3>
                <p>{m.description}</p>
                <div class="card-footer">
                    <span class="rating">⭐ {m.note}</span>
                    <a href="/manga/{m.id}/page/1" class="btn-play">Lire 🎙️</a>
                </div>
            </div>
        </div>
        """
    if not mangas_html:
        mangas_html = "<p style='color: #a1a1aa; grid-column: 1/-1; text-align: center;'>Aucun manga pour le moment. Allez sur <a href='/admin' style='color:#ff4757;'>/admin</a> pour en ajouter !</p>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MANGA CINE</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; }}
            header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4757; padding-bottom: 15px; margin-bottom: 30px; }}
            .logo {{ font-size: 1.8rem; font-weight: bold; color: white; text-transform: uppercase; text-decoration: none; }}
            .logo span {{ color: #ff4757; }}
            .nav-admin {{ background: #27272a; color: white; text-decoration: none; padding: 8px 15px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; }}
            h2 {{ color: #ffffff; border-left: 4px solid #ff4757; padding-left: 10px; font-size: 1.4rem; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #18181b; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.6); display: flex; flex-direction: column; }}
            .cover-container {{ height: 280px; background-size: cover; background-position: center; position: relative; }}
            .badge {{ position: absolute; bottom: 10px; left: 10px; background: #ff4757; color: white; font-size: 0.75rem; font-weight: bold; padding: 4px 8px; border-radius: 4px; }}
            .card-body {{ padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }}
            .card-body h3 {{ margin: 0 0 8px 0; font-size: 1.1rem; }}
            .card-body p {{ margin: 0 0 15px 0; font-size: 0.85rem; color: #a1a1aa; flex-grow: 1; }}
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
            .rating {{ color: #ffb81c; font-weight: bold; }}
            .btn-play {{ background: #ff4757; color: white; text-decoration: none; padding: 6px 12px; font-size: 0.85rem; border-radius: 4px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo">Manga<span>Cine</span></a>
            <a href="/admin" class="nav-admin">Panneau Admin ⚙️</a>
        </header>
        <h2>📚 Tous les Mangas</h2>
        <div class="grid">{mangas_html}</div>
    </body>
    </html>
    """
    return render_template_string(html)

# 📖 LECTEUR DE PAGE
@app.route('/manga/<int:manga_id>/page/<int:num_page>')
def lecteur(manga_id, num_page):
    page = Page.query.filter_by(manga_id=manga_id, numero_page=num_page).first()
    if not page:
        return "<body style='background:#0b0b0c;color:white;text-align:center;padding-top:100px;font-family:sans-serif;'><h1>Fin du Chapitre ! 🎉</h1><br><a href='/' style='color:#ff4757;font-weight:bold;text-decoration:none;font-size:1.2rem;'>Retour à l'accueil</a></body>", 200

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lecture</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px; margin:0; }}
            .player-container {{ max-width: 500px; margin: 10px auto; background: #18181b; padding: 20px; border-radius: 10px; }}
            .manga-img {{ width: 100%; border-radius: 6px; }}
            .text {{ font-size: 1.1rem; color: #e4e4e7; margin: 20px 0; }}
            .btn {{ background: #ff4757; color: white; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-weight: bold; display: inline-block; }}
            audio {{ width: 100%; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="player-container">
            <img class="manga-img" src="{page.image_url}">
            <p class="text">"{page.texte_narration}"</p>
            <audio autoplay controls src="/audio/{manga_id}/{num_page}"></audio>
            <br><br>
            <a class="btn" href="/manga/{manga_id}/page/{num_page + 1}">Page Suivante ➡️</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# 🎙️ AUDIO
@app.route('/audio/<int:manga_id>/<int:num_page>')
def generer_audio(manga_id, num_page):
    page = Page.query.filter_by(manga_id=manga_id, numero_page=num_page).first()
    texte = page.texte_narration if page else "Fin de l'histoire"
    tts = gTTS(text=texte, lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return send_file(audio_fp, mimetype="audio/mp3")

# ⚙️ ADMIN MANGA
@app.route('/admin', methods=['GET', 'POST'])
def admin_manga():
    if request.method == 'POST':
        nouveau_manga = Manga(
            titre=request.form['titre'],
            cover_url=request.form['cover'],
            description=request.form['desc'],
            note=request.form['note'],
            badge=request.form['badge']
        )
        db.session.add(nouveau_manga)
        db.session.commit()
        return redirect('/admin')
        
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin - Mangas</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: Arial, sans-serif; padding: 20px; max-width: 500px; margin: 0 auto; }}
            nav {{ margin-bottom: 20px; }}
            nav a {{ color: #ff4757; margin-right: 15px; font-weight: bold; text-decoration: none; }}
            form {{ background: #18181b; padding: 20px; border-radius: 8px; }}
            input, textarea, select {{ width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 4px; border: 1px solid #27272a; background: #0b0b0c; color: white; box-sizing: border-box; }}
            button {{ background: #ff4757; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <nav><a href="/">⬅️ Retour au site</a> | <a href="/admin/page">Ajouter des pages ➡️</a></nav>
        <h2>➕ Ajouter un nouveau Manga</h2>
        <form method="POST">
            <label>Titre du Manga :</label><input type="text" name="titre" required>
            <label>Lien URL de la Couverture :</label><input type="url" name="cover" required>
            <label>Résumé / Description :</label><textarea name="desc" rows="3" required></textarea>
            <label>Note (sur 10) :</label><input type="text" name="note" required>
            <label>Badge :</label>
            <select name="badge">
                <option value="POPULAIRE">Populaire</option>
                <option value="TENDANCE">Tendance</option>
                <option value="NOUVEAU">Nouveau</option>
            </select>
            <button type="submit">Enregistrer le Manga</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

# ⚙️ ADMIN PAGE
@app.route('/admin/page', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        nouvelle_page = Page(
            manga_id=int(request.form['manga_id']),
            numero_page=int(request.form['num_page']),
            image_url=request.form['image_url'],
            texte_narration=request.form['texte']
        )
        db.session.add(nouvelle_page)
        db.session.commit()
        return redirect('/admin/page')
        
    mangas = Manga.query.all()
    options = "".join([f"<option value='{m.id}'>{m.titre}</option>" for m in mangas])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin - Pages</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: Arial, sans-serif; padding: 20px; max-width: 500px; margin: 0 auto; }}
            nav {{ margin-bottom: 20px; }}
            nav a {{ color: #ff4757; margin-right: 15px; font-weight: bold; text-decoration: none; }}
            form {{ background: #18181b; padding: 20px; border-radius: 8px; }}
            input, textarea, select {{ width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 4px; border: 1px solid #27272a; background: #0b0b0c; color: white; box-sizing: border-box; }}
            button {{ background: #ff4757; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <nav><a href="/admin">⬅️ Ajouter un Manga</a> | <a href="/">Aller sur le site ➡️</a></nav>
        <h2>📖 Ajouter une Page à un Manga</h2>
        <form method="POST">
            <label>Choisir le Manga :</label>
            <select name="manga_id" required>{options}</select>
            <label>Numéro de la page :</label><input type="number" name="num_page" required>
            <label>Lien URL de l'image :</label><input type="url" name="image_url" required>
            <label>Texte de la narration :</label><textarea name="texte" rows="4" required></textarea>
            <button type="submit">Enregistrer la Page</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
