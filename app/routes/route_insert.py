from flask_security import login_required, roles_required, current_user
from app import app, limiter, cidades, turnos
from flask import request, jsonify
from datetime import date
from app.utilities import *
from app.database import *


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Inserts Site ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/register_user", methods=['POST'])
@limiter.limit('5 per minute')
def cadastrar_usuario():
  info = format_register(request.get_json())
  if info:
    inconsistencia, title, text, data = info
    if inconsistencia:
      return jsonify({'error': True, 'title': title, 'text': text})

    if create_user(data):
      return jsonify({'error': False, 'title': 'Usuário Cadastrado', 'text': ''})
  
  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar realizar o cadastro.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Inserts Line ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/create_line", methods=['POST'])
@login_required
@roles_required("motorista")
def create_line():
  data = request.get_json()

  if data and 'data' in data and 'codigo' not in data:
    data = data['data']

    if 'nome' in data and 'cidade' in data:
      if not data['cidade'] in cidades:
        return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})
      
      linha = Linha.query.filter_by(nome=data['nome']).first()
      if linha:
        if not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
          return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Já existe uma linha com o nome especificado.'})

      data['ferias'] = False
      dates = return_dates_week()
      linha = Linha(**data)
      try:
        db.session.add(linha)
        with db.session.begin_nested():
          for date in dates:
            db.session.add(Registro_Linha(Linha_codigo=linha.codigo, data=date))
            
          relacao = Membro(Linha_codigo=linha.codigo, Motorista_id=current_user.primary_key, dono=True, adm=True)
          db.session.add(relacao)

        db.session.commit()
        return jsonify({'error': False, 'title': 'Linha Cadastrada', 'text': 'Sua linha foi cadastrada e está disponível para utilização. Você foi adicionado(a) como usuário dono.'})

      except Exception as e:
        db.session.rollback()
        print(f'Erro na criação da linha: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a linha.'})


@app.route("/create_vehicle", methods=['POST'])
@login_required
@roles_required("motorista")
def create_vehicle():
  data = request.get_json()
  permission = check_permission(data)
  if permission == 'autorizado' and 'apelido' in data and 'motorista_nome' in data and 'cor' in data and 'modelo' in data and 'descricao' in data:
    motorista_nome = data.pop('motorista_nome')
    verify_surname = Onibus.query.filter_by(apelido=data['apelido'], Linha_codigo=data['Linha_codigo']).first()
    descricao = {
      'cor': data.pop('cor').capitalize(), 
      'modelo': data.pop('modelo').capitalize(), 
      'descricao': data.pop('descricao').capitalize()
    }
    if not descricao['descricao']:
      del descricao['descricao']
    
    if motorista_nome != 'Nenhum':
      subquery = db.session.query(Membro.Motorista_id).filter(Membro.Linha_codigo == data['Linha_codigo']).subquery()
      motorista_id = db.session.query(Motorista.id).filter(
        db.and_(
          Motorista.nome == motorista_nome,
          Motorista.id.in_(subquery.select())
        )
      ).all()
      
      if not verify_surname:
        if motorista_id and len(motorista_id) == 1:
          data['Motorista_id'] = motorista_id[0].id
          check_not_dis = Onibus.query.filter_by(Motorista_id=data['Motorista_id'], Linha_codigo=data['Linha_codigo']).first()

          report = False
          if check_not_dis:
            del data['Motorista_id']
            report = True

          onibus = Onibus(**data)
          try:
            db.session.add(onibus)
            with db.session.begin_nested():
              aparencia = Aparencia(**descricao, Onibus_id=onibus.id)
              db.session.add(aparencia)
            db.session.commit()

            if report:
              if motorista_id[0].id == current_user.primary_key:
                return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'Ao realizar o cadastro, identificamos que você já possui vínculo com outro veículo nesta linha. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
              
              return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'Ao realizar o cadastro, identificamos que o(a) motorista <strong>{motorista_nome}</strong> já possui vínculo com outro veículo. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
            
            if onibus.Motorista_id == current_user.primary_key:
              return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'O veículo foi adicionado e está disponível para utilização. Você foi definido(a) como condutor(a).'})
            
            return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'O veículo foi adicionado e está disponível para utilização. <strong>{motorista_nome}</strong> foi definido(a) como condutor(a).'})
            
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao criar o veículo: {str(e)}')
        else:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'O cadastro não pôde ser concluído devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
      else:
        return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos a existência de um veículo já cadastrado com esse apelido em sua linha. Por favor, escolha um apelido diferente.'})
    else:
      if not verify_surname:
        onibus = Onibus(**data)

        try:
          db.session.add(onibus)
          with db.session.begin_nested():
            aparencia = Aparencia(**descricao, Onibus_id=onibus.id)
            db.session.add(aparencia)
          db.session.commit()

          return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': 'O veículo foi adicionado e está disponível para utilização. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
        
        except Exception as e:
          db.session.rollback()
          print(f'Erro ao criar o veículo: {str(e)}')
      else:
        return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos a existência de um veículo já cadastrado com esse apelido em sua linha. Por favor, escolha um apelido diferente.'})

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o veículo.'})   


