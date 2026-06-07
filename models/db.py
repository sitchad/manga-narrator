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
        cursor.execute("SET statement_timeout = 30000;")

        print("Nettoyage de l'ancienne structure en cours...")
        # MÉTHODE RADICALE : On supprime les anciennes tables pour enlever les bugs
        cursor.execute("DROP TABLE IF EXISTS votes CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS pages CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS mangas CASCADE;")

        print("Reconstruction d'une base de données neuve et propre...")
        # Table des mangas toute neuve
        cursor.execute('''
            CREATE TABLE mangas (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                cover_url TEXT,
                description TEXT,
                note FLOAT DEFAULT 0.0,
                badge TEXT
            );
        ''')

        # Table des pages toute neuve
        cursor.execute('''
            CREATE TABLE pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER REFERENCES mangas(id) ON DELETE CASCADE,
                num_chapitre INTEGER,
                numero_page INTEGER,
                image_url TEXT,
                texte_narration TEXT
            );
        ''')

        # Table des votes toute neuve
        cursor.execute('''
            CREATE TABLE votes (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER REFERENCES mangas(id) ON DELETE CASCADE,
                ip_utilisateur TEXT,
                valeur_note INTEGER CHECK (valeur_note >= 1 AND valeur_note <= 10)
            );
        ''')

        conn.commit()
        cursor.close()
        print("Base de données nettoyée et réinitialisée avec succès !")
    except Exception as e:
        print(f"Erreur lors du nettoyage/initialisation : {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
