from flask import Flask, render_template_string, send_file, request, redirect
import psycopg2
import urllib.parse
from gtts import gTTS
import io

app = Flask(__name__)

# Configuration de la base de données sécurisée
DB_PASSWORD = "19902450aA@zZ#"

def get_db_connection():
    safe_password = urllib.parse.quote_plus(DB_PASSWORD)
    return psycopg2.connect(
        database="postgres",
        user="postgres.liiyfrmmwqsbsjbnmrwj",
        password=safe_password,
        host="aws-0-eu-west-1.pooler.supabase.com",
        port="6543"
    )

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mangas (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                cover_url TEXT,
                description TEXT,
                note TEXT,
                badge TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER,
                numero_page INTEGER,
                image_url TEXT,
                texte_narration TEXT
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de données initialisée.")
    except Exception as e:
        print(f"Erreur d'initialisation : {e}")

init_db()

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas")
        mangas = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erreur de connexion à la base de données : {e}", 500
    
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
            body {{ background: #0b0b0c; color: white; font-family: sans-serif; margin: 0; padding: 20px; }}
            header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4757; padding-bottom: 15px; margin-bottom: 30px; }}
            .logo {{ font-size: 1.8rem; font-weight: bold; color: white; text-decoration: none; }}
            .logo span {{ color: #ff4757; }}
            .nav-admin {{ background: #27272a; color: white; text-decoration: none; padding: 8px 15px; border-radius: 5px; font-size: 0.9rem; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #18181b; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }}
            .cover-container {{ height: 280px; background-size: cover; background-position: center; position: relative; }}
            .badge {{ position: absolute; bottom: 10px; left: 10px; background: #ff4757; color: white; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; }}
            .card-body {{ padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }}
            .card-body h3 {{ margin: 0 0 8px 0; }}
            .card-body p {{ margin: 0 0 15px 0; color: #a1a1aa; font-size: 0.85rem; flex-grow: 1; }}
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
            .btn-play {{ background: #ff4757; color: white; text-decoration: none; padding: 6px 12px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <header>
            <a href="/" class="logo">Manga<span>Cine</span></a>
            <a href="/admin" class="nav-admin">Panneau Admin ⚙️</a>
        </header>
        <div class="grid">{mangas_html}</div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/manga/<int:manga_id>/page/<int:num_page>')
def lecteur(manga_id, num_page):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT image_url, texte_narration FROM pages WHERE manga_id = %s AND numero_page = %s", (manga_id, num_page))
        page = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Erreur de base de données : {e}", 500
    
    if not page:
        return "<body style='background:#0b0b0c;color:white;text-align:center;padding-top:100px;'><h1>Fin du Chapitre ! 🎉</h1><br><a href='/' style='color:#ff4757;'>Retour à l'accueil</a></body>", 200

    image_url, texte = page
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lecture</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
            .player-container {{ max-width: 500px; margin: 10px auto; background: #18181b; padding: 20px; border-radius: 10px; }}
            .manga-img {{ width: 100%; border-radius: 6px; }}
            .text {{ font-size: 1.1rem; color: #e4e4e7; margin: 20px 0; }}
            .btn {{ background: #ff4757; color: white; text-decoration: none; padding: 12px 24px; border-radius: 5px; display: inline-block; }}
            audio {{ width: 100%; margin-top: 15px; }}
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

@app.route('/audio/<int:manga_id>/<int:num_page>')
def generer_audio(manga_id, num_page):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT texte_narration FROM pages WHERE manga_id = %s AND numero_page = %s", (manga_id, num_page))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception:
        res = None
    
    texte = res[0] if res else "Fin de l'histoire"
    tts = gTTS(text=texte, lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return send_file(audio_fp, mimetype="audio/mp3")

@app.route('/admin', methods=['GET', 'POST'])
def admin_manga():
    if request.method == 'POST':
        titre = request.form['titre']
        cover = request.form['cover']
        desc = request.form['desc']
        note = request.form['note']
        badge = request.form['badge']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mangas (titre, cover_url, description, note, badge) VALUES (%s, %s, %s, %s, %s)", (titre, cover, desc, note, badge))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/admin')
        
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Admin - Mangas</title>
        <style>
            body {{ background: #0b0b0c; color: white; font-family: sans-serif; padding: 20px; max-width: 500px; margin: 0 auto; }}
            form {{ background: #18181b; padding: 20px; border-radius: 8px; }}
            input, textarea, select {{ width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 4px; border: 1px solid #27272a; background: #0b0b0c; color: white; box-sizing: border-box; }}
            button {{ background: #ff4757; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <form method="POST">
            <h2>➕ Ajouter un Manga</h2>
            <input type="text" name="titre" placeholder="Titre" required>
            <input type="url" name="cover" placeholder="URL Couverture" required>
            <textarea name="desc" placeholder="Description" rows="3" required></textarea>
            <input type="text" name="note" placeholder="Note (ex: 8.5)" required>
            <select name="badge">
                <option value="POPULAIRE">Populaire</option>
                <option value="TENDANCE">Tendance</option>
                <option value="NOUVEAU">Nouveau</option>
            </select>
            <button type="submit">Enregistrer</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
