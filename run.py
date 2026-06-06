from flask import Flask, session, redirect, render_template_string
from app.controllers.main_controller import home_controller, lecteur_controller, login_controller, admin_controller

app = Flask(__name__)
app.secret_key = "manga_cine_secret_key_2026"

# Routes
@app.route('/')
def index(): return home_controller()

@app.route('/manga/<int:m_id>/page/<int:num>')
def lecteur(m_id, num): return lecteur_controller(m_id, num)

@app.route('/login', methods=['GET', 'POST'])
def login(): return login_controller()

@app.route('/admin', methods=['GET', 'POST'])
def admin(): return admin_controller()

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
