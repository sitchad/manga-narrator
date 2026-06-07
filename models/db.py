import psycopg2

def get_db_connection():
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
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        print("[-] Connexion Supabase OK")
    except Exception as e:
        print(f"[!] Erreur Connexion Supabase: {e}")

# ==========================================
#                  MANGAS
# ==========================================

def db_get_all_mangas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, photo_url, description FROM mangas ORDER BY id DESC;")
    mangas = cursor.fetchall()
    cursor.close()
    conn.close()
    return mangas

def db_get_manga_by_id(manga_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, photo_url, description FROM mangas WHERE id = %s;", (manga_id,))
    manga = cursor.fetchone()
    cursor.close()
    conn.close()
    return manga

def db_insert_manga(nom, photo_url, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mangas (nom, photo_url, description) VALUES (%s, %s, %s);", (nom, photo_url, description))
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
#                 CHAPITRES
# ==========================================

def db_get_chapitres_by_manga(manga_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero, titre, couverture_chapitre_url FROM chapitres WHERE manga_id = %s ORDER BY numero ASC;", (manga_id,))
    chapitres = cursor.fetchall()
    cursor.close()
    conn.close()
    return chapitres

def db_get_chapitre_numero(chapitre_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT numero FROM chapitres WHERE id = %s;", (chapitre_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def db_insert_chapitre(manga_id, numero, titre, couverture_chapitre_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chapitres (manga_id, numero, titre, couverture_chapitre_url) VALUES (%s, %s, %s, %s);", 
        (int(manga_id), int(numero), titre, couverture_chapitre_url)
    )
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
#                  PAGES
# ==========================================

def db_get_page(chapitre_id, numero_page):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_url, texte_narration FROM pages WHERE chapitre_id = %s AND numero_page = %s;", (chapitre_id, numero_page))
    page = cursor.fetchone()
    cursor.close()
    conn.close()
    return page

def db_check_next_page(chapitre_id, numero_page):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pages WHERE chapitre_id = %s AND numero_page = %s;", (chapitre_id, numero_page + 1))
    has_next = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return has_next

def db_insert_page(chapitre_id, numero_page, image_url, texte_narration):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (chapitre_id, numero_page, image_url, texte_narration) VALUES (%s, %s, %s, %s);", 
        (int(chapitre_id), int(numero_page), image_url, texte_narration)
    )
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
#         OPTIONS DE SUPPRESSION
# ==========================================

def db_delete_manga(manga_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mangas WHERE id = %s;", (manga_id,))
    conn.commit()
    cursor.close()
    conn.close()

def db_delete_chapitre(chapitre_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapitres WHERE id = %s;", (chapitre_id,))
    conn.commit()
    cursor.close()
    conn.close()

def db_delete_cases_by_chapitre(chapitre_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages WHERE chapitre_id = %s;", (chapitre_id,))
    conn.commit()
    cursor.close()
    conn.close()