@app.route("/create_point", methods=['POST'])
@login_required
@roles_required("motorista")
def create_point():
  data = request.get_json()
  if data and 'name_point' in data and 'name_line' in data and 'id' not in data and 'nome' not in data:
    permission = check_permission(data)
    if permission == 'autorizado':
      data['nome'] = capitalize(data.pop('name_point'), 'motorista')

      ponto_check = Ponto.query.filter_by(nome=data['nome'], Linha_codigo=data['Linha_codigo']).first()
      if ponto_check:
        if not Marcador_Exclusao.query.filter_by(tabela='Ponto', key_item=ponto_check.id).first():
          return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos que já existe um ponto com esse nome em sua linha. A ação não pôde ser concluída.'})

      ponto = Ponto(**data)
      try:
        db.session.add(ponto)
        db.session.commit()

        return jsonify({'error': False, 'title': 'Ponto Cadastrado', 'text': f'<strong>{ponto.nome}</strong> foi cadastrado com sucesso.'})
      
      except Exception as e:
        db.session.rollback()
        print(f'Erro ao criar o ponto: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o ponto.'})


@app.route("/create_route", methods=['POST'])
@login_required
@roles_required("motorista")
def create_route():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'turno' in data and 'codigo' not in data:
    permission = check_permission(data)
    if permission == 'autorizado' and 'horario_partida' in data and 'horario_retorno' in data:
      vehicle = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], apelido=data.pop('surname')).first()
      dates = return_dates_week()
      today = date.today()

      if vehicle:
        data['Onibus_id'] = vehicle.id
        hr_par = data['horario_partida']
        hr_ret = data['horario_retorno']

        if data['turno'] not in turnos:
          return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'O turno definido não está presente entre as opções disponíveis.'})

        if check_times(vehicle.id, time=[hr_par, hr_ret]):
          return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': f'Identificamos a possibilidade de um conflito de horários nesta rota com outra rota já definida para <strong>{vehicle.apelido}</strong>. A ação não pôde ser concluída.'})

        rota = Rota(**data)
        try:
          db.session.add(rota)
          with db.session.begin_nested():
            for value in dates:
              atualizar = (value >= today)
              for type in ['partida', 'retorno']:
                db.session.add(Registro_Rota(
                  Rota_codigo=rota.codigo, data=value, tipo=type, atualizar=atualizar
                ))

          db.session.commit()

          return jsonify({'error': False, 'title': 'Rota Cadastrada', 'text': f'A rota foi adicionada para o veículo: <strong>{vehicle.apelido}</strong>.'})
        except Exception as e:
          db.session.rollback()
          print(f'Erro ao criar a rota: {str(e)}')

      else:
        rota = Rota(**data)
        try:
          db.session.add(rota)
          with db.session.begin_nested():
            for value in dates:
              atualizar = (value >= today)
              for type in ['partida', 'retorno']:
                db.session.add(Registro_Rota(
                  Rota_codigo=rota.codigo, data=value, tipo=type, atualizar=atualizar
                ))

          db.session.commit()

          return jsonify({'error': False, 'title': 'Rota Cadastrada', 'text': 'A rota foi adicionada à sua linha como desativada e não estará visível para os alunos até que um veículo seja definido. Manteremos esta rota em um local reservado para que você possa configurá-la.'})
        except Exception as e:
          db.session.rollback()
          print(f'Erro ao criar a rota: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a rota.'})


