from flask_security import login_required, roles_required, current_user
from flask import request, jsonify
from collections import deque
from datetime import date, time
from app.utilities import *
from app.database import *
from app import app


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Profile ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_profile", methods=['GET'])
@login_required
def get_perfil():
  data = {}
  role = current_user.roles[0].name
  user = return_my_user()

  data['nome'] = user.nome
  data['telefone'] = user.telefone
  data['email'] = user.email

  if role == 'aluno':
    data['curso'] = user.curso
    data['turno'] = user.turno
  else:
    data['pix'] = user.pix
    if not data['pix']:
      data['pix'] = 'Não definido'

  return jsonify(data)


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ GET Page user ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_association", methods=['GET'])
@login_required
def get_association():
  response = {'conf': False}

  if current_user.roles[0].name == 'aluno':
    if (
      Passagem.query.filter_by(Aluno_id=current_user.primary_key)
      .first()
    ):
      response['conf'] = True
  else:
    user = return_my_user()
    if user and user.linhas:
      response['conf'] = True

  return jsonify(response)


@app.route("/get_routes", methods=['GET'])
@login_required
def get_routes():
  retorno = {'error': False, 'data': {}}
  user = return_my_user()

  if user:
    role = current_user.roles[0].name
    retorno['role'] = role
    
    if role == 'motorista':
      minhas_rotas = {}
      rotas = {}
      retorno['data']['minhas_rotas'] = minhas_rotas
      retorno['data']['rotas'] = rotas
      retorno['possui_veiculo'] = False

      if user.onibus:
        retorno['possui_veiculo'] = True

      subquery = (
        db.session.query(Linha.codigo).join(Membro)
        .filter(db.and_(
          Membro.Motorista_id == user.id,
          Linha.codigo == Membro.Linha_codigo
        ))
        .subquery()
      )
      todas_as_rotas = (
        db.session.query(Linha, Rota, Onibus)
        .filter(db.and_(
          Linha.codigo.in_(subquery.select()),
          Rota.Linha_codigo == Linha.codigo,
          Rota.Onibus_id == Onibus.id
        ))
        .order_by(Linha.nome, Rota.horario_partida, Onibus.apelido)
      )

      for linha, rota, onibus in todas_as_rotas:
        motorista = onibus.motorista

        if motorista:
          estado = 'Inativa'
          if rota.em_partida:
            estado = 'Em partida'
          elif rota.em_retorno:
            estado = 'Em retorno'

          info = {
            'line': linha.nome,
            'turno': rota.turno,
            'horario_partida': format_time(rota.horario_partida),
            'horario_retorno': format_time(rota.horario_retorno),
            'quantidade': count_part_route(rota.codigo),
            'apelido': onibus.apelido,
            'motorista': motorista.nome,
            'estado': estado
          }

          if motorista.id == user.id:
            if linha.nome not in minhas_rotas:
              minhas_rotas[linha.nome] = []
            
            if linha.nome not in rotas:
              rotas[linha.nome] = []

            minhas_rotas[linha.nome].append(info)
            rotas[linha.nome].append(info)
          
          else:
            if linha.nome not in rotas:
              rotas[linha.nome] = []

            rotas[linha.nome].append(info)
    
    else:
      minhas_rotas = []
      rotas = []
      diarias = {}
      retorno['data']['minhas_rotas'] = minhas_rotas
      retorno['data']['rotas'] = rotas
      retorno['data']['diarias'] = diarias
      retorno['msg'] = []

      rotas_diarias = (
        db.session.query(Linha, Rota).join(Parada).join(Passagem)
        .filter(db.and_(
          Passagem.passagem_fixa == False,
          Passagem.Aluno_id == user.id,
          Parada.codigo == Passagem.Parada_codigo,
          Rota.codigo == Parada.Rota_codigo,
          Rota.Linha_codigo == Linha.codigo
        ))
        .all()
      )
      rota_fixa = (
        db.session.query(Rota).join(Parada).join(Passagem)
        .filter(db.and_(
          Passagem.passagem_fixa == True,
          Passagem.passagem_contraturno == False,
          Passagem.Aluno_id == user.id,
          Parada.codigo == Passagem.Parada_codigo,
          Rota.codigo == Parada.Rota_codigo
        ))
        .first()
      )
      rota_contraturno = (
        db.session.query(Rota).join(Parada).join(Passagem)
        .filter(db.and_(
          Passagem.passagem_fixa == True,
          Passagem.passagem_contraturno == True,
          Passagem.Aluno_id == user.id,
          Parada.codigo == Passagem.Parada_codigo,
          Rota.codigo == Parada.Rota_codigo
        ))
        .first()
      )
      linha_codigo = None

      for linha, rota in rotas_diarias:
        if linha.nome not in diarias:
          diarias[linha.nome] = []
        
        info = {
          'line': linha.nome,
          'turno': rota.turno,
          'horario_partida': format_time(rota.horario_partida),
          'horario_retorno': format_time(rota.horario_retorno),
          'quantidade': count_part_route(rota.codigo),
          'estado': estado
        }
        veiculo = rota.onibus
        surname = 'Sem veículo'
        motorista = 'Desativada'

        if veiculo:
          surname = veiculo.apelido
          motorista = 'Nenhum'
          if veiculo.motorista:
            motorista = veiculo.motorista.nome
        info['apelido'] = surname
        info['motorista'] = motorista

        diarias[linha.nome].append(info)

      if rota_fixa:
        linha_codigo = rota_fixa.linha.codigo

        estado = 'Inativa'
        if rota_fixa.em_partida:
          estado = 'Em partida'
        elif rota_fixa.em_retorno:
          estado = 'Em retorno'

        info = {
          'line': rota_fixa.linha.nome,
          'turno': rota_fixa.turno,
          'horario_partida': format_time(rota_fixa.horario_partida),
          'horario_retorno': format_time(rota_fixa.horario_retorno),
          'quantidade': count_part_route(rota_fixa.codigo),
          'estado': estado
        }
        veiculo = rota_fixa.onibus
        surname = 'Sem veículo'
        motorista = 'Desativada'

        if veiculo:
          surname = veiculo.apelido
          motorista = 'Nenhum'
          if veiculo.motorista:
            motorista = veiculo.motorista.nome
        info['apelido'] = surname
        info['motorista'] = motorista

        minhas_rotas.append(info)

      else:
        retorno['msg'].append('Você não definiu sua rota fixa.')
      
      if rota_contraturno:
        if not linha_codigo:
          linha_codigo = rota_contraturno.linha.codigo
        
        estado = 'Inativa'
        if rota_contraturno.em_partida:
          estado = 'Em partida'
        elif rota_contraturno.em_retorno:
          estado = 'Em retorno'

        info = {
          'line': rota_contraturno.linha.nome,
          'turno': rota_contraturno.turno,
          'horario_partida': format_time(rota_contraturno.horario_partida),
          'horario_retorno': format_time(rota_contraturno.horario_retorno),
          'quantidade': count_part_route(rota_contraturno.codigo),
          'estado': estado
        }
        veiculo = rota_contraturno.onibus
        surname = 'Sem veículo'
        motorista = 'Desativada'

        if veiculo:
          surname = veiculo.apelido
          motorista = 'Nenhum'
          if veiculo.motorista:
            motorista = veiculo.motorista.nome
        info['apelido'] = surname
        info['motorista'] = motorista

        minhas_rotas.append(info)

      else:
        retorno['msg'].append('Você não definiu sua rota de contraturno.')
      
      if linha_codigo:
        todas_as_rotas = (
          db.session.query(Rota, Onibus)
          .filter(db.and_(
            Rota.Onibus_id == Onibus.id,
            Onibus.Motorista_id.isnot(None),
            Rota.Linha_codigo == linha_codigo
          ))
          .order_by(Rota.horario_partida, Onibus.apelido)
          .all()
        )

        for rota, onibus in todas_as_rotas:
          estado = 'Inativa'
          if rota.em_partida:
            estado = 'Em partida'
          elif rota.em_retorno:
            estado = 'Em retorno'

          rotas.append({
            'line': rota.linha.nome,
            'turno': rota.turno,
            'horario_partida': format_time(rota.horario_partida),
            'horario_retorno': format_time(rota.horario_retorno),
            'quantidade': count_part_route(rota.codigo),
            'apelido': onibus.apelido,
            'motorista': onibus.motorista.nome,
            'estado': estado
          })
      
      else:
        return jsonify({'error': True, 'title': 'Erro de Identificação', 'text': 'Ocorreu um erro inesperado ao identificar a linha.'})

    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações das rotas.'})


