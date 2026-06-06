def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 🔥 ON NETTOIE TOUT : On supprime les anciennes tables pour repartir à zéro
        print("Nettoyage complet de la base de données...")
        cursor.execute('DROP TABLE IF EXISTS pages CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS mangas CASCADE;')
        
        # 1. Recréation propre de la table des MANGAS
        print("Création de la table mangas...")
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
        
        # 2. Recréation propre de la table des PAGES (Cases)
        print("Création de la table pages...")
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
        print("Base de données Supabase entièrement réinitialisée avec succès !")
    except Exception as e:
        print(f"Erreur critique lors de l'initialisation : {e}")

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
