import psycopg2


def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ⚠️ AJOUTE CETTE LIGNE ICI POUR SUPPRIMER L'ANCIENNE TABLE OBSOLÈTE :
        cursor.execute('DROP TABLE IF EXISTS pages CASCADE;')
        
        # Table des Mangas (elle ne bouge pas)
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
        
        # Cette fois, elle sera recréée proprement avec toutes les colonnes !
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER,
                num_chapitre INTEGER,
                numero_page INTEGER,
                image_url TEXT,
                texte_narration TEXT
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de données réinitialisée avec succès.")
    except Exception as e:
        print(f"Erreur d'initialisation : {e}")


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
        
        # Table des Mangas
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
        
        # Table des Cases (reliée au Chapitre)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id SERIAL PRIMARY KEY,
                manga_id INTEGER,
                num_chapitre INTEGER,
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
