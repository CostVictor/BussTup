from flask_security import login_required, roles_required, current_user
from app import app, cidades, turnos
from flask import request, jsonify
from datetime import time, datetime
from app.tasks import sched, transferir_por_defeito
from app.utilities import *
from app.database import *
import bcrypt


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ Edit Profile ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_profile", methods=['PATCH'])
@login_required
def edit_perfil():
  data = request.get_json()
  if data and 'field' in data and 'new_value' in data and 'password' in data:
    if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.password_hash):
      not_modify = ['id', 'curso', 'turno', 'primary_key', 'fs_uniquifier', 'active', 'analysis', 'aceitou_termo_uso_dados']
      field = data['field']
      new_value = data['new_value']

      if field and field not in not_modify and new_value:
        if field == 'login':
          if not User.query.filter_by(login=new_value).first():
            try:
              current_user.login = new_value
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': 'Seu login foi alterada com sucesso.'})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao modificar o perfil: {str(e)}')
              
          return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'O nome de usuário definido não atende aos critérios de cadastro para ser utilizado como login. Por favor, escolha outro nome.'})

        elif field == 'senha':
          if isinstance(new_value, str):
            new_password_hash = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
            try:
              current_user.password_hash = new_password_hash
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': 'Sua senha foi alterada com sucesso.'})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao modificar o perfil: {str(e)}')
        else:
          my_user = return_my_user()
          if my_user and hasattr(my_user, field) and field != 'id':
            if field == 'nome':
              new_value = capitalize(new_value, current_user.roles[0].name)
              if not new_value:
                return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'O nome definido não atende aos critérios de cadastro do aluno. Por favor, defina seu nome completo para prosseguir.'})

            try:
              setattr(my_user, field, new_value)
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao modificar o perfil: {str(e)}')
    else:
      return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Edit Page ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_contraturno_fixo", methods=['PUT'])
