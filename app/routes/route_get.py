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
            estado = 'Em Partida'
          elif rota.em_retorno:
            estado = 'Em Retorno'

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
      retorno['diaria_agendada'] = False
      retorno['msg'] = []

      rotas_diarias = (
        db.session.query(Linha, Rota, Parada, Passagem)
        .filter(db.and_(
          Passagem.passagem_fixa == False,
          Passagem.Aluno_id == user.id,
          Parada.codigo == Passagem.Parada_codigo,
          Rota.codigo == Parada.Rota_codigo,
          Rota.Linha_codigo == Linha.codigo,
          Linha.ferias == False
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

      routes_includes = []
      for linha, rota, parada, passagem in rotas_diarias:
        condiction = False
        if passagem.migracao_lotado or passagem.migracao_manutencao:
          record_day = (
            db.session.query(Registro_Aluno)
            .filter(db.and_(
              Registro_Aluno.Aluno_id == user.id,
              Registro_Aluno.data == passagem.data
            ))
            .first()
          )
          faltara = record_day.faltara
          contraturno = record_day.contraturno
          condiction = (
            faltara if rota.turno == user.turno else (faltara or not contraturno)
          )

        if (
          check_valid_datetime(passagem.data, parada.horario_passagem, add_limit=0.25)
          and passagem.data == date.today() and not condiction
        ):
          if rota.codigo not in routes_includes:
            not_dis = (
              db.session.query(Registro_Linha)
              .filter(db.and_(
                Registro_Linha.Linha_codigo == linha.codigo,
                Registro_Linha.data == passagem.data,
                Registro_Linha.funcionando == False
              ))
              .first()
            )
            if not linha.ferias and not not_dis:
              execute = True
              if passagem.migracao_lotado or passagem.migracao_manutencao:
                combine = datetime.combine(passagem.data, parada.horario_passagem)
                time_ant = combine - timedelta(minutes=45)
                time_dep = combine + timedelta(minutes=45)

                if (
                  db.session.query(Passagem).join(Parada)
                  .filter(db.and_(
                    Passagem.Parada_codigo == Parada.codigo,
                    Passagem.data == passagem.data,
                    Passagem.Aluno_id == user.id,
                    Passagem.passagem_fixa == False,
                    Parada.horario_passagem.between(time_ant.time(), time_dep.time()),
                    Parada.tipo == parada.tipo,
                    db.not_(db.or_(
                      Passagem.migracao_lotado == True,
                      Passagem.migracao_manutencao == True
                    ))
                  ))
                  .first()
                ):
                  execute = False

              if execute:
                routes_includes.append(rota.codigo)
                if linha.nome not in diarias:
                  diarias[linha.nome] = []

                estado = 'Inativa'
                if rota.em_partida:
                  estado = 'Em Partida'
                elif rota.em_retorno:
                  estado = 'Em Retorno'
                
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
          estado = 'Em Partida'
        elif rota_fixa.em_retorno:
          estado = 'Em Retorno'

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
          estado = 'Em Partida'
        elif rota_contraturno.em_retorno:
          estado = 'Em Retorno'

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
            estado = 'Em Partida'
          elif rota.em_retorno:
            estado = 'Em Retorno'

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
        if rotas_diarias:
          retorno['diaria_agendada'] = True
        else:
          return jsonify({'error': True, 'title': 'Erro de Identificação', 'text': 'Ocorreu um erro inesperado ao identificar a linha.'})

    return jsonify(retorno)
  
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações das rotas.'})


@app.route("/get_lines", methods=['GET'])
@login_required
def get_lines():
  role = current_user.roles[0].name
  data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}
  if role == 'motorista':
    data['participacao'] = []

  query = Membro.query.filter_by(dono=True).join(Linha).order_by(Linha.nome).all()
  if query:
    user = return_my_user()
    if user:
      if role == 'aluno':
        passagem = (
          Passagem.query.filter_by(
          Aluno_id=user.id,
          passagem_fixa=True
          )
          .first()
        )

        dates = return_dates_week(only_valid=True)
        diarias = (
          db.session.query(Linha, Rota, Parada, Passagem)
          .filter(db.and_(
            Rota.Linha_codigo == Linha.codigo,
            Parada.Rota_codigo == Rota.codigo,
            Passagem.Parada_codigo == Parada.codigo,
            Passagem.Aluno_id == user.id,
            Passagem.passagem_fixa == False,
            Passagem.data.in_(dates)
          ))
          .all()
        )

        diarias_codes = []
        for linha, rota, parada, _passagem in diarias:
          condiction = False
          if _passagem.migracao_lotado or _passagem.migracao_manutencao:
            record_day = (
              db.session.query(Registro_Aluno)
              .filter(db.and_(
                Registro_Aluno.Aluno_id == user.id,
                Registro_Aluno.data == _passagem.data
              ))
              .first()
            )
            faltara = record_day.faltara
            contraturno = record_day.contraturno
            condiction = (
              faltara if rota.turno == user.turno else (faltara or not contraturno)
            )

          not_dis = (
            db.session.query(Registro_Linha)
            .filter(db.and_(
              Registro_Linha.Linha_codigo == linha.codigo,
              Registro_Linha.data == _passagem.data,
              Registro_Linha.funcionando == False
            ))
            .first()
          )
          if (
            check_valid_datetime(_passagem.data, parada.horario_passagem, add_limit=0.25)
            and not linha.ferias and not not_dis and not condiction
          ):
            diarias_codes.append(linha.codigo)

        if passagem:
          data['minha_linha'] = passagem.parada.ponto.linha.nome

      for result in query:
        linha = result.linha
        dict_linha = {
          'nome': linha.nome, 'ferias': linha.ferias, 
          'paga': linha.paga, 'diaria': (linha.codigo in diarias_codes) if role == 'aluno' else False
        }

        if linha.cidade not in data['cidades']:
          data['cidades'][linha.cidade] = []

        data['cidades'][linha.cidade].append(dict_linha)
        dict_linha['dono'] = result.motorista.nome

        if role == 'motorista':
          if dict_linha['dono'] == user.nome:
            data['minha_linha'].append(dict_linha)
          elif return_relationship(linha.codigo):
            data['participacao'].append(dict_linha)

  else: data['identify'] = False
  return jsonify(data)


@app.route("/get_summary_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_summary_route(name_line, surname, shift, hr_par, hr_ret):
  role = current_user.roles[0].name
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    retorno = {'error': False, 'role': role, 'data_forecast': True}
    if linha.ferias:
      retorno['data_forecast'] = False
      retorno['data'] = 'Os registros de previsão mais recentes não estarão disponíveis enquanto a linha estiver em período de férias.'
    
    rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, None)
    if rota:
      dates = return_dates_week()
      today = date.today()
      tomorrow = today + timedelta(days=1)
      if today.weekday() in [5, 6]:
        today = dates[0]

      relationship = return_relationship(linha.codigo)
      not_dis = (
        db.session.query(Registro_Linha.data)
        .filter(db.and_(
          Registro_Linha.Linha_codigo == linha.codigo,
          Registro_Linha.funcionando == False,
          Registro_Linha.data.in_(dates)
        ))
        .all()
      )
      not_dis = [_date[0] for _date in not_dis]

      while True:
        if today.weekday() == 5:
          retorno['data_forecast'] = False
          retorno['data'] = 'Os registros de previsão da próxima semana ainda não estão disponíveis.'
          break

        elif (
          not check_valid_datetime(today, rota.horario_retorno, add_limit=0.75)
          or today in not_dis
        ):
          today = today + timedelta(days=1)
        
        else: break

      check_daily = (
        db.session.query(Parada, Passagem)
        .filter(db.and_(
          Passagem.Parada_codigo == Parada.codigo,
          Parada.Rota_codigo == rota.codigo,
          Passagem.Aluno_id == current_user.primary_key,
          Passagem.passagem_fixa == False,
          Passagem.data == today
        ))
        .first()
      ) if role == 'aluno' else False
      
      if (
        (relationship and relationship != 'não participante') or 
        (not linha.ferias and check_daily)
      ):
        veiculo = rota.onibus
        capacidade = veiculo.capacidade if veiculo else '-'
        retorno['capacidade'] = capacidade

        estado = 'Inativa'
        if rota.em_partida:
          estado = 'Em Partida'
        elif rota.em_retorno:
          estado = 'Em Retorno'
        retorno['estado'] = estado

        if retorno['data_forecast']:
          data = {}
          if today == date.today():
            forecast = 'Hoje'
          elif today == tomorrow:
            forecast = 'Amanhã'
          else:
            forecast = f'{return_day_week(today.weekday())} {format_date(today)}'

          for tipo in ['partida', 'retorno']:
            registro = Registro_Rota.query.filter_by(
              data=today, tipo=tipo, Rota_codigo=rota.codigo
            ).first()

            if registro.atualizar:
              modify_forecast_route(rota, registro)
            if tipo == 'partida':
              data['partida_passou'] = not check_valid_datetime(today, rota.horario_partida, add_limit=0.75)
            data[f'previsao_{tipo}'] = registro.previsao_pessoas

          retorno['data'] = data
        else:
          forecast = 'Indisponível'

        retorno['day_week'] = f'Previsão: {forecast}'
        return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da rota. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_summary_line/<name_line>", methods=['GET'])
@login_required
def get_summary_line(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
    dates = return_dates_week()
    subquery = (
      db.session.query(Parada.codigo).join(Rota)
      .filter(db.and_(
        Parada.Rota_codigo == Rota.codigo,
        Rota.Linha_codigo == linha.codigo
      ))
      .subquery()
    )
    quantidade_aluno = (
      db.session.query(func.count(func.distinct(Passagem.Aluno_id)))
      .filter(db.and_(
        Passagem.passagem_fixa == True,
        Passagem.Parada_codigo.in_(subquery.select())
      ))
      .scalar()
    )

    records = (
      db.session.query(Registro_Linha)
      .filter(db.and_(
        Registro_Linha.Linha_codigo == linha.codigo,
        Registro_Linha.data.in_(dates)
      ))
      .all()
    )

    retorno = {
      'error': False,
      'paga': linha.paga,
      'data': {
        'local': linha.cidade,
        'qnt_participantes': f'{quantidade_aluno} {"cadastrados" if quantidade_aluno != 1 else "cadastrado"}'
      },
      'calendario': {}
    }
    if linha.paga:
      retorno['data']['valor_cartela'] = f'R$ {format_money(linha.valor_cartela)}'
      retorno['data']['valor_diaria'] = f'R$ {format_money(linha.valor_diaria)}'
    
    for record in records:
      color = 'green'
      if not record.funcionando:
        if record.feriado:
          color = 'yellow'
        else: color = 'red'
      if linha.ferias and check_valid_datetime(record.data):
        color = 'red'
      retorno['calendario'][return_day_week(record.data.weekday())] = color

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
    data = {'fixa': {'msg': [], 'paradas': deque()}, 'diaria': {'msg': [], 'paradas': []}}
    retorno = {'error': False, 'data': data}
    msg_ferias = 'Sua linha está em período de férias.'

    passagens = (
      db.session.query(Linha, Rota, Parada, Passagem)
      .filter(db.and_(
        Rota.Linha_codigo == Linha.codigo,
        Parada.Rota_codigo == Rota.codigo,
        Passagem.Parada_codigo == Parada.codigo,
        Passagem.Aluno_id == user.id
      ))
      .order_by(
        Passagem.data,
        db.case([
          (db.and_(Parada.tipo.like("%partida%"), Passagem.passagem_fixa == True), 1),
          (db.and_(Parada.tipo.like("%retorno%"), Passagem.passagem_fixa == False), 1)
        ], else_=0)
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
        'tipo': parada.tipo.capitalize(),
        'exibicao': 'normal'
      }

      if passagem.passagem_fixa:
        if linha.ferias and msg_ferias not in data['fixa']['msg']:
          data['fixa']['msg'].append(msg_ferias)

        if passagem.passagem_contraturno:
          info['data'] = 'fixo | Contraturno'
          data['fixa']['paradas'].append(info)
          tipos.remove('contraturno')
        else:
          info['data'] = 'fixo'
          data['fixa']['paradas'].appendleft(info)
          tipos.remove(info['tipo'].lower())
      else:
        not_dis = (
          db.session.query(Registro_Linha)
          .filter(db.and_(
            Registro_Linha.Linha_codigo == linha.codigo,
            Registro_Linha.data == passagem.data,
            Registro_Linha.funcionando == False
          ))
          .first()
        )
        if not linha.ferias and not not_dis:
          today = date.today()
          tomorrow = date.today() + timedelta(days=1)

          if check_valid_datetime(passagem.data, parada.horario_passagem, add_limit=0.25):
            faltara = False; contraturno = False
            execute = True; condiction = False

            if passagem.migracao_lotado or passagem.migracao_manutencao:
              combine = datetime.combine(passagem.data, parada.horario_passagem)
              time_ant = combine - timedelta(minutes=45)
              time_dep = combine + timedelta(minutes=45)
              if (
                db.session.query(Passagem).join(Parada)
                .filter(db.and_(
                  Passagem.Parada_codigo == Parada.codigo,
                  Passagem.Aluno_id == user.id,
                  Passagem.data == passagem.data,
                  Parada.horario_passagem.between(time_ant.time(), time_dep.time()),
                  Passagem.passagem_fixa == False,
                  db.not_(db.or_(
                    Passagem.migracao_lotado == True,
                    Passagem.migracao_manutencao == True
                  ))
                ))
                .first()
              ):
                execute = False
              else:
                record_day = (
                  db.session.query(Registro_Aluno)
                  .filter(db.and_(
                    Registro_Aluno.Aluno_id == user.id,
                    Registro_Aluno.data == passagem.data
                  ))
                  .first()
                )
                faltara = record_day.faltara
                contraturno = record_day.contraturno
                condiction = (
                  faltara if rota.turno == user.turno else (faltara or not contraturno)
                )
            
            if execute and not condiction:
              info_date = format_date(passagem.data)
              day_week = return_day_week(passagem.data.weekday())
              data['diaria']['paradas'].append(info)
              info['exibicao'] = 'agendado'

              if passagem.data == today:
                info['data'] = 'Hoje'
              elif passagem.data == tomorrow:
                info['data'] = 'Amanhã'
              else: info['data'] = f'{day_week[:3]} - {info_date}'

              if passagem.migracao_lotado:
                info['exibicao'] = 'lotado'
                info['data'] = f'{info["data"]} | Transferido devido lotação'
                msg = 'Veículo lotado: Seu motorista alterou o veículo que você usará devido a uma lotação prevista para seu transporte habitual.'
                if msg not in data['diaria']['msg']:
                  data['diaria']['msg'].append(msg)
              
              elif passagem.migracao_manutencao:
                info['exibicao'] = 'manutencao'
                info['data'] = f'{info["data"]} | Transferido devido manutenção'
                msg = 'Veículo em manutenção: Seu motorista alterou o veículo que você usará devido a um defeito encontrado em seu transporte habitual.'
                if msg not in data['diaria']['msg']:
                  data['diaria']['msg'].append(msg)
    
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
    line = None
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
      if line is None:
        line = parada.rota.linha

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
        db.not_(db.or_(
          Passagem.migracao_lotado == True,
          Passagem.migracao_manutencao == True
        )),
        Parada.Rota_codigo == Rota.codigo
      ))
      .order_by(
        db.case([(Parada.tipo.like("%partida%"), 0)], else_=1)
      )
      .all()
    )
    registro_linha = (
      db.session.query(Registro_Linha)
      .filter(db.and_(
        Registro_Linha.data.in_(dates),
        Registro_Linha.Linha_codigo == line.codigo,
      ))
      .order_by(Registro_Linha.data)
      .all()
    ) if line is not None else False

    registros_aluno = (
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

    for index, registro in enumerate(registros_aluno):
      value_partida = check_valid_datetime(
        registro.data, info_times['partida']
      ) if info_times['partida'] else True

      value_contraturno = check_valid_datetime(
        registro.data, info_times['contraturno']
      ) if info_times['contraturno'] else True

      invalida = False
      info_invalid = ''

      if registro_linha:
        record = registro_linha[index]
        if not record.funcionando and not line.ferias:
          invalida = True
          if record.feriado:
            info_invalid = 'Feriado'
          else:
            info_invalid = 'Fora de serviço'

      info = {
        'data': format_date(registro.data),
        'faltara': return_str_bool(registro.faltara),
        'contraturno': return_str_bool(registro.contraturno) if not registro.faltara else 'Não',
        'valida': check_valid_datetime(registro.data) if not invalida else False,
        'content_contraturno': value_contraturno,
        'content_faltara': value_partida,
        'info': info_invalid,
        'diarias': []
      }

      if not invalida and (not line.ferias if line else True):
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
    data = []
    retorno = {'error': False, 'data': data}
    dates = return_dates_week(only_valid=True)
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
        Registro_Rota.previsao_pessoas > Onibus.capacidade,
        Registro_Rota.atualizar == False,
        Registro_Rota.data.in_(dates)
      ))
      .order_by(Registro_Rota.data, Rota.horario_partida)
      .all()
    )

    routes_includes = []
    for line, route, record, onibus in todas_as_rotas:
      reference = route.horario_partida if record.tipo == 'partida' else route.horario_retorno
      if check_valid_datetime(record.data, reference, add_limit=0.75) and route.codigo not in routes_includes:
        routes_includes.append(route.codigo)

        estado = 'Inativa'
        if route.em_partida:
          estado = 'Em Partida'
        elif route.em_retorno:
          estado = 'Em Retorno'
        
        info = {
          'line': line.nome,
          'turno': route.turno,
          'horario_partida': format_time(route.horario_partida),
          'horario_retorno': format_time(route.horario_retorno),
          'quantidade': count_part_route(route.codigo),
          'apelido': onibus.apelido,
          'motorista': onibus.motorista.nome,
          'estado': estado
        }
        data.append(info)

    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar os dados de previsão. Por favor, recarregue a página e tente novamente.'})


