from app.settings import *
from flask import render_template, request, jsonify
from app.connect import database
from app import app

# ~~ Carrega página

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/cadastro")
def cadastro():
    return render_template('cadastro.html')

# @app.route("/")
def pag_usuario():...

# ~~ Não carrega página

@app.route("/cadastrar_usuario", methods=['POST'])
def cadastro_usuario():
    dados = formatData(request.get_json())
    if dados:
        tabela, data, inconsistencia, erro_titulo, erro_texto = dados

        if inconsistencia:
            return jsonify({
                'error': True,
                'title': erro_titulo,
                'text': erro_texto
            })
        
        database.insert(tabela, data)
        return jsonify({
            'error': False,
            'title': 'Usuário cadastrado'
        })

@app.route("/validar_usuario", methods=['POST'])
def verify_usuario():
    validar_usuario(request.get_json())
