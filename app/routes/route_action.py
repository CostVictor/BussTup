from flask_security import login_user, logout_user, login_required, current_user
from app.models import db_flask, user_datastore, database, create_user_flask
from flask import request, jsonify, Response
from app.format import formatData, formatTelefone
from app import app
import bcrypt, time


# ~~ Flask

@app.route("/autenticar_usuario", methods=['POST'])
def autenticar_usuario():
    data = request.get_json()
    user = user_datastore.find_user(primary_key=data['user'])
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.hash_senha):
        login_user(user)
        return jsonify({'error': False, 'redirect': '/pagina-usuario'})
    return jsonify({'error': True})


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
    

@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/checar_linha", methods=['GET'])
@login_required
def checkLine():
    key = current_user.primary_key
    response = {'conf': True}
    if key.isdigit():
        if database.select('Aluno_has_Ponto', where={'where': 'Aluno_matricula = %s', 'value': key}):
            response['conf'] = True
    else:
        if database.select('Linha_has_Motorista', where={'where': 'Motorista_nome = %s', 'value': key}):
            response['conf'] = True
    return jsonify(response)


@app.route("/get_perfil", methods=['GET'])
@login_required
def get_perfil():
    data = {}
    role = current_user.roles[0].name
    user = database.return_user(current_user.primary_key)

    data['nome'] = user.nome
    data['telefone'] = user.telefone
    data['email'] = user.email

    if role == 'aluno':
        data['curso'] = user.curso
        data['turno'] = user.turno

        if not data['email']:
            data['email'] = 'Não definido'
    else:
        data['pix'] = user.pix
        
        if not data['pix']:
            data['pix'] = 'Não definido'

    return jsonify(data)


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


@app.route("/get_linhas", methods=['GET'])
@login_required
def get_linha():
    role = current_user.roles[0].name
    data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}

    linhas = database.select('Linha', data='codigo, nome, particular, cidade, ferias')
    donos = database.select('Linha_has_Motorista', data='Linha_codigo, Motorista_nome', where={'where': 'motorista_dono = %s', 'value': True})

    if linhas and not isinstance(linhas, list):
        linhas = [linhas]

    if donos and not isinstance(donos, list):
        donos = [donos]

    if role == 'aluno':
        linha_aluno = False
        ponto_id = database.select('Aluno_has_Ponto', data='Ponto_id', where={'where': 'Aluno_matricula = %s', 'value': current_user.primary_key})
        if ponto_id:
            if isinstance(ponto_id, tuple):
                ponto_id = ponto_id[0]['Ponto_id']
            else: ponto_id = ponto_id['Ponto_id']

            linha_aluno_codigo = database.select('Ponto', data='Linha_codigo', where={'where': 'id = %s', 'value': ponto_id})['Linha_codigo']
            linha_aluno = database.select('Linha', data='nome', where={'where': 'codigo = %s', 'value': linha_aluno_codigo})['nome']

    if linhas:
        for linha in linhas:
            if linha['cidade'] not in data['cidades']:
                data['cidades'][linha['cidade']] = []

            data['cidades'][linha['cidade']].append(linha)
            for dono in donos:
                if dono['Linha_codigo'] == linha['codigo']:
                    linha['dono'] = dono['Motorista_nome']

                    if role == 'motorista':
                        if dono['Motorista_nome'] == current_user.primary_key:
                            data['minha_linha'].append(linha)
                    else:
                        if linha_aluno and linha['nome'] == linha_aluno:
                            data['minha_linha'].append(linha)
            del linha['codigo']
            del linha['cidade']
    else: data['identify'] = False
    return jsonify(data)


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


@app.route("/get_interfaceLinha", methods=['POST'])
@login_required
def get_interfaceLinha():
    data = request.get_json()

    if data:
        linha = database.select('Linha', where={'where': 'nome = %s', 'value': data['nome_linha']})
        if not linha['particular']:
            del linha['valor_cartela']
            del linha['valor_diaria']
        else:
            linha['valor_cartela'] = f'{linha["valor_cartela"]:.2f}'.replace('.', ',')
            linha['valor_diaria'] = f'{linha["valor_diaria"]:.2f}'.replace('.', ',')
        del linha['codigo']
        return jsonify({'error': False, 'data': linha})
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interfaceMotoristas", methods=['POST'])
@login_required
def get_interfaceMotoristas():
    data = request.get_json()

    if data:
        retorno = {}
        codigo_linha = database.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['nome_linha']})
        codigo_linha = codigo_linha['codigo']
        relacao_motoristas = database.select('Linha_has_Motorista', where={'where': 'Linha_codigo = %s', 'value': codigo_linha})

        if not isinstance(relacao_motoristas, list):
            relacao_motoristas = [relacao_motoristas]

        for dados in relacao_motoristas:
            motorista = database.select('Motorista', where={'where': 'nome = %s', 'value': dados['Motorista_nome']})

            if dados['motorista_dono']:
                retorno['dono'] = [motorista]

                if not motorista['pix']:
                    motorista['pix'] = 'Não definido'

            elif dados['motorista_adm']:
                if 'adm' not in retorno:
                    retorno['adm'] = []

                retorno['adm'].append(motorista)
                del motorista['pix']

            else:
                if 'motoristas' not in retorno:
                    retorno['membro'] = []

                retorno['membro'].append(motorista)
                del motorista['pix']

            del motorista['email']
        
        return jsonify({'error': False, 'data': retorno})
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações dos motoristas.'})


# ~~ SSE

def extract_info(function_extract):
    def generate_events():
        last_sent = time.time()
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - last_sent

            if elapsed_time >= 3:
                yield function_extract()
                last_sent = current_time
    
    return generate_events()


def extract_agenda():...


def extract_rota():...



@app.route("/stream_agenda")
@login_required
def stream_agenda():
    return Response(extract_info(extract_agenda), mimetype='text/event-stream')


@app.route("/stream_rota")
@login_required
def stream_rota():
    return Response(extract_info(extract_agenda), mimetype='text/event-stream')