@app.route("/create_stop", methods=['POST'])
@login_required
@roles_required("motorista")
def create_stop():
  data = request.get_json()
  if data and 'name_line' in data and 'name_point' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data and 'type' in data:
    permission = check_permission(data)
    hr_par = data['time_par']; hr_ret = data['time_ret']
    surname = data['surname']; tipo = data['type']
    dis = ['partida', 'retorno']

    if permission == 'autorizado' and tipo in dis and hr_par and hr_ret and surname:
      rota = return_route(data['Linha_codigo'], surname, data['shift'], hr_par, hr_ret, data['pos'])

      if rota is not None:
        if not rota:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
        
        ponto = Ponto.query.filter_by(nome=data['name_point'], Linha_codigo=data['Linha_codigo']).first()
        if ponto:
          if Parada.query.filter_by(tipo=tipo, Rota_codigo=rota.codigo, Ponto_id=ponto.id).first():
            return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': f'Identificamos que este ponto já está presente no trajeto de <strong>{tipo.capitalize()}</strong>. A ação não pôde ser concluída.'})

          if 'time_pas' in data:
            contagem_partida = 0
            contagem_retorno = 0
            for parada in rota.paradas:
              if parada.tipo == 'partida':
                contagem_partida += 1
              else: contagem_retorno += 1

            data_parada = {
              'Rota_codigo': rota.codigo,
              'Ponto_id': ponto.id,
              'horario_passagem': data['time_pas'],
              'ordem': (contagem_partida + 1) if tipo == 'partida' else (contagem_retorno + 1),
              'tipo': tipo
            }
            parada = Parada(**data_parada)
            text = f'<strong>{ponto.nome}</strong> foi adicionado ao trajeto de <strong>{tipo.capitalize()}</strong> como último ponto da ordem. Por favor, verifique se esta configuração está correta.'

            parada_2 = False
            if 'time_pas_2' in data:
              data_parada['horario_passagem'] = data['time_pas_2']
              data_parada['tipo'] = [tipo for tipo in dis if tipo != data_parada['tipo']][0]
              data_parada['ordem'] = (contagem_partida + 1) if data_parada['tipo'] == 'partida' else (contagem_retorno + 1)

              if not Parada.query.filter_by(tipo=data_parada['tipo'], Rota_codigo=rota.codigo, Ponto_id=ponto.id).first():
                parada_2 = Parada(**data_parada)
                text = f'<strong>{ponto.nome}</strong> foi adicionado aos dois trajetos como os últimos pontos na ordem. Por favor, verifique se essas configurações estão corretas.'
              else:
                text = f'<strong>{ponto.nome}</strong> foi adicionado apenas no trajeto <strong>{parada.tipo.capitalize()}</strong> devido a ele já estar presente no trajeto <strong>{data_parada["tipo"]}</strong>. Por favor, verifique se a configuração da ordem está correta.'

            try:
              db.session.add(parada)
              if parada_2:
                db.session.add(parada_2)
              db.session.commit()
              return jsonify({'error': False, 'title': 'Ponto Adicionado', 'text': text})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao criar parada: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a parada.'})


