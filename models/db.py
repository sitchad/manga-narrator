def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. On supprime l'ancienne table qui cause l'erreur de colonne manquante
        print("Suppression de l'ancienne table pages...")
        cursor.execute('DROP TABLE IF EXISTS pages CASCADE;')
        
        # 2. On recrée la table des mangas (sans y toucher)
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
        
        # 3. On crée la nouvelle table pages avec TOUTES les bonnes colonnes
        print("Création de la nouvelle table pages...")
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
        print("Base de données mise à jour avec succès sur Supabase !")
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
