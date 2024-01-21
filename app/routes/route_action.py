from flask_security import login_user, logout_user, login_required, current_user
from app.utilities import formatData, check_permission
from app.database import db, user_datastore, create_user
from flask import request, jsonify
from app import app, limiter
import bcrypt


# ~~ Flask

@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/authenticate_user", methods=['POST'])
@limiter.limit('5 per minute')
def autenticar_usuario():
    data = request.get_json()
    user = user_datastore.find_user(primary_key=data['login'])
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.hash_senha):
        login_user(user)
        return jsonify({'error': False, 'redirect': '/page_user'})
    return jsonify({'error': True})


@app.route("/create_message", methods=['POST'])
def enviar_email():...


# ~~ Inserts

@app.route("/register_user", methods=['POST'])
@limiter.limit('5 per minute')
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
        
        create_user()
        return jsonify({'error': False, 'title': 'Usuário cadastrado'})

    

@app.route("/create_line", methods=['POST'])
@login_required
def create_linha():
    data = request.get_json()['data']

    if data and current_user.roles[0].name == 'motorista':
        if not db.select('Linha', where={'where': 'nome = %s', 'value': data['nome']}):
            data['ferias'] = False
            db.insert('Linha', data)

            codigo_linha = db.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['nome']})
            db.insert('Linha_has_Motorista', data={'Linha_codigo': codigo_linha['codigo'], 'Motorista_nome': current_user.primary_key, 'motorista_dono': True, 'motorista_adm': True})

            return jsonify({'error': False, 'title': 'Linha cadastrada', 'text': 'Sua linha foi cadastrada e está disponível para utilização. Você foi adicionado como usuário dono.'})

        return jsonify({'error': True, 'title': 'Linha existente', 'text': 'Já existe uma linha com o nome especificado.'})

    return jsonify({'error': True, 'title': 'Erro de cadastro', 'text': 'Ocorreu um erro inesperado ao cadastrar a linha.'})


@app.route("/create_veicle", methods=['POST'])
@login_required
def create_veicle():
    data = request.get_json()

    if data and current_user.roles[0].name == 'motorista':
        result = check_permission(data)

        if result == 'autorizado':
            data['Linha_codigo'] = data.pop('code_line'); del data['name_line']
            verify_placa = db.select('Onibus', where={'where': 'placa = %s', 'value': data['placa']})

            if not verify_placa:
                if data['Motorista_nome'] != 'Nenhum':
                    verify_motorista = db.select('Onibus', where={'where': 'Motorista_nome = %s AND Linha_codigo = %s', 'value': (data['Motorista_nome'], data['Linha_codigo'])})

                    if verify_motorista:
                        return jsonify({'error': True, 'title': 'Motorista não disponível', 'text': 'O motorista selecionado já possui uma função.'})

                else: del data['Motorista_nome']

                db.insert('Onibus', data)
                return jsonify({'error': False, 'title': 'Veículo adicionado', 'text': 'O veículo foi adicionado e está disponível para utilização.'})

            return jsonify({'error': True, 'title': 'Veículo existente', 'text': 'Já há um veículo cadastrado com essas informações.'})
        
    return jsonify({'error': True})


# ~~ Edição de dados

@app.route("/edit_profile", methods=['PATCH'])
@login_required
def edit_perfil():
    data = request.get_json()
    if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.hash_senha):
        field = data['field']
        new_value = data['new_value']
        
        if field == 'senha':
            new_hash_password = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
            current_user.hash_senha = new_hash_password
            db.session.commit()

            return jsonify({'error': False, 'title': 'Edição concluida', 'text': 'Senha alterada com sucesso.'})
        else:
            if new_value:
                user_db = db.return_user(current_user.primary_key)
                user_db.update(field, new_value)

                return jsonify({'error': False, 'title': 'Edição concluida', 'text': ''})
            return jsonify({'error': True, 'title': 'Telefone inválido', 'text': 'O telefone especificado não é válido.'})
    
    return jsonify({'error': True, 'title': 'Senha incorreta', 'text': 'A senha especificada está incorreta.'})


@app.route("/edit_line", methods=['PATCH'])
@login_required
def edit_linha_valor():
    if current_user.roles[0].name == 'motorista':
        data = request.get_json()
        if data['field'] == 'nome' or data['field'] == 'cidade':
            result = check_permission(data, permission='motorista_dono')
        else: result = check_permission(data)

        if result == 'autorizado':
            if data['field'] == 'nome':
                verify = db.select('Linha', where={'where': 'nome = %s', 'value': data['new_value']})
                if verify:
                    if int(verify['codigo']) == int(data['code_line']):
                        return jsonify({'error': True, 'title': 'Edição inválida', 'text': 'Você deve definir um nome diferente do atual.'})
                    
                    return jsonify({'error': True, 'title': 'Nome existente', 'text': 'Já existe uma linha cadastrada neste nome.'})
                
            db.update('Linha', data['field'], data['new_value'], where={'where': 'codigo = %s', 'value': data['code_line']})
            return jsonify({'error': False, 'title': 'Alteração concluida'})
        
        elif result == 'senha incorreta':
            return jsonify({'error': True, 'title': 'Senha incorreta', 'text': 'A senha especificada está incorreta.'})
        
    return jsonify({'error': True, 'title': 'Erro', 'text': 'Um erro inesperado ocorreu ao tentar editar a informação.'})
