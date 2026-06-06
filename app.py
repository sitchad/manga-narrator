from flask import Flask, render_template_string, send_file, request, redirect, session
import psycopg2
import urllib.parse
from gtts import gTTS
import io

app = Flask(__name__)
# Clé secrète obligatoire pour gérer les sessions de connexion
app.secret_key = "manga_cine_secret_key_2026"

# Mot de passe pour ton accès Admin (tu peux le modifier ici)
ADMIN_PASSWORD = "AdminCine2026!"

def get_db_connection():
    safe_password = urllib.parse.quote_plus("19902450aA@zZ#")
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
        mangas_html = "<p style='color: #a1a1aa; text-align: center;'>Aucun manga disponible.</p>"

    # On affiche le bouton Admin et Logout UNIQUEMENT si tu es connecté en session
    admin_btn = ""
    if session.get('is_admin'):
        admin_btn = """
        <div>
            <a href="/admin" style="background: #27272a; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Admin ⚙️</a>
            <a href="/logout" style="background: #ff4757; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px;">Quitter 🚪</a>
        </div>
        """

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
            {admin_btn}
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px;">
            {mangas_html}
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# --- SYSTÈME DE CONNEXION ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = ""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect('/admin')
        else:
            erreur = "Mot de passe incorrect ❌"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Connexion Admin</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; text-align: center; padding-top: 100px;">
        <div style="max-width: 350px; margin: 0 auto; background: #18181b; padding: 30px; border-radius: 8px;">
            <h2>Espace Admin 🔒</h2>
            <p style="color: #ff4757;">{erreur}</p>
            <form method="POST">
                <input type="password" name="password" placeholder="Mot de passe" required style="width: 100%; padding: 10px; margin: 15px 0; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px; box-sizing: border-box;">
                <button type="submit" style="width: 100%; background: #ff4757; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer;">Se connecter</button>
            </form>
            <br><a href="/" style="color: #a1a1aa; text-decoration: none; font-size: 0.9rem;">← Retour au site</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect('/')

# --- PANNEAU ADMIN SÉCURISÉ ---

@app.route('/admin', methods=['GET', 'POST'])
def admin_manga():
    # Sécurité : Si pas connecté, redirection forcée vers le login
    if not session.get('is_admin'):
        return redirect('/login')

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
    <head><meta charset="UTF-8"><title>Admin - Mangas</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; padding: 20px; max-width: 500px; margin: 0 auto;">
        <nav style="margin-bottom: 25px;"><a href="/" style="color: #ff4757; text-decoration: none; font-weight: bold;">🏠 Accueil</a> | <a href="/admin/page" style="color: #ff4757; text-decoration: none; font-weight: bold; margin-left: 10px;">📖 Gérer les Pages →</a></nav>
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
            <button type="submit" style="background: #ff4757; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer;">Enregistrer le Manga</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/admin/page', methods=['GET', 'POST'])
def admin_page():
    # Sécurité : Si pas connecté, redirection forcée
    if not session.get('is_admin'):
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        manga_id = request.form['manga_id']
        num_page = request.form['num_page']
        image_url = request.form['image_url']
        texte_narration = request.form['texte_narration']
        
        cursor.execute("INSERT INTO pages (manga_id, numero_page, image_url, texte_narration) VALUES (%s, %s, %s, %s)", (manga_id, num_page, image_url, texte_narration))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/admin/page')
        
    cursor.execute("SELECT id, titre FROM mangas")
    mangas = cursor.fetchall()
    cursor.close()
    conn.close()
    options = "".join([f"<option value='{m[0]}'>{m[1]}</option>" for m in mangas])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Admin - Pages</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; padding: 20px; max-width: 500px; margin: 0 auto;">
        <nav style="margin-bottom: 25px;"><a href="/admin" style="color: #ff4757; text-decoration: none; font-weight: bold;">← Revenir aux Mangas</a></nav>
        <h2>📖 Ajouter une Page / Chapitre</h2>
        <form method="POST" style="background: #18181b; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <label style="margin-bottom: 5px; font-size: 0.9rem; color: #a1a1aa;">Choisir le Manga :</label>
            <select name="manga_id" required style="padding: 10px; margin-bottom: 15px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">{options}</select>
            
            <input type="number" name="num_page" placeholder="Numéro de la page (ex: 1)" required style="padding: 10px; margin-bottom: 15px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
            <input type="url" name="image_url" placeholder="URL de l'image de la page" required style="padding: 10px; margin-bottom: 15px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;">
            <textarea name="texte_narration" placeholder="Texte de la narration (lu par la voix off)" rows="4" required style="padding: 10px; margin-bottom: 15px; background: #0b0b0c; color: white; border: 1px solid #27272a; border-radius: 4px;"></textarea>
            
            <button type="submit" style="background: #ff4757; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer;">Enregistrer la Page</button>
        </form>
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
        return "<body style='background:#0b0b0c;color:white;text-align:center;padding-top:100px;'><h1>Fin du Chapitre ! 🎉</h1><br><a href='/' style='color:#ff4757; font-weight:bold; text-decoration:none;'>Retour à l'accueil</a></body>", 200

    image_url, texte = page
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Lecture</title></head>
    <body style="background: #0b0b0c; color: white; font-family: sans-serif; text-align: center; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #18181b; padding: 20px; border-radius: 10px;">
            <img src="{image_url}" style="width: 100%; border-radius: 6px;">
            <p style="font-size: 1.2rem; margin: 20px 0;">"{texte}"</p>
            <audio id="mangaAudio" autoplay controls src="/audio/{manga_id}/{num_page}" style="width: 100%;"></audio>
            <br><br>
            <a href="/manga/{manga_id}/page/{num_page + 1}" style="background: #ff4757; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Page Suivante ➡️</a>
        </div>
        <script>
            // Rythme guidé par la narration : passe automatiquement à la page suivante quand l'audio se termine
            var audio = document.getElementById('mangaAudio');
            audio.onended = function() {
                window.location.href = "/manga/" + {manga_id} + "/page/" + ({num_page} + 1);
            };
        </script>
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

if __name__ == '__main__':
    app.run(debug=True)
