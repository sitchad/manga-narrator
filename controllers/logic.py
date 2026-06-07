from flask import render_template, abort, request, redirect, jsonify
from models.db import (
    db_get_all_mangas, db_get_manga_by_id, db_insert_manga,
    db_get_chapitres_by_manga, db_get_chapitre_numero, db_insert_chapitre,
    db_get_page, db_check_next_page, db_insert_page,
    db_delete_manga, db_delete_chapitre, db_delete_cases_by_chapitre,
    db_get_max_chapitre_numero
)

# --- CLIENT ---
def liste_tous_les_mangas():
    mangas = db_get_all_mangas()
    return render_template("index.html", mangas=mangas)

def afficher_manga(manga_id):
    manga = db_get_manga_by_id(manga_id)
    if not manga:
        abort(404)
    chapitres = db_get_chapitres_by_manga(manga_id)
    return render_template("manga.html", manga=manga, chapitres=chapitres)

def lire_page_manga(manga_id, chapitre_id, numero_page):
    page_actuelle = db_get_page(chapitre_id, numero_page)
    if not page_actuelle:
        if numero_page == 1:
            return "Ce chapitre ne contient pas encore de cases.", 404
        return render_template("fin_chapitre.html", manga_id=manga_id)

    a_un_suivant = db_check_next_page(chapitre_id, numero_page)
    image_url = page_actuelle[0]
    narration = page_actuelle[1]
    num_chapitre = db_get_chapitre_numero(chapitre_id)
    
    return render_template("reader.html", 
                           manga_id=manga_id, chapitre_id=chapitre_id, num_chapitre=num_chapitre,
                           numero_page=numero_page, image_url=image_url, narration=narration, a_un_suivant=a_un_suivant)

# --- ADMIN ---
def charger_panel_admin():
    mangas = db_get_all_mangas()
    tous_les_chapitres = []
    for m in mangas:
        chaps = db_get_chapitres_by_manga(m[0])
        for c in chaps:
            tous_les_chapitres.append({
                'id': c[0],
                'manga_nom': m[1],
                'numero': c[1],
                'titre': c[2]
            })
    return render_template('admin.html', mangas=mangas, chapitres=tous_les_chapitres)

def api_prochain_chapitre_numero(manga_id):
    max_num = db_get_max_chapitre_numero(manga_id)
    return jsonify({"prochain_numero": max_num + 1})

def ajouter_nouveau_manga():
    nom = request.form.get('nom')
    photo_url = request.form.get('photo_url')
    description = request.form.get('description')
    db_insert_manga(nom, photo_url, description)
    return redirect('/admin')

def ajouter_nouveau_chapitre():
    manga_id = request.form.get('manga_id')
    numero = request.form.get('numero')
    titre = request.form.get('titre')
    couverture_chapitre_url = request.form.get('couverture_chapitre_url')
    db_insert_chapitre(manga_id, numero, titre, couverture_chapitre_url)
    return redirect('/admin')

def ajouter_cases_chapitre():
    chapitre_id = request.form.get('chapitre_id')
    urls_brutes = request.form.get('urls_cases')
    narrations_brutes = request.form.get('narrations_cases')
    
    if not urls_brutes:
        return "Erreur : URLs manquantes", 400
        
    liste_urls = [url.strip() for url in urls_brutes.split(',') if url.strip()]
    liste_narrations = [n.strip() for n in narrations_brutes.split(';')] if narrations_brutes else []
    
    for index, url in enumerate(liste_urls):
        narration = liste_narrations[index] if index < len(liste_narrations) else ""
        db_insert_page(chapitre_id, index + 1, url, narration)
        
    return redirect('/admin')

def supprimer_manga_action(manga_id):
    db_delete_manga(manga_id)
    return redirect('/admin')

def supprimer_chapitre_action(chapitre_id):
    db_delete_chapitre(chapitre_id)
    return redirect('/admin')

def vider_cases_action(chapitre_id):
    db_delete_cases_by_chapitre(chapitre_id)
    return redirect('/admin')
