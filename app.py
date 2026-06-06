from flask import Flask, render_template_string, send_file, g
import sqlite3
import os
from gtts import gTTS
import io

app = Flask(__name__)
DB_NAME = "manga_narration.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Nouvelle base de données avec Table MANGAS + Table PAGES
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table pour la liste des mangas sur la page d'accueil
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mangas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            cover_url TEXT,
            description TEXT,
            note TEXT,
            badge TEXT
        )
    ''')
    
    # Table pour les pages de lecture internes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manga_id INTEGER,
            numero_page INTEGER,
            image_url TEXT,
            texte_narration TEXT
        )
    ''')
    
    # Remplissage automatique si vide pour le test
    cursor.execute("SELECT COUNT(*) FROM mangas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''INSERT INTO mangas (titre, cover_url, description, note, badge) VALUES (?, ?, ?, ?, ?)''', [
            ("One Piece", "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500", "Luffy part à l'aventure pour devenir le roi des pirates.", "9.8", "POPULAIRE"),
            ("Naruto Shuden", "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500", "Le jeune ninja de Konoha cherche à faire reconnaître sa valeur.", "8.5", "NOUVEAU"),
            ("Demon Slayer", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500", "Tanjiro se bat pour sauver sa soeur transformée en démon.", "9.0", "TENDANCE")
        ])
        
        # Pages de lecture pour One Piece (manga_id = 1)
        cursor.executemany('''INSERT INTO pages (manga_id, numero_page, image_url, texte_narration) VALUES (?, ?, ?, ?)''', [
            (1, 1, "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500", "Chapitre 1. Le jeune garçon au chapeau de paille regarde l'océan avec détermination."),
            (1, 2, "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500", "Soudain, un monstre marin géant surgit des vagues en hurlant !")
        ])
        
    conn.commit()
    conn.close()

if not os.path.exists(DB_NAME):
    init_db()

# 🏠 ROUTE 1 : La page d'accueil style Netflix/Cine (Uniquement Mangas)
@app.route('/')
def home():
    cursor = get_db().cursor()
    cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas")
    mangas = cursor.fetchall()
    
    # Construction des cartes de mangas en HTML/CSS
    mangas_html = ""
    for m in mangas:
        m_id, titre, cover, desc, note, badge = m
        mangas_html += f"""
        <div class="card">
            <div class="cover-container" style="background-image: url('{cover}');">
                <span class="badge">{badge}</span>
            </div>
            <div class="card-body">
                <h3>{titre}</h3>
                <p>{desc}</p>
                <div class="card-footer">
                    <span class="rating">⭐ {note}</span>
                    <a href="/manga/{m_id}/page/1" class="btn-play">Lire 🎙️</a>
                </div>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MANGA CINE - Accueil</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; }}
            header {{ display: flex; align-items: center; border-bottom: 2px solid #ff4757; padding-bottom: 15px; margin-bottom: 30px; }}
            .logo {{ font-size: 1.8rem; font-weight: bold; color: white; text-transform: uppercase; }}
            .logo span {{ color: #ff4757; }}
            h2 {{ color: #ffffff; border-left: 4px solid #ff4757; padding-left: 10px; font-size: 1.4rem; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #18181b; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.6); display: flex; flex-direction: column; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); }}
            .cover-container {{ height: 280px; background-size: cover; background-position: center; position: relative; }}
            .badge {{ position: absolute; bottom: 10px; left: 10px; background: #ff4757; color: white; font-size: 0.75rem; font-weight: bold; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }}
            .card-body {{ padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }}
            .card-body h3 {{ margin: 0 0 8px 0; font-size: 1.1rem; color: #fff; }}
            .card-body p {{ margin: 0 0 15px 0; font-size: 0.85rem; color: #a1a1aa; line-height: 1.4; flex-grow: 1; }}
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
            .rating {{ color: #ffb81c; font-weight: bold; font-size: 0.9rem; }}
            .btn-play {{ background: #ff4757; color: white; text-decoration: none; padding: 6px 12px; font-size: 0.85rem; border-radius: 4px; font-weight: bold; }}
            .btn-play:hover {{ background: #ff6b81; }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo">Manga<span>Cine</span></div>
        </header>
        
        <h2>📚 Tous les Mangas</h2>
        <div class="grid">
            {mangas_html}
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# 📖 ROUTE 2 : Le lecteur audio interne pour chaque manga
@app.route('/manga/<int:manga_id>/page/<int:num_page>')
def lecteur(manga_id, num_page):
    cursor = get_db().cursor()
    cursor.execute("SELECT image_url, texte_narration FROM pages WHERE manga_id = ? AND numero_page = ?", (manga_id, num_page))
    page = cursor.fetchone()
    
    if not page:
        return "<body style='background:#0b0b0c;color:white;text-align:center;padding-top:100px;font-family:sans-serif;'><h1>Fin du Chapitre ! 🎉</h1><br><a href='/' style='color:#ff4757;font-weight:bold;text-decoration:none;'>Retour à l'accueil</a></body>", 200

    image_url, texte = page

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lecture Manga</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px; margin: 0; }}
            .player-container {{ max-width: 500px; margin: 20px auto; background: #18181b; padding: 20px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.8); }}
            .manga-img {{ width: 100%; border-radius: 6px; }}
            .text {{ font-size: 1.1rem; color: #e4e4e7; margin: 20px 0; min-height: 40px; }}
            .btn {{ background: #ff4757; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px; }}
            audio {{ width: 100%; margin-top: 15px; background: #27272a; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="player-container">
            <img class="manga-img" src="{image_url}">
            <p class="text">"{texte}"</p>
            <audio autoplay controls src="/audio/{manga_id}/{num_page}"></audio>
            <br><br>
            <a class="btn" href="/manga/{manga_id}/page/{num_page + 1}">Page Suivante ➡️</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# 🎙️ ROUTE 3 : Génération de la voix Google
@app.route('/audio/<int:manga_id>/<int:num_page>')
def generer_audio(manga_id, num_page):
    cursor = get_db().cursor()
    cursor.execute("SELECT texte_narration FROM pages WHERE manga_id = ? AND numero_page = ?", (manga_id, num_page))
    res = cursor.fetchone()
    texte = res[0] if res else "Fin de l'histoire"
    
    tts = gTTS(text=texte, lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return send_file(audio_fp, mimetype="audio/mp3")

if __name__ == '__main__':
    app.run(debug=True)
