from flask import render_template
from flask_security import current_user, login_required
from app.models import database
from app import app

@app.route("/")
@app.route("/index")
@app.route("/login")
def index():
    return render_template('index.html')


@app.route("/cadastro")
def cadastro():
    return render_template('cadastro.html')


@app.route("/usuario")
@login_required
def pag_usuario():
    user = database.return_user(current_user.primary_key)
    return f'Está é a página segura de {user.nome}'