@app.route("/create_pass_fixed", methods=['POST'])
@login_required
@roles_required("aluno")
def create_pass_fixed():
  data = request.get_json()
  if data and 'name_line' in data and 'name_point' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data and 'type' in data:
    linha = Linha.query.filter_by(nome=data['name_line']).first()
    user = return_my_user()

    hr_par = data['time_par']; hr_ret = data['time_ret']
    surname = data['surname']; tipo = data['type'].lower()
    shift = data['shift']
    dis = ['partida', 'retorno']
    
    if linha and user and hr_par and hr_ret and surname and shift and tipo in dis:
      route = return_route(linha.codigo, surname, shift, hr_par, hr_ret, data['pos'])
      if route is not None and shift.capitalize() == user.turno:
        if not route:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

        dates = return_dates_week(only_valid=True)
        dates_contraturno = (
          db.session.query(Registro_Aluno.data)
          .filter(db.and_(
            Registro_Aluno.Aluno_id == user.id,
            Registro_Aluno.contraturno == True,
            Registro_Aluno.data.in_(dates)
          ))
          .all()
        )
        records = (
          db.session.query(Registro_Rota)
          .filter(db.and_(
            Registro_Rota.Rota_codigo == route.codigo,
            Registro_Rota.tipo == tipo,
            Registro_Rota.data.in_(dates)
          ))
          .all()
        )

        dis.remove(tipo)
        reverse = dis[0]
        check_passagem = (
          db.session.query(Passagem).join(Parada)
          .filter(db.and_(
            Parada.tipo == tipo,
            Passagem.Parada_codigo == Parada.codigo,
            Passagem.Aluno_id == user.id,
            Passagem.passagem_fixa == True,
            Passagem.passagem_contraturno == False
          ))
          .first()
        )
        parada = (
          db.session.query(Parada).join(Ponto)
          .filter(db.and_(
            Ponto.nome == data['name_point'],
            Parada.Ponto_id == Ponto.id,
            Parada.Rota_codigo == route.codigo,
            Parada.tipo == tipo
          ))
          .first()
        )

        if parada:
          info = {
            'passagem_fixa': True,
            'passagem_contraturno': False,
            'Parada_codigo': parada.codigo,
            'Aluno_id': user.id
          }

          new_passagem = Passagem(**info)
          if check_passagem:
            parada_atual = check_passagem.parada
            rota_atual = parada_atual.rota
            if rota_atual.codigo == route.codigo:
              ponto_atual = parada_atual.ponto

              if ponto_atual.nome != data['name_point']:
                try:
                  db.session.delete(check_passagem)
                  with db.session.begin_nested():
                    db.session.add(new_passagem)
                  db.session.commit()

                  return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': f'Você trocou seu ponto fixo de <strong>{tipo.capitalize()}</strong>. Certifique-se de possuir um cadastro de <strong>{reverse.capitalize()}</strong>, caso não possua.'})
                
                except Exception as e:
                  db.session.rollback()
                  print(f'Erro ao criar a passagem: {str(e)}')
            
            else:
              code_line = rota_atual.linha.codigo
              passagens = (
                db.session.query(Passagem)
                .filter(db.and_(
                  Passagem.passagem_fixa == True,
                  (Passagem.passagem_contraturno == False) if linha.codigo == code_line else True,
                  Passagem.Aluno_id == user.id
                ))
                .all()
              )

              check_veicle = (rota_atual.onibus.id != route.onibus.id)
              rotas_migracoes = []
              if linha.codigo != code_line or check_veicle:
                migracoes = (
                  db.session.query(Passagem, Parada, Rota)
                  .filter(db.and_(
                    db.or_(
                      Passagem.migracao_lotado == True,
                      Passagem.migracao_manutencao == True
                    ),
                    Passagem.Aluno_id == user.id,
                    Passagem.Parada_codigo == Parada.codigo,
                    Parada.Rota_codigo == Rota.codigo
                  ))
                  .all()
                )
                for migracao, _, rota in migracoes:
                  if migracao.data.in_(dates):
                    rotas_migracoes.append(rota.codigo)
                  db.session.delete(migracao)

              route_contraturno = [passagem.parada.rota.codigo for passagem in passagens if passagem.passagem_contraturno]
              records_ant = (
                db.session.query(Registro_Rota)
                .filter(db.and_(
                  (
                    (Registro_Rota.Rota_codigo == rota_atual.codigo) 
                    if linha.codigo == code_line 
                    else db.or_(
                      db.and_(
                        db.or_(
                          Registro_Rota.Rota_codigo == rota_atual.codigo,
                          Registro_Rota.Rota_codigo.in_(rotas_migracoes)
                        ),
                        db.not_(db.and_(
                          Registro_Rota.tipo == return_ignore_route(user.turno),
                          Registro_Rota.data.in_(dates_contraturno)
                        ))
                      ),
                      db.and_(
                        Registro_Rota.Rota_codigo == route_contraturno[0],
                        Registro_Rota.tipo == return_ignore_route(user.turno),
                        Registro_Rota.data.in_(dates_contraturno)
                      ) if route_contraturno else False
                    )
                  ),
                  Registro_Rota.data.in_(dates)
                ))
                .all()
              )

              try:
                for passagem in passagens:
                  db.session.delete(passagem)

                with db.session.begin_nested():
                  db.session.add(new_passagem)
                
                for record in records + records_ant:
                  set_update_record_route(record)
                db.session.commit()

                if linha.codigo == code_line:
                  return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': f'Você trocou seu ponto fixo de <strong>{tipo.capitalize()}</strong> para esta rota; suas relações fixas na rota anterior foram removidas. Certifique-se de possuir um cadastro de <strong>{reverse.capitalize()}</strong> nesta rota.'})

                return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': f'Você trocou seu ponto fixo de <strong>{tipo.capitalize()}</strong> para esta rota; esta linha foi definida como sua linha atual, e todos os vínculos com a linha anterior foram removidos. Certifique-se de possuir um cadastro de <strong>{reverse.capitalize()}</strong> nesta nova rota.'})

              except Exception as e:
                db.session.rollback()
                print(f'Erro ao criar a passagem: {str(e)}')
          
          else:
            check_passagem = (
              db.session.query(Passagem).join(Parada)
              .filter(db.and_(
                Parada.tipo == reverse,
                Passagem.Parada_codigo == Parada.codigo,
                Passagem.Aluno_id == user.id,
                Passagem.passagem_fixa == True,
                Passagem.passagem_contraturno == False
              ))
              .first()
            )
            text = f'Você definiu seu ponto fixo de <strong>{tipo.capitalize()}</strong>. Certifique-se de possuir um cadastro de <strong>{reverse.capitalize()}</strong>, caso não possua.'

            try:
              if check_passagem:
                rota_check = check_passagem.parada.rota
                if rota_check.codigo != route.codigo:
                  check_veicle = (rota_check.onibus.id != route.onibus.id)
                  rotas_migracoes = []
                  if rota_check.linha.codigo != linha.codigo or check_veicle:
                    migracoes = (
                      db.session.query(Passagem, Parada, Rota)
                      .filter(db.and_(
                        db.or_(
                          Passagem.migracao_lotado == True,
                          Passagem.migracao_manutencao == True
                        ),
                        Passagem.Aluno_id == user.id,
                        Passagem.Parada_codigo == Parada.codigo,
                        Parada.Rota_codigo == Rota.codigo
                      ))
                      .all()
                    )
                    for migracao, _, rota in migracoes:
                      if migracao.data.in_(dates):
                        rotas_migracoes.append(rota.codigo)
                      db.session.delete(migracao)

                  record_ant_fixed = (
                    db.session.query(Registro_Rota)
                    .filter(db.and_(
                      db.or_(
                        Registro_Rota.Rota_codigo == rota_check.codigo,
                        Registro_Rota.Rota_codigo.in_(rotas_migracoes)
                      ),
                      db.not_(db.and_(
                        Registro_Rota.tipo == return_ignore_route(user.turno),
                        Registro_Rota.data.in_(dates_contraturno)
                      )),
                      Registro_Rota.data.in_(dates)
                    ))
                    .all()
                  )
                  for record in record_ant_fixed:
                    set_update_record_route(record)

                  if rota_check.linha.codigo != linha.codigo:
                    contraturno = (
                      Passagem.query.filter_by(
                        Aluno_id=user.id,
                        passagem_fixa=True,
                        passagem_contraturno=True
                      )
                      .first()
                    )

                    if contraturno:
                      record_ant_contraturno = (
                        db.session.query(Registro_Rota)
                        .filter(db.and_(
                          Registro_Rota.Rota_codigo == contraturno.parada.rota.codigo,
                          Registro_Rota.tipo == return_ignore_route(user.turno),
                          Registro_Rota.data.in_(dates_contraturno)
                        ))
                        .all()
                      )
                      for record in record_ant_contraturno:
                        set_update_record_route(record)
                      db.session.delete(contraturno)

                    text = f'Você definiu seu ponto fixo de <strong>{tipo.capitalize()}</strong> em outra linha; todas os seus vínculos com a linha anterior foram removidos. Defina seu novo ponto de <strong>{reverse.capitalize()}</strong> e <strong>Contraturno</strong> nesta nova linha.'
                  else:
                    text = f'Você definiu seu ponto fixo de <strong>{tipo.capitalize()}</strong> em outra rota; seu ponto de <strong>{reverse.capitalize()}</strong> na rota anterior foi removido.'
                  
                  db.session.delete(check_passagem)

              db.session.add(new_passagem)
              for record in records:
                set_update_record_route(record)

              db.session.commit()
              return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': text})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao criar a passagem: {str(e)}')
    
  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a passagem na rota.'})