@app.route("/get_lines", methods=['GET'])
@login_required
def get_lines():
  role = current_user.roles[0].name
  data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}
  query = Membro.query.filter_by(dono=True).join(Linha).order_by(Linha.nome).all()

  if query:
    user = return_my_user()
    if role == 'aluno':
      passagem = (
        Passagem.query.filter_by(
        Aluno_id=user.id,
        passagem_fixa=True
        )
        .first()
      )
      if passagem:
        data['minha_linha'] = passagem.parada.ponto.linha.nome

    for result in query:
      linha = result.linha
      dict_linha = {'nome': linha.nome, 'ferias': linha.ferias, 'paga': linha.paga}

      if linha.cidade not in data['cidades']:
        data['cidades'][linha.cidade] = []

      data['cidades'][linha.cidade].append(dict_linha)
      dict_linha['dono'] = result.motorista.nome

      if role == 'motorista' and dict_linha['dono'] == user.nome:
        data['minha_linha'].append(dict_linha)

  else: data['identify'] = False
  return jsonify(data)


@app.route("/get_summary_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_summary_route(name_line, surname, shift, hr_par, hr_ret):
  role = current_user.roles[0].name
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relationship = return_relationship(linha.codigo)
    rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, None)

    if relationship and relationship != 'não participante' and rota:
      veiculo = rota.onibus
      capacidade = veiculo.capacidade if veiculo else 'Indefinido'

      data = {}
      retorno = {'error': False, 'role': role, 'capacidade': capacidade, 'data': data}

      estado = 'Inativa'
      if rota.em_partida:
        estado = 'Em partida'
      elif rota.em_retorno:
        estado = 'Em retorno'
      retorno['estado'] = estado

      for tipo in ['partida', 'retorno']:
        registro = Registro_Rota.query.filter_by(
          data=date.today(), tipo=tipo, Rota_codigo=rota.codigo
        ).first()
        data[f'previsao_{tipo}'] = registro.previsao_pessoas
      
      return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da rota. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_summary_line/<name_line>", methods=['GET'])