@login_required
@roles_required("aluno")
def edit_contraturno_fixo():
  data = request.get_json()
  execute = True

  if data:
    for dia in data:
      if dia not in dias_semana:
        execute = False; break

  if execute:
    key = current_user.primary_key
    user = return_my_user()

    info_times = {
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
      if passagem.passagem_contraturno:
        if user.turno == 'Matutino':
          info_times['contraturno'] = time(hour=12)
        else:
          info_times['contraturno'] = parada.horario_passagem

    contraturnos = (
      Contraturno_Fixo.query
      .filter_by(Aluno_id=key).all()
    )
    registros = (
      db.session.query(Registro_Aluno)
      .filter(db.and_(
        Registro_Aluno.Aluno_id == key,
        Registro_Aluno.data.in_(return_dates_week())
      ))
      .order_by(Registro_Aluno.data)
      .all()
    )

    try:
      for record in contraturnos:
        check = check_valid_datetime(
          registros[record.dia_fixo].data,
          info_times['contraturno']
        ) if info_times['contraturno'] else False

        if check:
          registros[record.dia_fixo].contraturno = False
        db.session.delete(record)
      
      for dia in data:
        week_day = return_day_week(dia, reverse=True)
        check = check_valid_datetime(
          registros[week_day].data,
          info_times['contraturno']
        ) if info_times['contraturno'] else False

        if check:
          registros[week_day].contraturno = True

        db.session.add(Contraturno_Fixo(
          dia_fixo=week_day,
          Aluno_id=key
        ))

      db.session.commit()
      return jsonify({'error': False, 'title': 'Contraturno fixo atualizado', 'text': ''})

    except Exception as e:
      db.session.rollback()
      print(f'Erro ao salvar o contraturno fixo: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_day", methods=['PUT'])
@login_required
@roles_required("aluno")
def edit_day():
  data = request.get_json()
  user = return_my_user()
  dates = return_dates_week(only_valid=True)

  if user and data and 'faltara' in data and 'contraturno' in data and 'data' in data:
    fixas = (
      db.session.query(Passagem)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        db.or_(
          Passagem.passagem_fixa == True,
          db.and_(
            Passagem.data.in_(dates),
            db.or_(
              Passagem.migracao_lotado == True,
              Passagem.migracao_manutencao == True
            )
          )
        )
      ))
      .order_by(db.desc(Passagem.passagem_fixa))
      .all()
    )

    code_line = None
    routes = {
      'fixa': False, 'contraturno': False, 
      'tr_fixa': False, 'tr_contraturno': False
    }
    for passagem in fixas:
      parada = passagem.parada
      if passagem.passagem_fixa:
        routes['contraturno' if passagem.passagem_contraturno else 'fixa'] = parada
      else:
        if routes['fixa'] and parada.Ponto_id == routes['fixa'].Ponto_id:
          routes['tr_fixa'] = parada
        
        if routes['contraturno'] and parada.Ponto_id == routes['contraturno'].Ponto_id:
          routes['tr_contraturno'] = parada

      if not code_line:
        code_line = parada.rota.Linha_codigo
    
    for key, value in routes.items():
      if value:
        routes[key] = value.Rota_codigo

    not_dis = (
      db.session.query(Registro_Linha.data)
      .filter(db.and_(
        Registro_Linha.data.in_(dates),
        Registro_Linha.Linha_codigo == code_line,
        Registro_Linha.funcionando == False
      ))
      .all()
    ) if code_line else []

    try:
      dia = format_date(data['data'], reverse=True)
      check_not_dis = [True for date_ in not_dis if dia in date_]

      if dia in dates and not check_not_dis:
        record_student = Registro_Aluno.query.filter_by(
          Aluno_id=user.id, data=dia
        ).first()

        record_route_fixed = (
          Registro_Rota.query.filter_by(Rota_codigo=routes['fixa'], data=dia).all()
        ) if routes['fixa'] else []

        record_route_tr_fixed = (
          Registro_Rota.query.filter_by(Rota_codigo=routes['tr_fixa'], data=dia).all()
        ) if routes['tr_fixa'] else []

        record_route_contraturno = (
          Registro_Rota.query.filter_by(
            Rota_codigo=routes['contraturno'], data=dia, 
            tipo=return_ignore_route(user.turno)
          ).first()
        ) if routes['contraturno'] else []

        record_route_tr_contraturno = (
          Registro_Rota.query.filter_by(
            Rota_codigo=routes['tr_contraturno'], data=dia, 
            tipo=return_ignore_route(user.turno)
          ).first()
        ) if routes['tr_contraturno'] else []

        if record_student:
          if data['faltara']:
            if not record_student.faltara and (record_route_fixed or record_route_tr_fixed):
              for record in (record_route_fixed + record_route_tr_fixed):
                set_update_record_route(record)
            
            if record_student.contraturno and (record_route_contraturno or record_route_tr_contraturno):
              if record_route_contraturno:
                set_update_record_route(record_route_contraturno)
              if record_route_tr_contraturno:
                set_update_record_route(record_route_tr_contraturno)

            record_student.faltara = True
            record_student.contraturno = False
          else:
            if record_student.faltara and (record_route_fixed or record_route_tr_fixed):
              for record in (record_route_fixed + record_route_tr_fixed):
                set_update_record_route(record)
            
            if record_student.contraturno != data['contraturno'] and (record_route_contraturno or record_route_tr_contraturno):
              if record_route_contraturno:
                set_update_record_route(record_route_contraturno)
              if record_route_tr_contraturno:
                set_update_record_route(record_route_tr_contraturno)

              for record in (record_route_fixed + record_route_tr_fixed):
                if record.tipo == return_ignore_route(user.turno):
                  set_update_record_route(record)

            record_student.faltara = False
            record_student.contraturno = data['contraturno']
          
          db.session.commit()
          if dia == date.today():
            sched.add_job(
              None, transferir_por_defeito, trigger='date', 
              run_date=datetime.now() + timedelta(seconds=1), max_instances=30
            )
          return jsonify({'error': False, 'title': f'{return_day_week(dia.weekday())}-feira atualizada', 'text': ''})

    except Exception as e:
      db.session.rollback()
      print(f'Erro ao salvar o dia: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Edit Line ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_line", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_linha_valor():
  data = request.get_json()
  if data and 'field' in data and 'new_value' in data and 'name_line' in data:
    reference = 'dono' if data['field'] == 'nome' or data['field'] == 'cidade' else 'adm'
    permission = check_permission(data, reference)

    if permission == 'autorizado':
      if data['field'] == 'nome':
        check = Linha.query.filter_by(nome=data['new_value']).first()
        if check and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=check.codigo).first():
          if check.codigo == data['Linha_codigo']:
            return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Você deve definir um nome diferente do atual.'})
          return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Já existe uma linha cadastrada com este nome. Por favor, escolha um nome diferente para prosseguir.'})
        
      elif data['field'] == 'cidade':
        if not data['new_value'] in cidades:
          return jsonify({'error': True, 'title': 'Edição Interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})
      
      linha = Linha.query.filter_by(codigo=data['Linha_codigo']).first()
      if linha and hasattr(linha, data['field']):
        if data['field'] != 'codigo':
          try:
            setattr(linha, data['field'], data['new_value'])
            db.session.commit()
            return jsonify({'error': False, 'title': 'Alteração Concluída', 'text': ''})
          
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao modificar a linha: {str(e)}')
    
    elif permission == 'senha incorreta':
      return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'}) 


@app.route("/edit_vehicle", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_vehicle():
  data = request.get_json()
  if data and 'field' in data and 'new_value' in data and 'name_line' in data and 'surname' in data:
    field = data['field']; new_value = data['new_value']
    not_modify = ['id', 'Linha_codigo', 'Motorista_id']

    if field and field not in not_modify and new_value and data['surname']:
      linha = Linha.query.filter_by(nome=data['name_line']).first()
      code_line = linha.codigo if linha else None

      relationship = return_relationship(code_line)
      vehicle = Onibus.query.filter_by(Linha_codigo=code_line, apelido=data['surname']).first() if relationship else False

      if vehicle:
        if relationship == 'membro':
          if field == 'motorista':
            if vehicle.Motorista_id:
              if vehicle.Motorista_id == current_user.primary_key and new_value == 'Nenhum':
                try:
                  vehicle.Motorista_id = None
                  db.session.commit()
                  return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você não possui mais relação com <strong>{vehicle.apelido}</strong>.'}) 
                
                except Exception as e:
                  db.session.rollback()
                  print(f'Erro ao editar o veículo: {str(e)}')
            else:
              user = return_my_user()
              if user and new_value == user.nome:
                if Onibus.query.filter_by(Linha_codigo=code_line, Motorista_id=current_user.primary_key).first():
                  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                
                try:
                  vehicle.Motorista_id = current_user.primary_key
                  db.session.commit()
                  return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você foi definido como condutor de <strong>{vehicle.apelido}</strong>.'})
                
                except Exception as e:
                  db.session.rollback()
                  print(f'Erro ao editar o veículo: {str(e)}')
        else:
          user = return_my_user()
          if user:
            if field == 'motorista':
              motorista = None
              if new_value != 'Nenhum':
                subquery = db.session.query(Membro.Motorista_id).filter(
                  Membro.Linha_codigo == code_line
                ).subquery()

                motorista = db.session.query(Motorista).filter(
                  db.and_(
                    Motorista.nome == new_value,
                    Motorista.id.in_(subquery.select())
                  )
                ).all()

                if not motorista:
                  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})

                if len(motorista) != 1:
                  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'A edição não pôde ser concluída devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
                motorista = motorista[0]

                if Onibus.query.filter_by(Motorista_id=motorista.id, Linha_codigo=code_line).first():
                  if new_value == user.nome:
                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                  return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Identificamos que o(a) motorista selecionado(a) já possui vínculo com outro veículo.'})
                
                new_value = motorista.id
              else: new_value = None

              try:
                vehicle.Motorista_id = new_value
                db.session.commit()
              
                if new_value:
                  if motorista.id == current_user.primary_key:
                    return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você foi definido(a) como condutor(a) de <strong>{vehicle.apelido}</strong>.'})
                  return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'{motorista.nome} foi definido(a) como condutor(a) de <strong>{vehicle.apelido}</strong>.'}) 
                return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'O condutor de <strong>{vehicle.apelido}</strong> foi definido como: <strong>Nenhum</strong>.'}) 
              
              except Exception as e:
                db.session.rollback()
                print(f'Erro ao editar o veículo: {str(e)}')

            elif field == 'capacidade':
              if new_value.isdigit():
                new_value = int(new_value)
                try:
                  vehicle.capacidade = new_value
                  db.session.commit()
                  return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
                
                except Exception as e:
                  db.session.rollback()
                  print(f'Erro ao editar o veículo: {str(e)}')
            
            else:
              if Onibus.query.filter_by(Linha_codigo=code_line, apelido=new_value).first():
                return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Identificamos a existência de um veículo já cadastrado com esse apelido em sua linha. A ação não pôde ser concluída.'})
              
              try:
                vehicle.apelido = new_value
                db.session.commit()
                return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
              
              except Exception as e:
                db.session.rollback()
                print(f'Erro ao editar o veículo: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_point", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_point():
  data = request.get_json()
  if data and 'name_line' in data and 'name_point' in data and 'field' in data and 'new_value' in data:
    not_modify = ['id', 'Linha_codigo']
    if data['field'] not in not_modify:
      permission = check_permission(data)
      if permission == 'autorizado':
        if data['field'] == 'nome':
          data['new_value'] = capitalize(data['new_value'], 'motorista')
          check = Ponto.query.filter_by(Linha_codigo=data['Linha_codigo'], nome=data['new_value']).first()
          if check and not Marcador_Exclusao.query.filter_by(tabela='Ponto', key_item=check.id).first():
            return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Identificamos a existência de um ponto com o mesmo nome já cadastrado em sua linha. A ação não pôde ser concluída.'})

        ponto = Ponto.query.filter_by(Linha_codigo=data['Linha_codigo'], nome=data['name_point']).first()
        if ponto and hasattr(ponto, data['field']):
          try:
            setattr(ponto, data['field'], data['new_value'])
            db.session.commit()
            return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
          
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao editar o ponto: {str(e)}')
  
  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_route", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_route():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data:
    permission = check_permission(data)
    if permission == 'autorizado' and 'field' in data and 'new_value' in data:
      not_modify = ['codigo', 'Linha_codigo', 'em_partida', 'em_retorno']
      field = data['field']
      new_value = data['new_value']
      hr_par = data['time_par']
      hr_ret = data['time_ret']
      surname = data['surname']

      if field and field not in not_modify and new_value and hr_par and hr_ret and surname:
        vehicle = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], apelido=data['surname']).first()
        rota = return_route(data['Linha_codigo'], surname, data['shift'], hr_par, hr_ret, data['pos'])
        
        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

          if field == 'turno':
            if new_value not in turnos:
              return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'O turno definido não está presente entre as opções disponíveis.'})
            
          elif field == 'onibus':
            field = 'Onibus_id'
            if new_value != 'Nenhum':
              new_vehicle = Onibus.query.filter_by(apelido=new_value, Linha_codigo=data['Linha_codigo']).first()
              if not new_vehicle:
                return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Não foi possível identificar um veículo com este apelido em sua linha.'})
              
              elif check_times(new_vehicle.id, [hr_par, hr_ret]):
                return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': f'Identificamos a possibilidade de um conflito de horários nesta rota com outra rota já definida para <strong>{new_value}</strong>. A ação não pôde ser concluída.'})
              
              new_value = new_vehicle.id
            else: new_value = None
          
          elif field == 'horario_partida' or field == 'horario_retorno':
            if check_times(vehicle.id if vehicle else False, [new_value]):
              return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': f'Identificamos a possibilidade de um conflito de horários nesta rota com outra rota já definida para <strong>{vehicle.apelido}</strong>. A ação não pôde ser concluída.'})
          
          if hasattr(rota, field):
            try:
              setattr(rota, field, new_value)
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro na edição da rota: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_relationship-ponto", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_relationship_ponto():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data:
    permission = check_permission(data)
    if permission == 'autorizado' and 'field' in data and 'new_value' in data and 'type' in data and 'name_point' in data:
      field = data['field']
      new_value = data['new_value']
      surname = data['surname']
      shift = data['shift']
      time_par = data['time_par']
      time_ret = data['time_ret']

      if field and field == 'horario_passagem' and new_value and surname and shift and time_par and time_ret:
        rota = return_route(data['Linha_codigo'], surname, shift, time_par, time_ret, data['pos'])
        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
          
          parada = (
            db.session.query(Parada).join(Ponto)
            .filter(db.and_(
              Ponto.nome == data['name_point'],
              Parada.Ponto_id == Ponto.id,
              Parada.Rota_codigo == rota.codigo,
              Parada.tipo == data['type']
            ))
            .first()
          )

          if parada:
            try:
              parada.horario_passagem = new_value
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro na edição da relação do ponto: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_calendar", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_calendar():
  data = request.get_json()
  if data and 'name_line' in data and 'date' in data and 'feriado' in data and 'funcionando' in data:
    permission = check_permission(data)
    date = format_date(data['date'], reverse=True)

    if permission == 'autorizado' and check_valid_datetime(date):
      line = Linha.query.filter_by(codigo=data['Linha_codigo']).first()
      record = Registro_Linha.query.filter_by(Linha_codigo=data['Linha_codigo'], data=date).first()
      if not line.ferias:
        try:
          if not data['funcionando']:
            record.funcionando = False
            if data['feriado']:
              record.feriado = True
            else:
              record.feriado = False
          else:
            record.funcionando = True
            record.feriado = False
          
          db.session.commit()
          return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})

        except Exception as e:
          db.session.rollback()
          print(f'Erro na edição do calendário da linha: {str(e)}')

  return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Auto-save ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_order_stop", methods=['PUT'])
