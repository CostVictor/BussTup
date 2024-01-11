from flask_security import login_user, logout_user, login_required, current_user
from app.models import db_flask, user_datastore, database, create_user_flask
from flask import request, jsonify
from app.format import formatData, formatTelefone
from app import app
import bcrypt


# ~~ Flask

@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/autenticar_usuario", methods=['POST'])
def autenticar_usuario():
    data = request.get_json()
    user = user_datastore.find_user(primary_key=data['user'])
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.hash_senha):
        login_user(user)
        return jsonify({'error': False, 'redirect': '/pagina-usuario'})
    return jsonify({'error': True})


# ~~ Inserts

@app.route("/cadastrar_usuario", methods=['POST'])
def cadastro_usuario():
    dados = formatData(request.get_json())
    if dados:
        tabela, data, hash_senha, inconsistencia, erro_titulo, erro_texto = dados

        if inconsistencia:
            return jsonify({
                'error': True,
                'title': erro_titulo,
                'text': erro_texto
            })
        
        primary_key = data['matricula'] if tabela == 'aluno' else data['nome']
        create_user_flask(tabela, primary_key, hash_senha)
        database.insert(tabela, data)
        return jsonify({
            'error': False,
            'title': 'Usuário cadastrado'
        })
    

@app.route("/create_linha", methods=['POST'])
@login_required
def create_linha():
    data = request.get_json()['data']

    if data and current_user.roles[0].name == 'motorista':
        if not database.select('Linha', where={'where': 'nome = %s', 'value': data['nome']}):
            data['ferias'] = False
            database.insert('Linha', data)

            codigo_linha = database.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['nome']})
            database.insert('Linha_has_Motorista', data={'Linha_codigo': codigo_linha['codigo'], 'Motorista_nome': current_user.primary_key, 'motorista_dono': True, 'motorista_adm': True})

            return jsonify({'error': False, 'title': 'Linha cadastrada', 'text': 'Sua linha foi cadastrada e está disponível para utilização. Você foi adicionado como usuário dono.'})

        return jsonify({'error': True, 'title': 'Linha existente', 'text': 'Já existe uma linha com o nome especificado.'})

    return jsonify({'error': True, 'title': 'Erro de cadastro', 'text': 'Ocorreu um erro inesperado ao cadastrar a linha.'})


# ~~ Edição de dados

@app.route("/edit_perfil", methods=['POST'])
@login_required
def edit_perfil():
    data = request.get_json()
    if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.hash_senha):
        field = data['field']
        new_value = data['new_value']

        if field == 'telefone':
            new_value = formatTelefone(new_value)
        
        if field == 'senha':
            new_hash_password = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
            current_user.hash_senha = new_hash_password
            db_flask.session.commit()

            return jsonify({'error': False, 'title': 'Edição concluida', 'text': 'Senha alterada com sucesso.'})
        else:
            if new_value:
                user_db = database.return_user(current_user.primary_key)
                user_db.update(field, new_value)

                return jsonify({'error': False, 'title': 'Edição concluida', 'text': ''})
            return jsonify({'error': True, 'title': 'Telefone inválido', 'text': 'O telefone especificado não é válido.'})
    
    return jsonify({'error': True, 'title': 'Senha incorreta', 'text': 'A senha especificada está incorreta.'})