@login_required
def get_summary_line(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
    retorno = {
      'error': False,
      'paga': linha.paga,
      'data': {
        'local': linha.cidade
      }
    }
    if linha.paga:
      retorno['data']['valor_cartela'] = f'R$ {format_money(linha.valor_cartela)}'
      retorno['data']['valor_diaria'] = f'R$ {format_money(linha.valor_diaria)}'

    contador_motorista = 0
    for membro in linha.membros:
      motorista = membro.motorista
      contador_motorista += 1

      if membro.dono:
        retorno['data']['dono'] = motorista.nome

    retorno['data']['qnt_motorista'] = (
      f'{contador_motorista} {"disponíveis" if contador_motorista != 1 else "disponível"}'
    )
    
    qnt_veiculo = (
      db.session.query(func.count(Onibus.id))
      .filter(Onibus.Linha_codigo == linha.codigo)
      .scalar()
    )
    retorno['data']['qnt_veiculo'] = (
      f'{qnt_veiculo if qnt_veiculo else 0} {"disponíveis" if qnt_veiculo != 1 else "disponível"}'
    )

    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_stops_student", methods=['GET'])
@login_required
@roles_required("aluno")
def get_stops_student():
  user = return_my_user()
  if user:
    data = {'fixa': {'msg': [], 'paradas': deque()}, 'diaria': {'msg': None, 'paradas': []}}
    retorno = {'error': False, 'data': data}
    passagens = (
      db.session.query(Linha, Rota, Parada, Passagem)
      .filter(db.and_(
        Rota.Linha_codigo == Linha.codigo,
        Parada.Rota_codigo == Rota.codigo,
        Passagem.Parada_codigo == Parada.codigo,
        Passagem.Aluno_id == user.id
      ))
      .order_by(
        db.case([(Parada.tipo.like("%partida%"), 1)], else_=0),
        Passagem.data
      )
      .all()
    )

    tipos = ['partida', 'retorno', 'contraturno']
    for linha, rota, parada, passagem in passagens:
      veiculo = rota.onibus
      info = {
        'linha': linha.nome,
        'veiculo': veiculo.apelido if veiculo else 'Nenhum',
        'nome_ponto': parada.ponto.nome,
        'horario': format_time(parada.horario_passagem),
        'tipo': parada.tipo
      }

      if passagem.passagem_fixa:
        if passagem.passagem_contraturno:
          info['data'] = 'fixo - contraturno'
          data['fixa']['paradas'].append(info)
          tipos.remove('contraturno')
        else:
          info['data'] = 'fixo'
          data['fixa']['paradas'].appendleft(info)
          tipos.remove(info['tipo'])
      else:
        info_date = format_data(passagem.data)
        data['diaria']['paradas'].append(info)

        if passagem.migracao_lotado:
          info['data'] = f'{info_date} - migrado devido lotação'
          data['diaria']['msg'] = 'Lotado: Seu motorista alterou o veículo que você usará no dia e trajeto especificado devido a uma lotação identificada em seu veículo habitual naquele dia.'
        
        elif passagem.migracao_manutencao:
          info['data'] = f'{info_date} - migrado devido manutenção'
          data['diaria']['msg'] = 'Veículo em manutenção: Seu motorista alterou o veículo que você usará devido a um defeito encontrado em seu veículo habitual.'

        else: info['data'] = info_date
    
    for tipo in tipos:
      data['fixa']['msg'].append(f'Você não definiu seu ponto de {tipo}.')
    data['fixa']['paradas'] = list(data['fixa']['paradas'])

    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar os dados do aluno. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_schedule_student", methods=['GET'])
@login_required
@roles_required("aluno")
def get_schedule_student():
  user = return_my_user()
  if user:
    data = {}
    retorno = {'error': False, 'data': data}
    dates = return_dates_week()
    code_line = None
    info_times = {
      'partida': False,
      'contraturno': False
    }
    fixas = (
      db.session.query(Parada, Passagem)
      .filter(db.and_(
        Passagem.Parada_codigo == Parada.codigo,
        Passagem.passagem_fixa == True,
        Passagem.Aluno_id == user.id
      ))
      .all()
    )

    for parada, passagem in fixas:
      if code_line is None:
        code_line = parada.rota.linha.codigo

      if passagem.passagem_contraturno:
        if user.turno == 'Matutino':
          info_times['contraturno'] = time(hour=12)
        else:
          info_times['contraturno'] = parada.horario_passagem

      elif parada.tipo == 'partida':
        info_times['partida'] = parada.horario_passagem

    diarias = (
      db.session.query(Rota.turno, Parada.tipo, Passagem.data)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == False,
        Passagem.data.in_(dates),
        Passagem.Parada_codigo == Parada.codigo,
        Parada.Rota_codigo == Rota.codigo
      ))
      .order_by(
        db.case([(Parada.tipo.like("%partida%"), 0)], else_=1)
      )
      .all()
    )
    feriados = (
      db.session.query(Registro_Linha.data)
      .filter(db.and_(
        Registro_Linha.data.in_(dates),
        Registro_Linha.Linha_codigo == code_line,
        Registro_Linha.feriado == True
      ))
      .all()
    ) if code_line is not None else []

    registros = (
      db.session.query(Registro_Aluno)
      .filter(db.and_(
        Registro_Aluno.Aluno_id == user.id,
        Registro_Aluno.data.in_(dates)
      ))
      .order_by(Registro_Aluno.data)
      .all()
    )

    contraturnos_fixos = (
      Contraturno_Fixo.query.filter_by(Aluno_id=user.id)
      .order_by(Contraturno_Fixo.dia_fixo).all()
    )
    contraturnos_fixos = [
      return_day_week(int(record.dia_fixo))[:3]
      for record in contraturnos_fixos
    ]

    if contraturnos_fixos:
      if len(contraturnos_fixos) == 5:
        contraturnos_fixos = 'Todos os dias'
      elif len(contraturnos_fixos) == 2:
        contraturnos_fixos = ' e '.join(contraturnos_fixos)
      elif len(contraturnos_fixos) >= 3:
        ultimo = contraturnos_fixos.pop()
        contraturnos_fixos = ', '.join(contraturnos_fixos) + f' e {ultimo}'
      else: contraturnos_fixos = contraturnos_fixos[0]
    else: contraturnos_fixos = 'Nenhum'
    retorno['contraturno_fixo'] = contraturnos_fixos

    for registro in registros:
      value_partida = check_valid_datetime(
        registro.data, info_times['partida']
      ) if info_times['partida'] else True

      value_contraturno = check_valid_datetime(
        registro.data, info_times['contraturno']
      ) if info_times['contraturno'] else True

      feriado = [True for feriado in feriados if registro.data in feriado]
      info = {
        'data': format_data(registro.data),
        'faltara': return_str_bool(registro.faltara),
        'contraturno': return_str_bool(registro.contraturno) if not registro.faltara else 'Não',
        'valida': check_valid_datetime(registro.data) if not feriado else False,
        'feriado': True if feriado else False,
        'content_contraturno': value_contraturno,
        'content_faltara': value_partida,
        'diarias': []
      }

      check_diarias = [diaria for diaria in diarias if registro.data in diaria]
      for turno, tipo, _ in check_diarias:
        if turno == user.turno:
          info['diarias'].append(tipo.capitalize())
          if tipo == 'partida':
            info['faltara'] = 'Sim'
          info['contraturno'] = 'Não'

      data[return_day_week(registro.data.weekday())] = info
    
    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar os dados do aluno. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_crowded", methods=['GET'])