@app.route("/get_forecast_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_forecast(name_line, surname, shift, hr_par, hr_ret):
  pos = request.args.get('pos')
  user = return_my_user()

  if user and name_line and surname and shift and hr_par and hr_ret:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      relationship = return_relationship(linha.codigo)
      role = current_user.roles[0].name
      retorno = {'error': False, 'role': role, 'relacao': relationship}

      rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)
      if rota is not None:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

        vehicle = rota.onibus
        if vehicle:
          data = {}
          dates = return_dates_week()
          today = date.today()
          retorno['capacidade'] = vehicle.capacidade

          records_line = (
            db.session.query(Registro_Linha)
            .filter(db.and_(
              Registro_Linha.data.in_(dates),
              Registro_Linha.Linha_codigo == linha.codigo
            ))
            .order_by(Registro_Linha.data)
            .all()
          )
          not_includes = [
            record.data for record in records_line
            if not record.funcionando
          ]

          records_route = (
            db.session.query(Registro_Rota)
            .filter(db.and_(
              Registro_Rota.data.in_(dates),
              Registro_Rota.Rota_codigo == rota.codigo
            ))
            .order_by(Registro_Rota.data)
            .all()
          )

          for record in records_route:
            week_day = return_day_week(record.data.weekday())
            if week_day not in data:
              data_local = {
                'date': format_date(record.data), 'date_valid': check_valid_datetime(record.data),
                'not_dis': False
              }
              data_local['info'] = {'partida': {}, 'retorno': {}}
              data_local['today'] = (record.data == today)

              if (
                (linha.ferias and data_local['date_valid'])
                or record.data in not_includes
              ):
                data_local['not_dis'] = True
                msg = '<Férias>'

                if not linha.ferias:
                  msg = '<Fora de serviço>'
                  if records_line[record.data.weekday()].feriado:
                    msg = '<Feriado>'
                data_local['msg'] = msg

              data[week_day] = data_local

            if not data_local['not_dis']:
              time_reference = rota.horario_partida if record.tipo == 'partida' else rota.horario_retorno
              check_valid = check_valid_datetime(record.data, time_reference, add_limit=0.75)

              if check_valid and record.atualizar:
                modify_forecast_route(rota, record)
              
              data_local['info'][record.tipo]['valid'] = check_valid
              data_local['info'][record.tipo]['qnt'] = record.previsao_pessoas
              color = 'normal'

              if record.previsao_pessoas > vehicle.capacidade:
                color = 'red'
              elif (vehicle.capacidade - 5) <= record.previsao_pessoas <= vehicle.capacidade:
                color = 'yellow'
              data_local['info'][record.tipo]['color'] = color
          
          retorno['data'] = data
          return jsonify(retorno)
        
        return jsonify({'error': True, 'title': 'Previsão Indisponível', 'text': 'A previsão completa não está disponível pois a rota não possui vínculo com nenhum veículo.'})

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar os dados de previsão. Por favor, recarregue a página e tente novamente.'})


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

    dates = return_dates_week()
    calendario = {}
    retorno['calendario'] = calendario

    records = (
      db.session.query(Registro_Linha)
      .filter(db.and_(
        Registro_Linha.Linha_codigo == linha.codigo,
        Registro_Linha.data.in_(dates)
      ))
      .order_by(Registro_Linha.data)
      .all()
    )

    for index, date in enumerate(dates):
      week_day = return_day_week(date.weekday())
      calendario[week_day] = {'valida': False, 'info': 'Em atividade'}
      if not records[index].funcionando:
        if records[index].feriado:
          calendario[week_day]['info'] = 'Feriado'
        else:
          calendario[week_day]['info'] = 'Fora de serviço'

      if check_valid_datetime(date):
        if linha.ferias:
          calendario[week_day]['info'] = 'Férias'
        else:
          calendario[week_day]['valida'] = True
          
    return jsonify(retorno)

  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver/<name_line>", methods=['GET'])
