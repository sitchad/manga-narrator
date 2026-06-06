from flask import Flask, render_template
# ...
@app.route('/')
def home():
    try:
        mangas = get_mangas()
        return render_template('index.html', mangas=mangas)
    except Exception as e:
        return f"Erreur critique : {str(e)}" # Cela affichera l'erreur sur ton site au lieu de 500