@login_required
@roles_required("motorista")
def edit_order_stop():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data:
    permission = check_permission(data)
    hr_par = data['time_par']
    hr_ret = data['time_ret']
    surname = data['surname']
    shift = data['shift']

    if permission == 'autorizado' and hr_par and hr_ret and surname and shift and 'partida' in data and 'retorno' in data:
      rota = return_route(data['Linha_codigo'], surname, shift, hr_par, hr_ret, data['pos'])
      if rota is not None:
        if rota:
          try:
            for tipo in ['partida', 'retorno']:
              for index, nome in enumerate(data[tipo]):
                parada = (
                  db.session.query(Parada)
                  .join(Ponto)
                  .filter(
                    db.and_(
                      Ponto.nome == nome,
                      Parada.Ponto_id == Ponto.id,
                      Parada.Rota_codigo == rota.codigo,
                      Parada.tipo == tipo
                    )
                  )
                  .first()
                )
                parada.ordem = index + 1
            db.session.commit()
            return jsonify({'error': False})

          except Exception as e:
            db.session.rollback()
            print(f'Erro no salvamento automático da rota: {str(e)}')
  
      return jsonify({'error': True, 'title': 'Erro ao Salvar', 'text': 'Ocorreu um erro inesperado durante o salvamento automático dos dados da sua rota. Implementamos o procedimento padrão de segurança, revertendo as alterações feitas para uma versão anterior estável.'})
    
  return jsonify({'error': False})


