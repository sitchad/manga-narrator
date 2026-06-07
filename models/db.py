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

        # ON ENLÈVE LES DROP TABLE POUR NE PLUS RIEN SUPPRIMER !

        # Création de la table mangas (SEULEMENT SI ELLE N'EXISTE PAS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mangas (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                cover_url TEXT,
                description TEXT,
                note TEXT,
                badge TEXT
            );
        ''')

        # Création de la table pages (SEULEMENT SI ELLE N'EXISTE PAS)
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

        conn.commit()
        cursor.close()
        print("Base de données vérifiée : les tables existantes ont été conservées !")
    except Exception as e:
        print(f"Erreur d'initialisation de la base : {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
