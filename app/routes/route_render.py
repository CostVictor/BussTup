from flask import render_template, request
from flask_security import current_user, login_required
from app import app, cursos, turnos, cidades, dias_semana
from app.database import Linha, Marcador_Exclusao


@app.route("/")
@app.route("/index")
@app.route("/login")
def index():
    return render_template('auth/login.html')


@app.route("/register")
def cadastro():
    return render_template('auth/register.html', cursos=cursos, turnos=turnos)


@app.route("/page_user")
@login_required
def pag_usuario():
    abas = ['agenda', 'rota', 'linhas', 'chat']
    local = request.args.get('local')
    local = local if local and local in abas else 'agenda'

    role = current_user.roles[0].name
    return render_template('blog/page_user.html', role=role, turnos=turnos, dias_semana=dias_semana, cidades=cidades, local=local)


@app.route("/line/<name_line>")
@login_required
def pag_linha(name_line):
    local_page = request.args.get('local_page')
    linha = Linha.query.filter_by(nome=name_line).first()

    if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
        role = current_user.roles[0].name
        return render_template('blog/line.html', name_line=name_line, role=role, turnos=turnos, local_page=local_page)
    return 'Linha não encontrada.'


@app.route("/profile_user")
@login_required
def perfil_usuario():
    local_page = request.args.get('local_page')
    role = current_user.roles[0].name
    return render_template('blog/profile_user.html', role=role, local_page=local_page)
