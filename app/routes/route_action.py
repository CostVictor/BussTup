from flask_security import login_user, logout_user, login_required, current_user
from app.models import user_datastore, database, create_user_flask
from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta, datetime
from flask import request, jsonify
from app.format import formatData
from app import app, socketio
import bcrypt

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


@app.route("/gerar_token", methods=['GET'])
@login_required
def create_token():
    return jsonify({'token_access': create_access_token(identity=current_user.primary_key, expires_delta=timedelta(days=1))})


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


# ~~ WebSocket

def return_users(token):
    decoded_token = decode_token(token)
    user_db = database.return_user(decoded_token['sub'])
    user_flask = user_datastore.find_user(primary_key=decoded_token['sub'])
    return user_db, user_flask

def return_dates():
    hoje = datetime.now()
    dia_semana = hoje.weekday()
    dias_ate_segunda = (dia_semana + 1) % 7
    if dia_semana == 5 or dia_semana == 6:
        dias_ate_segunda = 7 - dia_semana
        segunda = hoje + timedelta(days=dias_ate_segunda)
    else: segunda = hoje - timedelta(days=dias_ate_segunda)

    datas_semana = []
    for index in range(5):
        data_dia = segunda + timedelta(days=index)
        data_dia = f'"{data_dia.strftime("%Y-%m-%d")}"'
        datas_semana.append(data_dia)
    return datas_semana


@socketio.on('send_line_schedule')
def send_schedule(data):
    token = data.get('token')
    if token:
        user, user_flask = return_users(token)
        if user:
            match user_flask.roles[0]:
                case 'aluno':...
                case 'motorista':...
