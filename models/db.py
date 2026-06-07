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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Désactiver les verrous pour éviter que ça bloque si une ancienne requête tourne encore
        cursor.execute("SET statement_timeout = 30000;")
        
        # 1. Suppression propre des anciennes tables
        cursor.execute("DROP TABLE IF EXISTS pages CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS mangas CASCADE;")
        
        # 2. Création de la table mangas
        cursor.execute('''
            CREATE TABLE mangas (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                cover_url TEXT,
                description TEXT,
                note TEXT,
                badge TEXT
            );
        ''')
        
        # 3. Création de la table pages (avec num_chapitre et numero_page)
        cursor.execute('''
            CREATE TABLE pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER,
                num_chapitre INTEGER,
                numero_page INTEGER,
                image_url TEXT,
                texte_narration TEXT
            );
        ''')
        
        conn.commit()
        cursor.close()
        print("Supabase a bien été nettoyé et recréé à neuf !")
    except Exception as e:
        print(f"Erreur d'initialisation de la base : {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