@login_required
def get_interface_driver(name_line):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relacoes = (
      db.session.query(Membro).join(Motorista)
      .filter(db.and_(
        Membro.Motorista_id == Motorista.id,
        Membro.Linha_codigo == linha.codigo
      ))
      .order_by(Motorista.nome)
      .all()
    )
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
        'capacidade': vehicle.capacidade,
        'defect': False
      }

      if (
        db.session.query(Manutencao)
        .filter(db.and_(
          Manutencao.Onibus_id == vehicle.id,
          Manutencao.data_fim.is_(None)
        ))
        .first()
      ):
        info['defect'] = True

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
        db.session.query(Parada, Passagem)
        .filter(db.and_(
          Passagem.Aluno_id == user.id,
          Passagem.passagem_fixa == False,
          Passagem.Parada_codigo == Parada.codigo,
          Parada.Rota_codigo.in_(code_routes)
        ))
        .order_by(Passagem.data)
        .all()
      )

      routes_includes = []
      for parada, passagem in minhas_diarias:
        not_dis = (
          db.session.query(Registro_Linha)
          .filter(db.and_(
            Registro_Linha.Linha_codigo == linha.codigo,
            Registro_Linha.data == passagem.data,
            Registro_Linha.funcionando == False
          ))
          .first()
        )
        if (
          check_valid_datetime(passagem.data, parada.horario_passagem, add_limit=0.25)
          and not linha.ferias and not not_dis
        ):
          rota = parada.rota
          execute = True
          condiction = False

          if passagem.migracao_lotado or passagem.migracao_manutencao:
            combine = datetime.combine(passagem.data, parada.horario_passagem)
            time_ant = combine - timedelta(minutes=45)
            time_dep = combine + timedelta(minutes=45)
            if (
              db.session.query(Passagem).join(Parada)
              .filter(db.and_(
                Passagem.Parada_codigo == Parada.codigo,
                Passagem.Aluno_id == user.id,
                Passagem.data == passagem.data,
                Parada.horario_passagem.between(time_ant.time(), time_dep.time()),
                Passagem.passagem_fixa == False,
                db.not_(db.or_(
                  Passagem.migracao_lotado == True,
                  Passagem.migracao_manutencao == True
                ))
              ))
              .first()
            ):
              execute = False
            else:
              record_day = (
                db.session.query(Registro_Aluno)
                .filter(db.and_(
                  Registro_Aluno.Aluno_id == user.id,
                  Registro_Aluno.data == passagem.data
                ))
                .first()
              )
              faltara = record_day.faltara
              contraturno = record_day.contraturno
              condiction = (
                faltara if rota.turno == user.turno else (faltara or not contraturno)
              )

          if execute and not condiction:
            if rota.codigo not in routes_includes:
              routes_includes.append(rota.codigo)
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
          return jsonify({'error': False, 'data': [user.nome]})
        return jsonify({'error': False, 'data': []})

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
  only_valid = request.args.get('only_valid')

  if surname_ignore == 'Não definido':
    surname_ignore = None

  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relacao = return_relationship(linha.codigo)
    if relacao and relacao != 'membro':
      retorno = {'error': False}
      vehicles = (
        Onibus.query.filter_by(Linha_codigo=linha.codigo)
        .order_by(Onibus.apelido).all()
      )
      list_valid = []
      list_invalid = []

      for vehicle in vehicles:
        if surname_ignore != vehicle.apelido:
          motorista = vehicle.motorista
          if motorista:
            list_valid.append(f"{vehicle.apelido} > {motorista.nome}")
          elif not only_valid:
            list_invalid.append(f"{vehicle.apelido} > Nenhum")

      retorno['data'] = list_valid + list_invalid
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
          retorno['diarias'] = {}

          today = datetime.today()
          tomorrow = today + timedelta(days=1)

          diarias = (
            db.session.query(Parada, Ponto, Passagem)
            .filter(db.and_(
              Parada.Rota_codigo == rota.codigo,
              Ponto.id == Parada.Ponto_id,
              Passagem.Parada_codigo == Parada.codigo,
              Passagem.Aluno_id == user.id,
              Passagem.passagem_fixa == False
            ))
            .order_by(
              Passagem.data,
              Ponto.nome,
              db.case([(Parada.tipo.like("%partida%"), 0)], else_=1)
            )
            .all()
          )
          for parada, ponto, diaria in diarias:
            not_dis = (
              db.session.query(Registro_Linha)
              .filter(db.and_(
                Registro_Linha.Linha_codigo == linha.codigo,
                Registro_Linha.data == diaria.data,
                Registro_Linha.funcionando == False
              ))
              .first()
            )

            condiction = False
            if diaria.migracao_lotado or diaria.migracao_manutencao:
              record_day = (
                db.session.query(Registro_Aluno)
                .filter(db.and_(
                  Registro_Aluno.Aluno_id == user.id,
                  Registro_Aluno.data == diaria.data
                ))
                .first()
              )
              faltara = record_day.faltara
              contraturno = record_day.contraturno
              condiction = (
                faltara if rota.turno == user.turno else (faltara or not contraturno)
              )

            if (
              check_valid_datetime(diaria.data, parada.horario_passagem, add_limit=0.25)
              and not linha.ferias and not not_dis and not condiction
            ):
              execute = True
              if diaria.migracao_lotado or diaria.migracao_manutencao:
                combine = datetime.combine(diaria.data, parada.horario_passagem)
                time_ant = combine - timedelta(minutes=45)
                time_dep = combine + timedelta(minutes=45)
                if (
                  db.session.query(Passagem).join(Parada)
                  .filter(db.and_(
                    Passagem.Parada_codigo == Parada.codigo,
                    Passagem.Aluno_id == user.id,
                    Passagem.data == diaria.data,
                    Parada.horario_passagem.between(time_ant.time(), time_dep.time()),
                    Passagem.passagem_fixa == False,
                    db.not_(db.or_(
                      Passagem.migracao_lotado == True,
                      Passagem.migracao_manutencao == True
                    ))
                  ))
                  .first()
                ):
                  execute = False

              if execute:
                date = format_date(diaria.data)
                if date == today:
                  date = 'Hoje'
                elif date == tomorrow:
                  date = 'Amanhã'

                if date not in retorno['diarias']:
                  retorno['diarias'][date] = {}
                  retorno['diarias'][date]['dayweek'] = return_day_week(diaria.data.weekday())
                  retorno['diarias'][date]['date'] = date
                  retorno['diarias'][date]['data'] = []
                  
                retorno['diarias'][date]['data'].append({
                  'valid': check_valid_datetime(diaria.data, parada.horario_passagem),
                  'edit': False if diaria.migracao_lotado or diaria.migracao_manutencao else True,
                  'tipo': parada.tipo.capitalize(),
                  'nome': ponto.nome
                })
          retorno['diarias'] = [value for value in retorno['diarias'].values()]

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


