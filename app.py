from flask import Flask, render_template
from controllers.logic import get_mangas

app = Flask(__name__)

@app.route('/')
def home():
    # Récupère la liste depuis ton contrôleur
    mangas = get_mangas()
    # Envoie les données vers le HTML
    return render_template('index.html', mangas=mangas)

if __name__ == '__main__':
    app.run()
