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


@app.route("/pagina-usuario")
@login_required
def pag_usuario():
    role = current_user.roles[0].name
    turnos = ('Matutino', 'Vespertino', 'Noturno')
    dias_semana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta')
    return render_template('pag_usuario.html', role=role, turnos=turnos, dias_semana=dias_semana)


@app.route("/perfil-usuario")
@login_required
def perfil_usuario():
    role = current_user.roles[0].name
    return render_template('perfil_usuario.html', role=role)
