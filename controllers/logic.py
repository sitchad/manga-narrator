from flask import render_template, abort, request, redirect
from models.db import get_db_connection

def liste_tous_les_mangas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas ORDER BY id DESC;")
    mangas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", mangas=mangas)

def afficher_manga(manga_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, titre, cover_url, description, note, badge FROM mangas WHERE id = %s;", (manga_id,))
    manga = cursor.fetchone()
    
    if not manga:
        cursor.close()
        conn.close()
        abort(404)

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
    conn = get_db_connection()
    cursor = conn.cursor()
    
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

    cursor.execute("""
        SELECT id FROM pages 
        WHERE manga_id = %s AND num_chapitre = %s AND numero_page = %s;
    """, (manga_id, num_chapitre, numero_page + 1))
    a_un_suivant = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    
    return render_template("reader.html", 
                           manga_id=manga_id, num_chapitre=num_chapitre, numero_page=numero_page,
                           image_url=page_actuelle[0], narration=page_actuelle[1], a_un_suivant=a_un_suivant)

# --- LOGIQUE DE L'ADMINISTRATION ---

def ajouter_nouveau_manga():
    titre = request.form.get('titre')
    cover_url = request.form.get('cover_url')
    description = request.form.get('description')
    badge = request.form.get('badge')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mangas (titre, cover_url, description, note, badge)
        VALUES (%s, %s, %s, 0.0, %s);
    """, (titre, cover_url, description, badge))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

def ajouter_cases_chapitre():
    manga_id = request.form.get('manga_id')
    num_chapitre = request.form.get('num_chapitre')
    urls_brutes = request.form.get('urls_cases')

    if not urls_brutes:
        return "Erreur", 400

    liste_urls = [url.strip() for url in urls_brutes.split(',') if url.strip()]

    conn = get_db_connection()
    cursor = conn.cursor()
    for index, url in enumerate(liste_urls):
        cursor.execute("""
            INSERT INTO pages (manga_id, num_chapitre, numero_page, image_url, texte_narration)
            VALUES (%s, %s, %s, %s, %s);
        """, (manga_id, num_chapitre, index + 1, url, ""))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

# --- LOGIQUE DU VOTE CLIENT ---

def voter_pour_manga():
    manga_id = request.form.get('manga_id')
    note_client = request.form.get('note_valeur')
    ip_client = request.remote_addr

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM votes WHERE manga_id = %s AND ip_utilisateur = %s;", (manga_id, ip_client))
        deja_vote = cursor.fetchone()

        if deja_vote:
            cursor.execute("UPDATE votes SET valeur_note = %s WHERE id = %s;", (note_client, deja_vote[0]))
        else:
            cursor.execute("INSERT INTO votes (manga_id, ip_utilisateur, valeur_note) VALUES (%s, %s, %s);", 
                           (manga_id, ip_client, note_client))

        cursor.execute("SELECT AVG(valeur_note) FROM votes WHERE manga_id = %s;", (manga_id,))
        nouvelle_moyenne = round(cursor.fetchone()[0], 1)

        cursor.execute("UPDATE mangas SET note = %s WHERE id = %s;", (nouenne_moyenne, manga_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(f'/manga/{manga_id}')
