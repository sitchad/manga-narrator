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

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_url TEXT,
                texte_narration TEXT
            )
        ''')
        cursor.executemany('''INSERT INTO pages (image_url, texte_narration) VALUES (?, ?)''', [
            ("https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500", "Chapitre 1. Le jeune garçon au chapeau de paille regarde l'océan avec détermination."),
            ("https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500", "Soudain, un monstre marin géant surgit des vagues en hurlant !")
        ])
        conn.commit()
        conn.close()

init_db()

@app.route('/')
@app.route('/page/<int:page_id>')
def lecteur(page_id=1):
    cursor = get_db().cursor()
    cursor.execute("SELECT image_url, texte_narration FROM pages WHERE id = ?", (page_id,))
    page = cursor.fetchone()
    
    if not page:
        return "<body style='background:#121212;color:white;text-align:center;padding-top:100px;'><h1>Fin du chapitre ! 🎉</h1><a href='/page/1' style='color:#ff4757;'>Recommencer</a></body>", 200

    image_url, texte = page

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Manga Narration</title>
        <style>
            body {{ background: #121212; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px; }}
            .manga-card {{ max-width: 500px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
            .manga-img {{ width: 100%; border-radius: 5px; margin-bottom: 15px; }}
            .narration-text {{ font-size: 1.2rem; min-height: 50px; margin: 15px 0; color: #e0e0e0; }}
            .btn {{ background: #ff4757; color: white; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn:hover {{ background: #ff6b81; }}
            audio {{ width: 100%; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>Manga Audio Narrateur 🎙️</h1>
        <div class="manga-card">
            <img class="manga-img" src="{image_url}" alt="Manga Page">
            <p class="narration-text">"{texte}"</p>
            <audio autoplay controls src="/audio/{page_id}"></audio>
            <br><br>
            <a class="btn" href="/page/{page_id + 1}">Page Suivante ➡️</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/audio/<int:page_id>')
def generer_audio(page_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT texte_narration FROM pages WHERE id = ?", (page_id,))
    res = cursor.fetchone()
    texte = res[0] if res else "Fin de l'histoire"
    
    tts = gTTS(text=texte, lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return send_file(audio_fp, mimetype="audio/mp3")

if __name__ == '__main__':
    app.run(debug=True)
