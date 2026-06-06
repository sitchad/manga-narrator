from flask import Flask, send_file
from controllers.logic import get_mangas, get_page_data
from gtts import gTTS
import io

app = Flask(__name__)

@app.route('/')
def home():
    mangas = get_mangas()
    return f"Application en ligne. Mangas trouvés : {len(mangas)}"

@app.route('/manga/<int:manga_id>/page/<int:num_page>')
def page(manga_id, num_page):
    data = get_page_data(manga_id, num_page)
    return str(data)

if __name__ == '__main__':
    app.run()
