from flask_security import login_user, logout_user, login_required, roles_required
from flask_jwt_extended import decode_token
from flask import request, jsonify
from app import app, limiter
from app.utilities import *
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


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Assistance ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/help_student/<name_line>", methods=['GET'])
@login_required
@roles_required("aluno")
def assistência_aluno(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  not_dis = Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first()
  user = return_my_user()

  if linha and user and not not_dis:
    retorno = {'error': False, 'finished': False}
    pass_fixed = Passagem.query.filter_by(
      passagem_fixa=True,
      passagem_contraturno=False,
      Aluno_id=user.id
    ).all()

    if not pass_fixed:
      retorno['popup'] = 'new'
      rotas_shift = return_options_route(linha, user)

      if rotas_shift:
        retorno['data'] = rotas_shift
      else:
        return jsonify({'error': True, 'title': 'Rota Não Identificada', 'text': 'Parece que esta linha não possui nenhuma rota com veículo e motorista disponíveis no momento.'})
    
    elif len(pass_fixed) == 1:
      rota = pass_fixed[0].parada.rota
      if rota.linha.codigo == linha.codigo:
        retorno['popup'] = 'blocked'
        retorno['data'] = []

        onibus = rota.onibus
        retorno['data'].append({
          'motorista': onibus.motorista.nome,
          'apelido': onibus.apelido,
          'turno': rota.turno,
          'horario_partida': format_time(rota.horario_partida),
          'horario_retorno': format_time(rota.horario_retorno),
          'quantidade': count_part_route(rota.codigo, formated=False)
        })
      
      else:
        retorno['popup'] = 'change'
        rotas = return_options_route(linha, user)
        if rotas:
          retorno['data'] = rotas
        else:
          return jsonify({'error': True, 'title': 'Rota Não Identificada', 'text': 'Parece que esta linha não possui nenhuma rota com veículo e motorista disponíveis no momento.'})
    
    elif len(pass_fixed) == 2:
      rota = pass_fixed[0].parada.rota
      if rota.linha.codigo == linha.codigo:
        contraturno = Passagem.query.filter_by(
          passagem_fixa=True,
          passagem_contraturno=True,
          Aluno_id=user.id
        ).first()

        if contraturno:
          retorno['finished'] = True
        else:
          shift_query = ['Matutino', 'Vespertino', 'Noturno']
          shift_query.remove(user.turno)

          retorno['popup'] = 'contraturno'
          retorno['data'] = {}

          for index, shift in enumerate(shift_query):
            if shift not in retorno['data']:
              retorno['data'][f'{index} {shift}'] = []
            
            rotas_shift = (
              db.session.query(Rota, Onibus)
              .filter(db.and_(
                db.not_(Onibus.Motorista_id.is_(None)),
                Rota.Onibus_id == Onibus.id,
                Rota.Linha_codigo == linha.codigo,
                Rota.turno == shift
              ))
              .order_by(Rota.horario_partida, Onibus.apelido)
              .all()
            )

            for value in rotas_shift:
              rota_shift, onibus = value
              motorista_nome = onibus.motorista.nome

              dados = {
                'motorista': motorista_nome,
                'apelido': onibus.apelido,
                'turno': rota_shift.turno,
                'horario_partida': format_time(rota_shift.horario_partida),
                'horario_retorno': format_time(rota_shift.horario_retorno),
                'quantidade': count_part_route(rota_shift.codigo, formated=False)
              }
              retorno['data'][f'{index} {shift}'].append(dados)
      
      else:
        retorno['popup'] = 'change'
        rotas = return_options_route(linha, user)
        if rotas:
          retorno['data'] = rotas
        else:
          return jsonify({'error': True, 'title': 'Rota Não Identificada', 'text': 'Parece que esta linha não possui nenhuma rota com veículo e motorista disponíveis no momento.'})

    return jsonify(retorno)
  
  return jsonify({'error': True})


@app.route("/check_register_in/<name_line>/<type>", methods=['GET'])
@login_required
@roles_required("aluno")
def check_register_in(name_line, type):
  user = return_my_user()
  if user and name_line and type:
    retorno = {'error': False, 'change': False, 'new_line': False}
    parada = (
      db.session.query(Parada).join(Passagem)
      .filter(db.and_(
        Parada.tipo == type,
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == True,
        Passagem.passagem_contraturno == False
      ))
      .first()
    )

    if parada:
      linha = parada.ponto.linha.nome
      retorno['change'] = True
      if linha != name_line:
        retorno['new_line'] = True

    return retorno

  return jsonify({'error': True, 'title': 'Relação não identificada', 'text': 'Ocorreu um erro inesperado ao tentar identificar as relações de usuário.'})


@app.route("/check_register_in_contraturno/<name_line>", methods=['GET'])
@login_required
@roles_required("aluno")
def check_register_in_contraturno(name_line):
  user = return_my_user()
  if user and name_line:
    retorno = {'error': False, 'change': False, 'new_line': False}
    parada = (
      db.session.query(Parada).join(Passagem)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == True,
        Passagem.passagem_contraturno == True
      ))
      .first()
    )

    if parada:
      linha = parada.ponto.linha.nome
      retorno['change'] = True
      if linha != name_line:
        retorno['new_line'] = True

    return retorno

  return jsonify({'error': True, 'title': 'Relação não identificada', 'text': 'Ocorreu um erro inesperado ao tentar identificar a relação do usuário.'})


'''~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Recover ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/schedule_recover", methods=['POST'])
def recuperar_conta():
  data = request.get_json()
  if 'recover' in data and 'email' in data:
    user = return_user_email(data['email'])
    recover = 'usuario' if data['recover'] == 'Usuário' else 'senha'

    if user:
      check = AccessToken.query.filter_by(User_id=user['sessao'].id, type='recuperacao').first()
      agendar = True
      if check:
        token = check.token
        try:
          decode = decode_token(token)
          if decode['dado'] != recover:
            db.session.delete(check)
          else:
            agendar = False

        except:
          db.session.delete(check)

      if agendar:
        nome = user['principal'].nome.split(' ')
        nome = ' '.join(nome[:2]) if len(nome) >= 2 else nome[0]

        info = {
          'id': user['sessao'].id,
          'dado': recover,
          'nome': nome
        }
        agendamento = SendEmail(to=data['email'], type='recuperar', data=info)
        try:
          db.session.add(agendamento)
          db.session.commit()
        
        except Exception as e:
          db.session.rollback()
          print (f'Erro ao agendar o email: {str(e)}')
      
    return jsonify({'error': False, 'title': 'Solicitação Concluída', 'text': 'Um e-mail será enviado para você em alguns instantes.'})

  return jsonify({'error': True, 'title': 'Erro de Recuperação', 'text': 'Os dados fornecidos estão incompletos.'})