@app.route("/edit_aparence", methods=['PUT'])
@login_required
@roles_required("motorista")
def edit_aparence():
  data = request.get_json()
  if data and 'field' in data and 'new_value' in data and 'name_line' in data and 'surname' in data:
    field = data['field']
    new_value = data['new_value']
    permission = check_permission(data)

    if field != 'description':
      if permission == 'autorizado' and field and field != 'Onibus_id' and new_value:
        vehicle = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], apelido=data['surname']).first()
        if vehicle:
          aparence = vehicle.aparencia
          if aparence and hasattr(aparence, field):
            try:
              setattr(aparence, field, new_value)
              db.session.commit()
              return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao editar a aparência: {str(e)}')

      return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})
    
    else:
      if permission == 'autorizado' and new_value:
        vehicle = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], apelido=data['surname']).first()
        if vehicle:
          aparence = vehicle.aparencia
          try:
            aparence.descricao = new_value
            db.session.commit()
            return jsonify({'error': False})
          
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao editar a aparência: {str(e)}')

          return jsonify({'error': True, 'title': 'Erro ao Salvar', 'text': 'Ocorreu um erro inesperado durante o salvamento automático dos dados de seu veículo. Implementamos o procedimento padrão de segurança, revertendo as alterações feitas para uma versão anterior estável.'})
        
      return jsonify({'error': False})
