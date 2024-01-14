from flask import render_template
from flask_security import current_user, login_required
from app import app


@app.route("/")
@app.route("/index")
@app.route("/login")
def index():
    return render_template('auth/login.html')


@app.route("/register")
def cadastro():
    return render_template('auth/register.html')


@app.route("/page_user")
@login_required
def pag_usuario():
    role = current_user.roles[0].name
    turnos = ('Matutino', 'Vespertino', 'Noturno')
    dias_semana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta')
    return render_template('blog/page_user.html', role=role, turnos=turnos, dias_semana=dias_semana)


@app.route("/profile_user")
@login_required
def perfil_usuario():
    role = current_user.roles[0].name
    return render_template('blog/profile_user.html', role=role)
