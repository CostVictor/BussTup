from flask_security import login_user, logout_user, login_required, current_user
from app.models import user_datastore, database, create_user_flask
from app.format import formatData
from flask import request, jsonify
from app import app, socketio
import bcrypt

# ~~ Flask

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({'redirect': '/'})


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


# ~~ WebSocket

def confirm_user():
    if current_user and current_user.is_authenticated:
        return database.return_user(current_user.primary_key)
    return False


@socketio.on('send_points')
def send_points():
    user = confirm_user()
    if user:
        match current_user.roles[0]:
            case 'aluno':
                if user.Ponto_id:
                    aluno_point = database.select('Ponto', where=f'id = {user.Ponto_id}')
                    route_has_point = database.select('Rota_has_Ponto', where=f'Ponto_id = {aluno_point["id"]}')
                    aluno_route = database.select('Rota', where=f'codigo = {route_has_point["Rota_codigo"]}')
                    bus = database.select('Onibus', where=f'placa = "{aluno_route["Onibus_placa"]}"')
                    driver = database.select('Motorista', where=f'nome = "{aluno_route["Onibus_Motorista_nome"]}"')
                    linha = database.select('Linha', where=f'nome = "{driver["Linha_nome"]}"')
                    

