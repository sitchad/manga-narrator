from models.db import get_db_connection
from gtts import gTTS
import io

def get_mangas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas")
    mangas = cur.fetchall()
    cur.close()
    conn.close()
    return mangas

def get_page_data(manga_id, num_page):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image_url, texte_narration FROM pages WHERE manga_id = %s AND numero_page = %s", (manga_id, num_page))
    page = cur.fetchone()
    cur.close()
    conn.close()
    return page

def generate_audio_stream(text):
    tts = gTTS(text=text or "Fin de l'histoire", lang='fr', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp
