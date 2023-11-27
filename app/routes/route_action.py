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
        return jsonify({'error': False, 'redirect': '/usuario'})
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


@socketio.on('send_schedule')
def send_schedule(data):
    token = data.get('token')
    if token:
        user, user_flask = return_users(token)
        if user:
            match user_flask.roles[0]:
                case 'aluno':
                    aluno_has_ponto = database.select('Aluno_has_Ponto', where=f'Aluno_matricula = "{user_flask.primary_key}"')
                    information = {'ponto_cadastrado': True}
                    if aluno_has_ponto:
                        points = {}
                        for element in aluno_has_ponto:
                            rota_has_ponto = database.select('Rota_has_Ponto', where=f'Ponto_id = {element["Ponto_id"]}')
                            route = database.select('Rota', where=f'codigo = {rota_has_ponto["Rota_codigo"]}')
                            name_line = database.select('Motorista', data='Linha_nome', where=f'nome = "{route["Onibus_Motorista_nome"]}"')['Linha_nome']
                            line = database.select('Linha', data='nome, cidade', where=f'nome = "{name_line}"')

                            if 'dados' not in information and route['tipo'] == 'ida':
                                bus = database.select('Onibus', where=f'placa = "{route["Onibus_placa"]}"')
                                records_bus = database.select('Registro_Diario_Onibus', where=f'Onibus_placa = "{bus["placa"]}" AND {database.format_listDate(return_dates())}')

                                if records_bus:
                                    records_bus = database.format_date(records_bus)
                                    if isinstance(records_bus, list):
                                        for index in records_bus:
                                            del index['Onibus_Motorista_nome']
                                            del index['Onibus_placa']
                                    else:
                                        del records_bus['Onibus_Motorista_nome']
                                        del records_bus['Onibus_placa']

                                route = database.format_time(route)
                                del route['Onibus_placa']; del route['Onibus_Motorista_nome']

                                information['dados'] = {
                                    'linha': line,
                                    'onibus': bus,
                                    'onibus_registros': records_bus,
                                    'rota_ida': route,
                                }

                            point = database.select('Ponto', where=f'id = {element["Ponto_id"]}')
                            point['ordem'] = rota_has_ponto['ordem']
                            point['horario'] = database.format_time(rota_has_ponto['hora_passagem'])
                            points[point['id']] = point
                        
                        information['pontos'] = points
                        records_aluno = database.select('Registro_Diario_Aluno', where=f'Aluno_matricula = "{user_flask.primary_key}" AND {database.format_listDate(return_dates())}')

                        if records_aluno:
                            records_aluno = database.format_date(records_aluno)
                            if isinstance(records_aluno, list):
                                for index in records_aluno:
                                    del index['Aluno_matricula']
                            else: del records_aluno['Aluno_matricula']

                        contraturno = database.select('Contraturnos_Fixos', data='numero_do_dia', where=f'Aluno_matricula = "{user_flask.primary_key}"')
                        information['aluno_registros'] = records_aluno
                        information['contraturnos_fixos'] = contraturno
                    else:
                        information['ponto_cadastrado'] = False

                case 'motorista':...
            socketio.emit('return_schedule', information)


@socketio.on('send_lines')
def send_lines(data):
    token = data.get('token')
    if token:
        user, user_flask = return_users(token)
        if user:
            data = {}
            linhas = database.select('Linha')
            if linhas:
                match user_flask.roles[0]:
                    case 'aluno':
                        data['linha_aluno'] = None
                        point_id = database.select('Aluno_has_Ponto', data='Ponto_id', where=f'Aluno_matricula = "{user.get_PrimaryKey()}"')
                        if point_id:
                            route_code = database.select('Rota_has_Ponto', data='Rota_codigo', where=f'Ponto_id = {point_id}')
                            name_driver = database.select('Rota', data='Onibus_Motorista_nome', where=f'codigo = {route_code}')
                            name_line = database.select('Motorista', data='Linha_nome', where=f'nome = "{name_driver}"')

                            for index, value in enumerate(linhas):
                                if value['nome'] == name_line:
                                    line = value
                                    linhas.remove(index)
                                    break
                            data['linha_aluno'] = line

                    case 'motorista':...

                data['outras_linhas'] = linhas
                socketio.emit('return_lines', data)
