from flask import render_template, abort
from models.db import get_db_connection

def liste_tous_les_mangas():
    """Affiche la page d'accueil avec tous les mangas disponibles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas;")
    mangas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", mangas=mangas)

def afficher_manga(manga_id):
    """Affiche le profil d'un manga avec sa liste de chapitres uniques."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer les détails du manga
    cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas WHERE id = %s;", (manga_id,))
    manga = cursor.fetchone()
    
    if not manga:
        cursor.close()
        conn.close()
        abort(404, description="Manga introuvable")

    # Extraire la liste des chapitres uniques existants dans la table pages
    cursor.execute("""
        SELECT DISTINCT num_chapitre 
        FROM pages 
        WHERE manga_id = %s 
        ORDER BY num_chapitre ASC;
    """, (manga_id,))
    
    chapitres = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return render_template("manga.html", manga=manga, chapitres=chapitres)

def lire_page_manga(manga_id, num_chapitre, numero_page):
    """Gère le lecteur de manga case par case en suivant le rythme de la narration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer la case/page actuelle
    cursor.execute("""
        SELECT image_url, texte_narration 
        FROM pages 
        WHERE manga_id = %s AND num_chapitre = %s AND numero_page = %s;
    """, (manga_id, num_chapitre, numero_page))
    page_actuelle = cursor.fetchone()
    
    if not page_actuelle:
        cursor.close()
        conn.close()
        return render_template("fin_chapitre.html", manga_id=manga_id, num_chapitre=num_chapitre)

    # Vérifier s'il y a une page suivante pour le bouton "Suivant"
    cursor.execute("""
        SELECT id FROM pages 
        WHERE manga_id = %s AND num_chapitre = %s AND numero_page = %s;
    """, (manga_id, num_chapitre, numero_page + 1))
    a_un_suivant = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    
    return render_template("reader.html", 
                           manga_id=manga_id,
                           num_chapitre=num_chapitre,
                           numero_page=numero_page,
                           image_url=page_actuelle[0],
                           narration=page_actuelle[1],
                           a_un_suivant=a_un_suivant)