@app.route("/create_pass_contraturno", methods=['POST'])
@login_required
@roles_required("aluno")
def create_pass_contraturno():
  data = request.get_json()
  if data and 'name_line' in data and 'name_point' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'type' in data and 'pos' in data:
    linha = Linha.query.filter_by(nome=data['name_line']).first()
    user = return_my_user()

    hr_par = data['time_par']; hr_ret = data['time_ret']
    surname = data['surname']; tipo = data['type'].lower()
    shift = data['shift']

    dis = ['partida', 'retorno']
    if user.turno != 'Noturno':
      dis.remove('partida' if user.turno == 'Matutino' else 'retorno')
    
    if linha and user and hr_par and hr_ret and surname and shift and tipo in dis:
      route = return_route(linha.codigo, surname, shift, hr_par, hr_ret, data['pos'])
      if route is not None and shift.capitalize() != user.turno:
        if not route:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

        dates = return_dates_week(only_valid=True)
        dates_contraturno = (
          db.session.query(Registro_Aluno.data)
          .filter(db.and_(
            Registro_Aluno.Aluno_id == user.id,
            Registro_Aluno.contraturno == True,
            Registro_Aluno.data.in_(dates)
          ))
          .all()
        )
        
        check_passagem = (
          Passagem.query.filter_by(
            passagem_fixa=True,
            passagem_contraturno=True,
            Aluno_id=user.id
          )
          .first()
        )
        parada = (
          db.session.query(Parada).join(Ponto)
          .filter(db.and_(
            Ponto.nome == data['name_point'],
            Parada.Ponto_id == Ponto.id,
            Parada.Rota_codigo == route.codigo,
            Parada.tipo == tipo
          ))
          .first()
        )

        if parada:
          info = {
            'passagem_fixa': True,
            'passagem_contraturno': True,
            'Parada_codigo': parada.codigo,
            'Aluno_id': user.id
          }

          new_contraturno = Passagem(**info)
          if check_passagem:
            rota_atual = check_passagem.parada.rota
            linha_atual = rota_atual.linha.codigo

            if linha_atual == linha.codigo:
              records = (
                db.session.query(Registro_Rota)
                .filter(db.and_(
                  db.or_(
                    Registro_Rota.Rota_codigo == route.codigo,
                    Registro_Rota.Rota_codigo == rota_atual.codigo
                  ),
                  Registro_Rota.tipo == return_ignore_route(user.turno),
                  Registro_Rota.data.in_(dates_contraturno)
                ))
                .all()
              )
              try:
                for record in records:
                  set_update_record_route(record)

                db.session.delete(check_passagem)
                with db.session.begin_nested():
                  db.session.add(new_contraturno)
                db.session.commit()

                return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': f'Você trocou seu ponto de contraturno.'})
              
              except Exception as e:
                db.session.rollback()
                print(f'Erro ao criar a passagem: {str(e)}')
            
            else:
              passagens = (
                db.session.query(Passagem)
                .filter(db.and_(
                  Passagem.Aluno_id == user.id,
                  db.or_(
                    Passagem.passagem_fixa == True,
                    Passagem.migracao_lotado == True,
                    Passagem.migracao_manutencao == True
                  )
                ))
                .all()
              )

              route_fixed = [
                passagem.parada.rota.codigo for passagem in passagens 
                if passagem.passagem_fixa or 
                (passagem.data in dates and (passagem.migracao_lotado or passagem.migracao_manutencao))
              ]
              records = (
                db.session.query(Registro_Rota)
                .filter(db.and_(
                  db.or_(
                    db.and_(
                      Registro_Rota.tipo == return_ignore_route(user.turno),
                      Registro_Rota.data.in_(dates_contraturno),
                      db.or_(
                        Registro_Rota.Rota_codigo == route.codigo,
                        Registro_Rota.Rota_codigo == rota_atual.codigo
                      )
                    ),
                    db.and_(
                      Registro_Rota.Rota_codigo.in_(route_fixed),
                      db.not_(db.and_(
                        Registro_Rota.tipo == return_ignore_route(user.turno),
                        Registro_Rota.data.in_(dates_contraturno)
                      ))
                    )
                  ),
                  Registro_Rota.data.in_(dates)
                ))
                .all()
              )
              try:
                for record in records:
                  set_update_record_route(record)

                for passagem in passagens:
                  db.session.delete(passagem)

                with db.session.begin_nested():
                  db.session.add(new_contraturno)
                db.session.commit()

                return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': f'Você trocou seu ponto de contraturno para esta linha. Todos os vínculos com a linha anterior foram removidos. Certifique-se de configurar sua rota fixa.'})
              
              except Exception as e:
                db.session.rollback()
                print(f'Erro ao criar a passagem: {str(e)}')

          else:
            check_passagem = (
              db.session.query(Rota, Parada, Passagem)
              .filter(db.and_(
                Passagem.Aluno_id == user.id,
                Passagem.passagem_fixa == True,
                Passagem.Parada_codigo == Parada.codigo,
                Parada.Rota_codigo == Rota.codigo,
                Rota.Linha_codigo != linha.codigo,
              ))
              .all()
            )
            try:
              route_fixed = []
              if check_passagem:
                for rota, _, passagem in check_passagem:
                  route_fixed.append(rota.codigo)
                  db.session.delete(passagem)
                
                migracoes = (
                  db.session.query(Rota, Parada, Passagem)
                  .filter(db.and_(
                    Passagem.Aluno_id == user.id,
                    Passagem.Parada_codigo == Parada.codigo,
                    Parada.Rota_codigo == Rota.codigo,
                    db.or_(
                      Passagem.migracao_lotado == True,
                      Passagem.migracao_manutencao == True
                    )
                  ))
                  .all()
                )

                for rota, _, migracao in migracoes:
                  route_fixed.append(rota.codigo)
                  db.session.delete(migracao)
              
              records = (
                db.session.query(Registro_Rota)
                .filter(db.and_(
                  db.or_(
                    db.and_(
                      Registro_Rota.tipo == return_ignore_route(user.turno),
                      Registro_Rota.data.in_(dates_contraturno),
                      Registro_Rota.Rota_codigo == route.codigo
                    ),
                    db.and_(
                      Registro_Rota.Rota_codigo.in_(route_fixed),
                      db.not_(db.and_(
                        Registro_Rota.tipo == return_ignore_route(user.turno),
                        Registro_Rota.data.in_(dates_contraturno)
                      ))
                    )
                  ),
                  Registro_Rota.data.in_(dates)
                ))
                .all()
              )
              for record in records:
                set_update_record_route(record)
              db.session.add(new_contraturno)

              db.session.commit()
              return jsonify({'error': False, 'title': 'Cadastro Efetuado', 'text': ''})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao criar a passagem: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a passagem na rota.'})
