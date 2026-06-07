import io
import asyncio
import edge_tts
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mangas (titre, cover_url, description, note, badge) VALUES (%s, %s, %s, %s, %s)",
            (titre, cover, desc, note, badge)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur insertion manga : {e}")

def insert_page(manga_id, num_chapitre, num_case, image_url, texte_narration):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pages (manga_id, num_chapitre, numero_page, image_url, texte_narration) VALUES (%s, %s, %s, %s, %s)",
            (manga_id, num_chapitre, num_case, image_url, texte_narration)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur insertion case : {e}")

def fetch_manga_page(manga_id, num_chapitre, num_case):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT image_url, texte_narration FROM pages WHERE manga_id = %s AND num_chapitre = %s AND numero_page = %s", 
            (manga_id, num_chapitre, num_case)
        )
        page = cursor.fetchone()
        cursor.close()
        conn.close()
        return page
    except Exception as e:
        print(f"Erreur récupération case : {e}")
        return None

def create_audio_stream(manga_id, num_chapitre, num_case):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT texte_narration FROM pages WHERE manga_id = %s AND num_chapitre = %s AND numero_page = %s", 
            (manga_id, num_chapitre, num_case)
        )
        res = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur SQL audio : {e}")
        res = None
    
    texte = res[0] if res else "Fin de l'histoire"
    
    # Configuration de la voix Microsoft (HenriNeural = Voix d'homme cinéma)
    # Tu peux la remplacer par "fr-FR-DeniseNeural" si tu préfères une voix de femme
    voix_choisie = "fr-FR-HenriNeural" 
    
    # Fonction asynchrone pour générer le flux audio avec Edge-TTS
    async def generate_voice() -> bytes:
        communicate = edge_tts.Communicate(texte, voix_choisie)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["data"]:
                audio_data += chunk["data"]
        return audio_data

    # Exécution de la coroutine dans l'environnement synchrone de Flask
    audio_bytes = asyncio.run(generate_voice())
    
    audio_fp = io.BytesIO(audio_bytes)
    audio_fp.seek(0)
    return audio_fp
