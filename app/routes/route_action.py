from flask_security import login_user, logout_user, login_required
from app import app, limiter
from flask import request, jsonify
from app.database import *
import bcrypt


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Session ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.errorhandler(429)
def return_limitacao(e):
    route = request.endpoint
    if route == 'cadastrar_usuario':
        return jsonify({'error': True, 'title': 'Excesso de Cadastro', 'text': 'Identificamos que você realizou várias tentativas de cadastro em um curto período de tempo. Por questões de segurança, bloqueamos temporariamente o seu acesso.'})
    return jsonify({'error': True, 'title': 'Limite de Tentativas Excedido', 'text': 'Parece que você atingiu o limite de tentativas de login. Por questões de segurança, sua conta foi temporariamente bloqueada. Por favor, tente novamente mais tarde.'}), 429


@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/authenticate_user", methods=['POST'])
@limiter.limit('5 per minute')
def autenticar_usuario():
    data = request.get_json()

    if data and 'login' in data and 'password' in data:
        user = user_datastore.find_user(login=data['login'])

        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash):
            if not user.active:
                role = user.roles[0].name
                if role == 'motorista' and user.analysis:
                    return jsonify({'error': True, 'title': 'Conta em Avaliação', 'text': 'A análise da sua conta de motorista está em andamento por nossa equipe. Destacamos que esse procedimento não envolve a visualização de suas informações de login. Esse protocolo é adotado para novos usuários motoristas, visando garantir a autenticidade do usuário e fortalecer a segurança do site. Assim que a análise for concluída, enviaremos um e-mail para notificá-lo sobre a liberação do acesso.'})
                return jsonify({'error': True, 'title': 'Conta Desativada', 'text': 'Esta conta foi desativada por tempo indefinido.'})
            login_user(user)
            return jsonify({'error': False, 'redirect': 'page_user'})
        
    return jsonify({'error': True, 'title': 'Falha de Login', 'text': 'Verifique suas credenciais e tente novamente.'})
