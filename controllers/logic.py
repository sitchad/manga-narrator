import io
from gtts import gTTS
from models.db import get_db_connection

def fetch_all_mangas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas")
        mangas = cursor.fetchall()
        cursor.close()
        conn.close()
        return mangas
    except Exception:
        return []

def insert_manga(titre, cover, desc, note, badge):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mangas (titre, cover_url, description, note, badge) VALUES (%s, %s, %s, %s, %s)",
        (titre, cover, desc, note, badge)
    )
    conn.commit()
    cursor.close()
    conn.close()

def insert_page(manga_id, num_page, image_url, texte_narration):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (manga_id, numero_page, image_url, texte_narration) VALUES (%s, %s, %s, %s)",
        (manga_id, num_page, image_url, texte_narration)
    )
    conn.commit()
    cursor.close()
    conn.close()

def fetch_manga_page(manga_id, num_page):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_url, texte_narration FROM pages WHERE manga_id = %s AND numero_page = %s", (manga_id, num_page))
    page = cursor.fetchone()
    cursor.close()
    conn.close()
    return page

def create_audio_stream(manga_id, num_page):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT texte_narration FROM pages WHERE manga_id = %s AND numero_page = %s", (manga_id, num_page))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    
    texte = res[0] if res else "Fin de l'histoire"
    tts = gTTS(text=texte, lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp
