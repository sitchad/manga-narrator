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

        # Table des mangas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mangas (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                cover_url TEXT,
                description TEXT,
                note FLOAT DEFAULT 0.0,
                badge TEXT
            );
        ''')

        # Table des pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER,
                num_chapitre INTEGER,
                numero_page INTEGER,
                image_url TEXT,
                texte_narration TEXT
            );
        ''')

        # Table des votes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER REFERENCES mangas(id) ON DELETE CASCADE,
                ip_utilisateur TEXT,
                valeur_note INTEGER CHECK (valeur_note >= 1 AND valeur_note <= 10)
            );
        ''')

        conn.commit()
        cursor.close()
        print("Structure de la base de données vérifiée et validée !")
    except Exception as e:
        print(f"Erreur d'initialisation : {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