@login_required
@roles_required("motorista")
def get_crowded():
  user = return_my_user()
  if user:
    data = {}
    retorno = {'error': False, 'data': data}
    subquery = (
      db.session.query(Linha.codigo).join(Membro)
      .filter(db.and_(
        Membro.Motorista_id == user.id,
        Linha.codigo == Membro.Linha_codigo
      ))
      .subquery()
    )
    todas_as_rotas = (
      db.session.query(Linha, Rota, Registro_Rota, Onibus)
      .filter(db.and_(
        Linha.codigo.in_(subquery.select()),
        Rota.Linha_codigo == Linha.codigo,
        Registro_Rota.Rota_codigo == Rota.codigo,
        Onibus.id == Rota.Onibus_id,

        Onibus.Motorista_id.isnot(None),
        Registro_Rota.previsao_pessoas > Onibus.capacidade
      ))
      .order_by(Registro_Rota.data, Linha.nome, Rota.horario_partida)
      .all()
    )

    for line, route, record, onibus in todas_as_rotas:
      if line.nome not in data:
        data[line.nome] = []
      
      info = {
        'turno': route.turno,
        'horario_partida': format_time(route.horario_partida),
        'horario_retorno': format_time(route.horario_retorno),
        'motorista': onibus.motorista.nome,
        'veiculo': onibus.apelido,
        'capacidade': onibus.capacidade,
        'previsao': record.previsao_pessoas
      }
      data[line.nome].append(info)

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar os dados de previsão. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_forecast_route", methods=['GET'])
@login_required
def get_forecast():
  user = return_my_user()
  if user:...


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~ GET Interface Line ~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_interface-line/<name_line>", methods=['GET'])
@login_required
def get_interface_line(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    retorno = {'error': False, 'role': current_user.roles[0].name, 'relacao': return_relationship(linha.codigo)}
    data = return_dict(linha, not_includes=['codigo', 'nome'])

    data['valor_cartela'] = format_money(linha.valor_cartela)
    data['valor_diaria'] = format_money(linha.valor_diaria)
    retorno['data'] = data

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver/<name_line>", methods=['GET'])
@login_required
def get_interface_driver(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relacoes = Membro.query.filter_by(Linha_codigo=linha.codigo).all()
    motoristas = {}
    retorno = {
      'error': False,
      'role': current_user.roles[0].name,
      'relacao': return_relationship(linha.codigo),
      'data': motoristas
    }

    for relacao in relacoes:
      motorista = relacao.motorista
      dict_motorista = return_dict(motorista, not_includes=['id', 'email', 'pix'])

      if relacao.dono:
        if 'dono' not in motoristas:
          motoristas['dono'] = []

        dict_dono = return_dict(motorista, not_includes=['id', 'email'])
        motoristas['dono'].append(dict_dono)

        if not motorista.pix:
          dict_dono['pix'] = 'Não definido'

      elif relacao.adm:
        if 'adm' not in motoristas:
          motoristas['adm'] = []
        motoristas['adm'].append(dict_motorista)

      else:
        if 'membro' not in motoristas:
          motoristas['membro'] = []
        motoristas['membro'].append(dict_motorista)

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-vehicle/<name_line>", methods=['GET'])
@login_required
def get_interface_vehicle(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  user = return_my_user()
  if linha and user:
    role = current_user.roles[0].name
    retorno = {
      'error': False,
      'role': role,
      'relacao': return_relationship(linha.codigo),
      'data': {'com_condutor': [], 'sem_condutor': []}
    }

    if role == 'motorista':
      retorno['meu_nome'] = user.nome

    vehicles = Onibus.query.filter_by(Linha_codigo=linha.codigo).order_by(Onibus.apelido).all()
    for vehicle in vehicles:
      info = {
        'surname': vehicle.apelido,
        'capacidade': vehicle.capacidade
      }

      if vehicle.motorista:
        info['nome'] = vehicle.motorista.nome
        info['motorista'] = info['nome']
        retorno['data']['com_condutor'].append(info)
      else:
        info['nome'] = 'Nenhum'
        info['motorista'] = info['nome']
        retorno['data']['sem_condutor'].append(info)

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-points/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_interface_points(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
    keys = db.session.query(Ponto.id).filter_by(Linha_codigo=linha.codigo).subquery()
    not_include = (
      db.session.query(Marcador_Exclusao.key_item)
      .filter(db.and_(
        Marcador_Exclusao.tabela == 'Ponto',
        Marcador_Exclusao.key_item.in_(keys.select())
      ))
      .subquery()
    )
    pontos = Ponto.query.filter(
      Ponto.Linha_codigo == linha.codigo,
      db.not_(Ponto.id.in_(not_include.select()))
    ).all()
    
    data = [ponto.nome for ponto in pontos]
    retorno['quantidade'] = count_list(data, 'cadastrado')
    retorno['data'] = data
    return retorno

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-routes/<name_line>", methods=['GET'])
@login_required
def get_interface_route(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    keys = db.session.query(Rota.codigo).filter_by(Linha_codigo=linha.codigo).subquery()
    not_include = (
      db.session.query(Marcador_Exclusao.key_item)
      .filter(db.and_(
        Marcador_Exclusao.tabela == 'Rota',
        Marcador_Exclusao.key_item.in_(keys.select())
      ))
      .subquery()
    )
    rotas = (
      db.session.query(Rota).outerjoin(Onibus)
      .filter(db.and_(
        Rota.Linha_codigo == linha.codigo,
        db.not_(Rota.codigo.in_(not_include.select()))
      ))
      .order_by(Rota.horario_partida, Onibus.apelido)
      .all()
    )

    retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
    retorno['ativas'] = []; retorno['desativas'] = []
    retorno['role'] = current_user.roles[0].name
    code_routes = []

    for rota in rotas:
      code_routes.append(rota.codigo)
      info = {
        'turno': rota.turno,
        'horario_partida': format_time(rota.horario_partida),
        'horario_retorno': format_time(rota.horario_retorno),
        'quantidade': count_part_route(rota.codigo),
      }

      veiculo = rota.onibus
      surname = 'Sem veículo'
      motorista = 'Desativada'

      if veiculo:
        surname = veiculo.apelido
        motorista = 'Nenhum'
        if veiculo.motorista:
          motorista = veiculo.motorista.nome
        retorno['ativas'].append(info)
      else: retorno['desativas'].append(info)

      info['apelido'] = surname
      info['motorista'] = motorista
    retorno['quantidade'] = count_list([retorno['ativas'], retorno['desativas']], 'cadastrada', list_unique=False)

    if retorno['role'] == 'aluno':
      del retorno['quantidade']
      del retorno['desativas']
      retorno['diarias'] = []
      user = return_my_user()

      minhas_diarias = (
        db.session.query(Parada).join(Passagem)
        .filter(db.and_(
          Passagem.Aluno_id == user.id,
          Passagem.passagem_fixa == False,
          Passagem.Parada_codigo == Parada.codigo,
          Parada.Rota_codigo.in_(code_routes)
        ))
        .all()
      )

      for parada in minhas_diarias:
        rota = parada.rota
        info = {
          'turno': rota.turno,
          'horario_partida': format_time(rota.horario_partida),
          'horario_retorno': format_time(rota.horario_retorno),
          'quantidade': count_part_route(rota.codigo),
        }

        veiculo = rota.onibus
        surname = 'Sem veículo'
        motorista = 'Desativada'

        if veiculo:
          surname = veiculo.apelido
          motorista = 'Nenhum'
          if veiculo.motorista:
            motorista = veiculo.motorista.nome
        info['apelido'] = surname
        info['motorista'] = motorista

        retorno['diarias'].append(info)

      if retorno['relacao'] == 'participante':
        retorno['minhas_rotas'] = {'turno': [], 'contraturno': []}
        retorno['mensagens'] = []

        minhas_paradas = (
          db.session.query(Parada).join(Passagem)
          .filter(db.and_(
            Passagem.Aluno_id == user.id,
            Passagem.passagem_fixa == True,
            Passagem.Parada_codigo == Parada.codigo,
          ))
          .all()
        )
        
        list_posibility = ['partida', 'retorno']
        for parada in minhas_paradas:
          rota = parada.rota
          info = {
            'turno': rota.turno,
            'horario_partida': format_time(rota.horario_partida),
            'horario_retorno': format_time(rota.horario_retorno),
            'quantidade': count_part_route(rota.codigo),
          }

          veiculo = rota.onibus
          surname = 'Sem veículo'
          motorista = 'Desativada'

          if veiculo:
            surname = veiculo.apelido
            motorista = 'Nenhum'
            if veiculo.motorista:
              motorista = veiculo.motorista.nome
          info['apelido'] = surname
          info['motorista'] = motorista

          if rota.turno == user.turno:
            list_posibility.remove(parada.tipo)
            if not retorno['minhas_rotas']['turno']:
              retorno['minhas_rotas']['turno'].append(info)
          else: retorno['minhas_rotas']['contraturno'].append(info)
        
        if len(list_posibility) == 1:
          retorno['mensagens'].append(f'Aviso: Você não definiu seu ponto fixo de {list_posibility[0].capitalize()}.')

        elif len(list_posibility) == 2:
          retorno['mensagens'].append(f'Aviso: Você não definiu sua rota fixa.')
        
        if not retorno['minhas_rotas']['contraturno']:
          retorno['mensagens'].append('Aviso: Você não definiu sua rota de contraturno.')

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Options ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_interface-option_driver/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_driver(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relacao = return_relationship(linha.codigo)
    if relacao:
      if relacao == 'membro':
        if not Onibus.query.filter_by(Motorista_id=current_user.primary_key, Linha_codigo=linha.codigo).first():
          user = return_my_user()
          return jsonify({'error': False, 'data': user.nome})
        return jsonify({'error': False, 'data': None})

      not_includes = db.session.query(Onibus.Motorista_id).filter(
        db.and_(Onibus.Linha_codigo == linha.codigo, Onibus.Motorista_id.isnot(None))
      ).subquery()

      query = db.session.query(Membro).filter(
        db.and_(
          Membro.Linha_codigo == linha.codigo,
          db.not_(Membro.Motorista_id.in_(not_includes.select()))
        )
      ).all()
      retorno = [result.motorista.nome for result in query]

      return jsonify({'error': False, 'data': retorno})

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_vehicle/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_vehicle(name_line):
  surname_ignore = request.args.get('surname_ignore')

  if surname_ignore == 'Não definido':
    surname_ignore = None

  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relacao = return_relationship(linha.codigo)
    if relacao and relacao != 'membro':
      retorno = {'error': False, 'data': deque()}

      for onibus in linha.onibus:
        if surname_ignore != onibus.apelido:
          motorista = onibus.motorista
          if motorista:
            retorno['data'].appendleft(f"{onibus.apelido} > {motorista.nome}")
          else: retorno['data'].append(f"{onibus.apelido} > Nenhum")

      retorno['data'] = list(retorno['data'])
      return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_point/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>/<type>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_point(name_line, surname, shift, hr_par, hr_ret, type):
  pos = request.args.get('pos')

  if name_line and surname and shift and hr_par and hr_ret and type:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      relationship = return_relationship(linha.codigo)
      if relationship and relationship != 'membro':
        rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)
        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

          keys = db.session.query(Ponto.id).filter_by(Linha_codigo=linha.codigo).subquery()
          not_includes_1 = (
            db.session.query(Marcador_Exclusao.key_item)
            .filter(db.and_(
              Marcador_Exclusao.tabela == 'Ponto',
              Marcador_Exclusao.key_item.in_(keys.select())
            ))
            .subquery()
          )

          not_includes_2 = (
            db.session.query(Ponto.id).join(Parada)
            .filter(db.and_(
              Parada.Ponto_id.in_(keys.select()),
              Parada.Rota_codigo == rota.codigo,
              Parada.tipo == type
            ))
            .subquery()
          )

          pontos = (
            db.session.query(Ponto.nome)
            .filter(db.and_(
              Ponto.Linha_codigo == linha.codigo,
              db.not_(db.or_(
                Ponto.id.in_(not_includes_1.select()),
                Ponto.id.in_(not_includes_2.select())
              ))
            ))
            .order_by(Ponto.nome)
            .all()
          )

          return jsonify({'error': False, 'data': [ponto.nome for ponto in pontos]})

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_route_vehicle/<name_line>/<surname>", methods=['GET'])
@login_required
def get_options_route_vehicle(name_line, surname):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    rotas = (
      db.session.query(Rota).join(Onibus)
      .filter(db.and_(
        Onibus.apelido == surname,
        Rota.Onibus_id == Onibus.id,
        Rota.Linha_codigo == linha.codigo
      ))
      .order_by(Rota.horario_partida)
      .all()
    )

    retorno = {'error': False, 'data': []}
    for rota in rotas:
      veiculo = rota.onibus
      surname = 'Sem veículo'
      motorista = 'Desativada'

      if veiculo:
        surname = veiculo.apelido
        motorista = 'Nenhum'
        if veiculo.motorista:
          motorista = veiculo.motorista.nome

      dados = {
        'motorista': motorista,
        'apelido': surname,
        'turno': rota.turno,
        'horario_partida': format_time(rota.horario_partida),
        'horario_retorno': format_time(rota.horario_retorno),
        'quantidade': count_part_route(rota.codigo, formated=False)
      }
      retorno['data'].append(dados)

    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações do veículo.'})


@app.route("/get_interface-option_point_contraturno/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
@roles_required("aluno")
def get_interface_option_point_all(name_line, surname, shift, hr_par, hr_ret):
  pos = request.args.get('pos')

  if name_line and surname and shift and hr_par and hr_ret:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)
      if rota is not None:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

        user = return_my_user()
        if user.turno != 'Noturno':
          tipo = 'retorno' if user.turno == 'Matutino' else 'partida'
          values = (
            db.session.query(Parada, Ponto)
            .filter(db.and_(
              Parada.Rota_codigo == rota.codigo,
              Parada.Ponto_id == Ponto.id,
              Parada.tipo == tipo
            ))
            .order_by(Parada.ordem)
            .all()
          )
        else:
          values = (
            db.session.query(Parada, Ponto)
            .filter(db.and_(
              Parada.Rota_codigo == rota.codigo,
              Parada.Ponto_id == Ponto.id,
            ))
            .order_by(Parada.ordem)
            .all()
          )

        retorno = {'error': False, 'data': {}}
        for value in values:
          parada, ponto = value
          if parada.tipo not in retorno['data']:
            retorno['data'][parada.tipo] = []

          info = {
            'number': parada.ordem,
            'nome': ponto.nome,
            'horario': format_time(parada.horario_passagem)
          }
          retorno['data'][parada.tipo].append(info)
        
        return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-students/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_students(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
    data = {'Matutino': {'alunos': []}, 'Vespertino': {'alunos': []}, 'Noturno': {'alunos': []}}
    retorno['data'] = data

    subquery = (
      db.session.query(Parada.codigo).join(Rota)
      .filter(db.and_(
        Rota.Linha_codigo == linha.codigo,
        Parada.Rota_codigo == Rota.codigo
      ))
      .subquery()
    )
    alunos = (
      db.session.query(Aluno).join(Passagem)
      .filter(db.and_(
        Passagem.Parada_codigo.in_(subquery.select()),
        Passagem.passagem_fixa == True,
        Passagem.Aluno_id == Aluno.id
      ))
      .order_by(Aluno.nome)
      .group_by(Aluno.id)
      .all()
    )

    for aluno in alunos:
      data[aluno.turno]['alunos'].append(aluno.nome)
    
    qnt_mat = len(data['Matutino']['alunos'])
    qnt_ves = len(data['Vespertino']['alunos'])
    qnt_not = len(data['Noturno']['alunos'])
    qnt_total = qnt_mat + qnt_ves + qnt_not

    retorno['quantidade'] = f'{qnt_total} {"cadastrado" if qnt_total == 1 else "cadastrados"}'
    data['Matutino']['quantidade'] = f'{qnt_mat} {"cadastrado" if qnt_mat == 1 else "cadastrados"}'
    data['Vespertino']['quantidade'] = f'{qnt_ves} {"cadastrado" if qnt_ves == 1 else "cadastrados"}'
    data['Noturno']['quantidade'] = f'{qnt_not} {"cadastrado" if qnt_not == 1 else "cadastrados"}'

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ GET Config ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_point/<name_line>/<name_point>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_point(name_line, name_point):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relationship = return_relationship(linha.codigo)
    if relationship:
      ponto = Ponto.query.filter_by(nome=name_point, Linha_codigo=linha.codigo).first()
      if ponto:
        retorno = {'error': False, 'relacao': relationship, 'turnos': {}}
        dict_ponto = return_dict(ponto, not_includes=['id', 'Linha_codigo'])
        retorno['info'] = dict_ponto
        retorno['utilizacao'] = {'rotas': []}
        retorno['turnos']['Matutino'] = {'ids_turno': [], 'ids_contraturno': [], 'alunos': [], 'contraturno': []}
        retorno['turnos']['Vespertino'] = {'ids_turno': [], 'ids_contraturno': [], 'alunos': [], 'contraturno': []}
        retorno['turnos']['Noturno'] = {'ids_turno': [], 'ids_contraturno': [], 'alunos': [], 'contraturno': []}

        if not dict_ponto['linkGPS']:
          dict_ponto['linkGPS'] = 'Não definido'
        
        rotas = (
          db.session.query(Rota).join(Parada).outerjoin(Onibus)
          .filter(db.and_(
            Parada.Rota_codigo == Rota.codigo,
            Parada.Ponto_id == ponto.id,
            Parada.tipo == 'partida'
          ))
          .order_by(Rota.horario_partida, Onibus.apelido)
          .all()
        )

        for rota in rotas:
          veiculo = rota.onibus
          surname = 'Sem veículo'
          motorista = 'Desativada'

          if veiculo:
            surname = veiculo.apelido
            motorista = 'Nenhum'
            if veiculo.motorista:
              motorista = veiculo.motorista.nome

          dados = {
            'motorista': motorista,
            'apelido': surname,
            'turno': rota.turno,
            'horario_partida': format_time(rota.horario_partida),
            'horario_retorno': format_time(rota.horario_retorno),
            'quantidade': count_part_route(rota.codigo, formated=False)
          }
          retorno['utilizacao']['rotas'].append(dados)
        retorno['utilizacao']['quantidade'] = count_list(retorno['utilizacao']['rotas'], 'rota')

        paradas = db.session.query(Parada.codigo).filter_by(Ponto_id=ponto.id).subquery()
        values = (
          db.session.query(Passagem, Aluno)
          .filter(db.and_(
            Passagem.passagem_fixa == True,
            Passagem.Parada_codigo.in_(paradas.select()),
            Passagem.Aluno_id == Aluno.id
          ))
          .order_by(Aluno.nome)
          .all()
        )

        for value in values:
          passagem, aluno = value
          if passagem.passagem_contraturno:
            if aluno.id not in retorno['turnos'][aluno.turno]['ids_contraturno']:
              retorno['turnos'][aluno.turno]['contraturno'].append(aluno.nome)
              retorno['turnos'][aluno.turno]['ids_contraturno'].append(aluno.id)
          else:
            if aluno.id not in retorno['turnos'][aluno.turno]['ids_turno']:
              retorno['turnos'][aluno.turno]['alunos'].append(aluno.nome)
              retorno['turnos'][aluno.turno]['ids_turno'].append(aluno.id)

        for turno in retorno['turnos']:
          local = retorno['turnos'][turno]
          local['quantidade'] = count_list([local['alunos'], local['contraturno']], 'cadastro', list_unique=False)
          del local['ids_turno']; del local['ids_contraturno']

        return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações do ponto.'})


@app.route("/get_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_route(name_line, surname, shift, hr_par, hr_ret):
  pos = request.args.get('pos')

  if name_line and shift and hr_par and hr_ret:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      relationship = return_relationship(linha.codigo)
      role = current_user.roles[0].name
      retorno = {'error': False, 'role': role, 'relacao': relationship}
      retorno['data'] = {'partida': {'paradas': []}, 'retorno': {'paradas': []}}
      retorno['msg_desativada'] = False

      user = return_my_user()
      rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)

      if rota is not None and user:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

        veiculo = rota.onibus
        motorista = 'Nenhum'
        surname = 'Não definido'
        if veiculo:
          surname = veiculo.apelido
          if veiculo.motorista:
            motorista = veiculo.motorista.nome
        else: retorno['msg_desativada'] = True

        retorno['info'] = {
          'motorista': motorista,
          'onibus': surname,
          'turno_rota': rota.turno,
          'horario_partida': format_time(rota.horario_partida),
          'horario_retorno': format_time(rota.horario_retorno)
        }

        if role == 'aluno':
          retorno['meu_turno'] = user.turno
          retorno['msg_cadastrar'] = False
          retorno['msg_contraturno'] = False
          retorno['btn_contraturno'] = False
          retorno['msg_incompleta'] = False

          if user.turno == rota.turno:
            retorno['meus_pontos'] = {}

            values = (
              db.session.query(Parada).join(Passagem)
              .filter(db.and_(
                Passagem.Parada_codigo == Parada.codigo,
                Parada.Rota_codigo == rota.codigo,
                Passagem.Aluno_id == current_user.primary_key,
                Passagem.passagem_contraturno == False,
                Passagem.passagem_fixa == True
              ))
              .all()
            )

            if values:
              for value in values:
                ponto = value.ponto
                retorno['meus_pontos'][value.tipo] = ponto.nome
              
              if retorno['meus_pontos']:
                if 'partida' not in retorno['meus_pontos']:
                  retorno['msg_incompleta'] = True
                  retorno['incompleta'] = 'Partida'
                
                elif 'retorno' not in retorno['meus_pontos']:
                  retorno['msg_incompleta'] = True
                  retorno['incompleta'] = 'Retorno'

            else:
              check_cadastro = (
                Passagem.query.filter_by(
                  Aluno_id=user.id,
                  passagem_fixa=True,
                  passagem_contraturno=False
                )
                .first()
              )

              if check_cadastro:
                linha_codigo = check_cadastro.parada.rota.linha.codigo
                if linha_codigo != linha.codigo:
                  retorno['msg_cadastrar'] = True
              else: retorno['msg_cadastrar'] = True
          else:
            retorno['meu_contraturno'] = None

            parada_contraturno = (
              db.session.query(Parada).join(Passagem)
              .filter(db.and_(
                Passagem.Parada_codigo == Parada.codigo,
                Passagem.Aluno_id == current_user.primary_key,
                Passagem.passagem_contraturno == True,
                Passagem.passagem_fixa == True
              ))
              .first()
            )

            if parada_contraturno:
              rota_contraturno = parada_contraturno.rota
              if rota_contraturno.linha.codigo == linha.codigo:
                if rota_contraturno.codigo == rota.codigo:
                  retorno['meu_contraturno'] = f'{parada_contraturno.tipo.capitalize()} ~> {parada_contraturno.ponto.nome}'
                else:
                  retorno['btn_contraturno'] = True
              else:
                retorno['msg_contraturno'] = True
                retorno['btn_contraturno'] = True
            else:
              retorno['msg_contraturno'] = True
              retorno['btn_contraturno'] = True

        for tipo in ['partida', 'retorno']:
          values = db.session.query(Parada, Ponto).filter(
            db.and_(
              Parada.Rota_codigo == rota.codigo,
              Parada.Ponto_id == Ponto.id,
              Parada.tipo == tipo
            )
          ).order_by(Parada.ordem).all()

          for value in values:
            info = {
              'number': value[0].ordem,
              'nome': value[1].nome,
              'horario': format_time(value[0].horario_passagem)
            }
            retorno['data'][tipo]['paradas'].append(info)
          retorno['data'][tipo]['quantidade'] = count_list(values, 'definido')

        return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações da rota.'})


@app.route("/get_relationship-point/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>/<type>/<name_point>", methods=['GET'])
@login_required
def get_relationship(name_line, surname, shift, hr_par, hr_ret, type, name_point):
  pos = request.args.get('pos')

  if name_line and name_point and surname and type and shift and hr_par and hr_ret:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      relationship = return_relationship(linha.codigo)
      role = current_user.roles[0].name
      retorno = {'error': False, 'role': role, 'relacao': relationship, 'contraturno': False}

      rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)
      if rota is not None:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
        
        parada, ponto = (
          db.session.query(Parada, Ponto)
          .filter(db.and_(
            Ponto.nome == name_point,
            Parada.Ponto_id == Ponto.id,
            Parada.tipo == type,
            Parada.Rota_codigo == rota.codigo,
          ))
          .first()
        )

        if parada and ponto:
          data = {
            'tipo': type.capitalize(),
            'nome': ponto.nome,
            'horario': format_time(parada.horario_passagem),
            'linkGPS': ponto.linkGPS if ponto.linkGPS else 'Não definido'
          }
          retorno['data'] = data

          if role == 'motorista':
            alunos = {'turno': {'alunos': []}, 'contraturno': {'alunos': []}}
            passagens = (
              db.session.query(Passagem, Aluno)
              .filter(db.and_(
                Passagem.Parada_codigo == parada.codigo,
                Passagem.Aluno_id == Aluno.id,
                Passagem.passagem_fixa == True,
              ))
              .order_by(Aluno.nome)
              .all()
            )

            for value in passagens:
              passagem, aluno = value
              if passagem.passagem_contraturno:
                alunos['contraturno']['alunos'].append(aluno.nome)
              else: alunos['turno']['alunos'].append(aluno.nome)

            alunos['turno']['quantidade'] = count_list(alunos['turno']['alunos'], 'cadastrado')
            alunos['contraturno']['quantidade'] = count_list(alunos['contraturno']['alunos'], 'cadastrado')
            retorno['cadastrados'] = alunos
          
          else:
            user = return_my_user()
            if user.turno == rota.turno:
              retorno['cadastrado'] = False
              if Passagem.query.filter_by(
                Parada_codigo=parada.codigo,
                passagem_contraturno=False,
                passagem_fixa=True,
                Aluno_id=user.id
              ).first():
                retorno['cadastrado'] = True
            else:
              retorno['contraturno'] = True
          
          return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações da rota.'})


@app.route("/get_aparence/<name_line>/<surname_vehicle>", methods=['GET'])
@login_required
def get_aparence(name_line, surname_vehicle):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    vehicle = Onibus.query.filter_by(Linha_codigo=linha.codigo, apelido=surname_vehicle).first()
    if vehicle:
      aparence = vehicle.aparencia
      role = current_user.roles[0].name
      relationship = return_relationship(linha.codigo)

      retorno = {
        'error': False,
        'role': role,
        'relacao': relationship,
        'data': {
          'color': aparence.cor,
          'model': aparence.modelo,
          'description': aparence.descricao
        }
      }
      return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações do veículo.'})


@app.route("/get_student/<name_line>/<shift>/<name_student>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_stundet(name_line, shift, name_student):
  name_point = request.args.get('name_point')
  contraturno = request.args.get('contraturno')
  pos = request.args.get('pos')

  linha = Linha.query.filter_by(nome=name_line).first()
  if linha and return_relationship(linha.codigo):
    retorno = {'error': False}

    if name_point:
      ponto = Ponto.query.filter_by(Linha_codigo=linha.codigo, nome=name_point).first()
      if ponto:
        aluno = (
          db.session.query(Aluno).join(Passagem).join(Parada)
          .filter(db.and_(
            Aluno.nome == name_student,
            (Aluno.turno == shift.capitalize()) if not contraturno else True,
            Passagem.Aluno_id == Aluno.id,
            Passagem.passagem_fixa == True,
            (Passagem.passagem_contraturno == True) if contraturno else True,
            Passagem.Parada_codigo == Parada.codigo,
            Parada.Ponto_id == ponto.id
          ))
          .all()
        )

        if aluno:
          if len(aluno) > 1:
            if pos and isinstance(pos, str) and pos.isdigit():
              aluno = aluno[int(pos)]
            else:
              return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar o aluno. Por favor, recarregue a página e tente novamente.'})
          else:
            aluno = aluno[0]

          retorno['data'] = return_dict(aluno, not_includes=['id', 'email'])
          return jsonify(retorno)
    
    else:
      keys = db.session.query(Rota.codigo).filter_by(Linha_codigo=linha.codigo).subquery()
      not_include = (
        db.session.query(Marcador_Exclusao.key_item)
        .filter(db.and_(
          Marcador_Exclusao.tabela == 'Rota',
          Marcador_Exclusao.key_item.in_(keys.select())
        ))
        .subquery()
      )

      aluno = (
        db.session.query(Aluno).join(Passagem).join(Parada).join(Rota)
        .filter(db.and_(
          Aluno.nome == name_student,
          (Aluno.turno == shift.capitalize()) if not contraturno else True,
          Passagem.Aluno_id == Aluno.id,
          Passagem.passagem_fixa == True,
          (Passagem.passagem_contraturno == True) if contraturno else True,
          Passagem.Parada_codigo == Parada.codigo,
          Parada.Rota_codigo == Rota.codigo,
          Rota.Linha_codigo == linha.codigo,
          db.not_(Rota.codigo.in_(not_include.select()))
        ))
        .all()
      )

      if aluno:
        if len(aluno) > 1:
          if pos and isinstance(pos, str) and pos.isdigit():
            aluno = aluno[int(pos)]
          else:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar o aluno. Por favor, recarregue a página e tente novamente.'})
        else:
          aluno = aluno[0]

        retorno['data'] = return_dict(aluno, not_includes=['id', 'email'])
        return jsonify(retorno)
    
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações do aluno.'})
