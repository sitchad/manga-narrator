from flask import Flask, send_file, request
from controllers.logic import get_mangas, get_page_data, generate_audio_stream

app = Flask(__name__)
app.secret_key = "manga_cine_secret_key_2026"

@app.route('/')
def home():
    mangas = get_mangas()
    return f"Accueil - {len(mangas)} mangas chargés."

@app.route('/manga/<int:manga_id>/page/<int:num_page>')
def lecteur(manga_id, num_page):
    page = get_page_data(manga_id, num_page)
    if not page: return "Fin du chapitre !"
    return f"Image: {page[0]} <br> Texte: {page[1]}"

@app.route('/audio/<int:manga_id>/<int:num_page>')
def audio(manga_id, num_page):
    page = get_page_data(manga_id, num_page)
    audio_fp = generate_audio_stream(page[1] if page else None)
    return send_file(audio_fp, mimetype="audio/mp3")

if __name__ == '__main__':
    app.run(debug=True)
