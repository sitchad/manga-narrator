from flask import Flask, render_template_string, send_file, request, redirect
import psycopg2
from gtts import gTTS
import io

app = Flask(__name__)

def get_db_connection():
    # Configuration explicite par paramètres pour éviter les conflits de caractères spéciaux
    return psycopg2.connect(
        database="postgres",
        user="postgres.liiyfrmmwqsbsjbnmrwj",
        password="19902450aA@zZ#",
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
        print("Base de données initialisée avec succès.")
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
        <div class="card" style="background: #18181b; border-radius: 8px; padding: 15px; margin: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <img src="{cover}" style="width: 100%; height: 250px; object-fit: cover; border-radius: 6px;">
            <h3>{titre}</h3>
            <p style="color: #a1a1aa; font-size: 0.9rem;">{desc}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #ffb81c;">⭐ {note} ({badge})</span>
                <a href="/manga/{m_id}/page/1" style="background: #ff4757; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-weight: bold;">Lire 🎙️</a>
            </div>
        </div>
        """

    if not mangas_html:
        mangas_html = "<p style='color: #a1a1aa; text-align: center;'>Aucun manga disponible. <a href='/admin' style='color:#ff4757;'>Ajouter ici</a></p>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manga Cine</title>
    </head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4757; padding-bottom: 10px;">
            <h1>Manga<span style="color: #ff4757;">Cine</span></h1>
            <a href="/admin" style="background: #27272a; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px;">Admin ⚙️</a>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px;">
            {mangas_html}
        </div>
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
    <head><meta charset="UTF-8"><title>Lecture</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; text-align: center; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #18181b; padding: 20px; border-radius: 10px;">
            <img src="{image_url}" style="width: 100%; border-radius: 6px;">
            <p style="font-size: 1.2rem; margin: 20px 0;">"{texte}"</p>
            <audio autoplay controls src="/audio/{manga_id}/{num_page}" style="width: 100%;"></audio>
            <br><br>
            <a href="/manga/{manga_id}/page/{num_page + 1}" style="background: #ff4757; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Page Suivante ➡️</a>
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
    <head><meta charset="UTF-8"><title>Admin</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; padding: 20px; max-width: 500px; margin: 0 auto;">
        <h2>➕ Ajouter un Manga</h2>
        <form method="POST" style="background: #18181b; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <input type="text" name="titre" placeholder="Titre du Manga" required style="padding: 10px; margin-bottom: 10px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
            <input type="url" name="cover" placeholder="URL Image Couverture" required style="padding: 10px; margin-bottom: 10px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
            <textarea name="desc" placeholder="Résumé / Description" rows="3" required style="padding: 10px; margin-bottom: 10px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;"></textarea>
            <input type="text" name="note" placeholder="Note (ex: 9.2)" required style="padding: 10px; margin-bottom: 10px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
            <select name="badge" style="padding: 10px; margin-bottom: 15px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
                <option value="POPULAIRE">Populaire</option>
                <option value="TENDANCE">Tendance</option>
                <option value="NOUVEAU">Nouveau</option>
            </select>
            <button type="submit" style="background: #ff4757; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 4px;">Enregistrer</button>
        </form>
        <br><a href="/" style="color: #ff4757; text-decoration: none;">⬅️ Retour au site</a>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