@app.route("/get_stops_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_stops_route(name_line, surname, shift, hr_par, hr_ret):
  pos = request.args.get('pos')

  if name_line and shift and hr_par and hr_ret:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      retorno = {'error': False, 'data': {'partida': [], 'retorno': []}}
      rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)

      if rota is not None:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
        
      paradas = (
        db.session.query(Parada, Ponto).join(Rota)
        .filter(db.and_(
          Parada.Ponto_id == Ponto.id,
          Parada.Rota_codigo == rota.codigo,
        ))
        .order_by(Parada.ordem)
        .all()
      )

      for parada, ponto in paradas:
        retorno['data'][parada.tipo].append(ponto.nome)
      
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


'''~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Route ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_stop_path/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>/<type_>", methods=['GET'])
@login_required
def get_stop_path(name_line, surname, shift, hr_par, hr_ret, type_):
  if name_line and shift and hr_par and hr_ret and type_:
      linha = Linha.query.filter_by(nome=name_line).first()
      if linha:
        role = current_user.roles[0].name
        relationship = return_relationship(linha.codigo)

        data = []
        retorno = {'error': False, 'role': role, 'relacao': relationship, 'data': data}
        rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, None)
        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
          
          today = date.today()
          pass_daily = False
          meu_ponto = None

          if role == 'aluno':
            not_dis_line = (
              db.session.query(Registro_Linha)
              .filter(db.and_(
                Registro_Linha.Linha_codigo == linha.codigo,
                Registro_Linha.data == today,
                Registro_Linha.funcionando == False
              ))
              .first()
            )

            user = return_my_user()
            record_stundent = (
              db.session.query(Registro_Aluno)
              .filter(db.and_(
                Registro_Aluno.data == today,
                Registro_Aluno.Aluno_id == user.id
              ))
              .first()
            )
            check_daily_in_route = (
              db.session.query(Parada, Passagem)
              .filter(db.and_(
                Passagem.Parada_codigo == Parada.codigo,
                Parada.Rota_codigo == rota.codigo,
                Passagem.data == today,
                Passagem.passagem_fixa == False,
                Passagem.Aluno_id == user.id
              ))
              .all()
            )

            execute = True
            for stop, pass_ in check_daily_in_route:
              if pass_.migracao_lotado or pass_.migracao_manutencao:
                combine = datetime.combine(today, stop.horario_passagem)
                time_ant = combine - timedelta(minutes=45)
                time_dep = combine + timedelta(minutes=45)

                condiction = (
                  db.session.query(Passagem).join(Parada)
                  .filter(db.and_(
                    Passagem.Parada_codigo == Parada.codigo,
                    Parada.horario_passagem.between(time_ant.time(), time_dep.time()),
                    Passagem.data == today,
                    Passagem.passagem_fixa == False,
                    Passagem.Aluno_id == user.id,
                    db.not_(db.or_(
                      Passagem.migracao_lotado == True,
                      Passagem.migracao_manutencao == True
                    ))
                  ))
                  .first()
                )

                student_dis = True
                ignore = return_ignore_route(user.turno)
                if user.turno == rota.turno:
                  if (record_stundent.contraturno and stop.tipo == ignore) or record_stundent.faltara:
                    student_dis = False
                else:
                  if not (record_stundent.contraturno and stop.tipo == ignore) or record_stundent.faltara:
                      student_dis = False

                if not condiction and not not_dis_line and student_dis:
                  pass_daily = True
                  if stop.tipo == type_:
                    meu_ponto = stop.ponto.nome
                    execute = False
                  break
              else:
                pass_daily = True
                if stop.tipo == type_:
                  meu_ponto = stop.ponto.nome
                  execute = False
                break
            
            if execute and record_stundent:
              check_daily = (
                db.session.query(Parada).join(Passagem).join(Rota)
                .filter(db.and_(
                  Passagem.Parada_codigo == Parada.codigo,
                  Parada.Rota_codigo == Rota.codigo,
                  Passagem.data == today,
                  Passagem.passagem_fixa == False,
                  Passagem.Aluno_id == user.id,
                  Parada.tipo == type_,
                  Rota.turno == rota.turno
                ))
                .first()
              )

              if not check_daily and not not_dis_line:
                pass_fixed = (
                  db.session.query(Parada, Ponto).join(Passagem)
                  .filter(db.and_(
                    Parada.Ponto_id == Ponto.id,
                    Passagem.Parada_codigo == Parada.codigo,
                    Parada.Rota_codigo == rota.codigo,
                    Parada.tipo == type_,
                    Passagem.passagem_fixa == True,
                    Passagem.Aluno_id == user.id
                  ))
                  .first()
                )
                if pass_fixed:
                  parada_fixed, ponto_fixed = pass_fixed
                  pass_contraturno = Passagem.query.filter_by(Aluno_id=user.id, passagem_contraturno=True).first()
                  ignore = return_ignore_route(user.turno)

                  if user.turno == rota.turno:
                    if pass_contraturno:
                      if not (record_stundent.contraturno and parada_fixed.tipo == ignore) and not record_stundent.faltara:
                        meu_ponto = ponto_fixed.nome
                    else:
                      if not record_stundent.faltara:
                        meu_ponto = ponto_fixed.nome
                  else:
                    if record_stundent.contraturno and parada_fixed.tipo == ignore and not record_stundent.faltara:
                      meu_ponto = ponto_fixed.nome

          if (relationship and relationship != 'não participante') or pass_daily:
            stops = (
              db.session.query(Parada, Ponto)
              .filter(db.and_(
                Parada.Ponto_id == Ponto.id,
                Parada.Rota_codigo == rota.codigo,
                Parada.tipo == type_,
              ))
              .order_by(Parada.ordem)
              .all()
            )

            for parada, ponto in stops:
              passou = False
              if (
                Registro_Passagem.query
                .filter_by(data=today, Parada_codigo=parada.codigo)
                .first()
              ):
                passou = True

              data.append({
                'local': ponto.nome,
                'horario': format_time(parada.horario_passagem),
                'tolerancia': f'{ponto.tempo_tolerancia} min',
                'meu_ponto': (ponto.nome == meu_ponto),
                'passou': passou
              })
            
            retorno['passagem_diaria'] = pass_daily
            return jsonify(retorno)
            
  return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações da linha.'})
