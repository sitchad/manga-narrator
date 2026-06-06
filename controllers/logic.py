from models.db import get_db_connection
from gtts import gTTS
import io

def get_mangas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titre, cover_url FROM mangas")
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
