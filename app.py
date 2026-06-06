from flask import Flask, render_template
from controllers.logic import get_mangas

# Cette ligne est OBLIGATOIRE, ne l'efface jamais
app = Flask(__name__)

@app.route('/')
def home():
    try:
        mangas = get_mangas()
        return render_template('index.html', mangas=mangas)
    except Exception as e:
        return f"Erreur critique : {str(e)}"

if __name__ == '__main__':
    app.run()
