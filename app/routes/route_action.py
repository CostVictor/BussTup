from flask_security import login_user, logout_user, login_required, roles_required
from app import app, limiter
from flask import request, jsonify
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
      passagem_contraturno=False
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
          passagem_contraturno=True
        ).first()

        if contraturno:
          retorno['finished'] = True
        else:
          shift_query = ['Matutino', 'Vespertino', 'Noturno']
          shift_query.remove(user.turno)

          retorno['popup'] = 'contraturno'
          retorno['data'] = {}

          for shift in shift_query:
            if shift not in retorno['data']:
              retorno['data'][shift] = []
            
            rotas_shift = (
              db.session.query(Rota, Onibus)
              .filter(db.and_(
                db.not_(Onibus.Motorista_id.is_(None)),
                Rota.Onibus_id == Onibus.id,
                Rota.Linha_codigo == linha.codigo,
                Rota.turno == shift
              ))
              .order_by(Rota.horario_partida)
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
              retorno['data'][shift].append(dados)
      
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
        Passagem.Parada_codigo == Parada.codigo,
        Passagem.Aluno_id == user.id
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
