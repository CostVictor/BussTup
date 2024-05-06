from flask_security import login_required, roles_required
from flask import request, jsonify
from app.utilities import *
from app.database import *
from app import app


@app.route("/del_line", methods=['POST'])
@login_required
@roles_required("motorista")
def del_line():
  data = request.get_json()
  if data and 'name_line' in data and 'password' in data:
    permission = check_permission(data, permission='dono')

    if permission == 'autorizado':
      linha = Linha.query.filter_by(codigo=data['Linha_codigo']).first()
      try:
        db.session.delete(linha)
        db.session.commit()
        return jsonify({'error': False, 'title': 'Linha Excluída', 'text': f'Esta linha foi excluída e todos os registros associados foram apagados. Você será redirecionado(a) para a página principal.'})
      
      except Exception as e:
        db.session.rollback()
        print(f'Erro ao remover o veículo: {str(e)}')
    
    elif permission == 'senha incorreta':
      return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})
      
  return jsonify({'error': True, 'title': 'Exclusão Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir a linha.'})


@app.route("/del_myPoint_fixed/<type>", methods=['DELETE'])
@login_required
@roles_required("aluno")
def del_myPoint_fixed(type):
  user = return_my_user()

  if user and type:
    passagem = (
      db.session.query(Passagem).join(Parada)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == True,
        Passagem.passagem_contraturno == False,
        Parada.tipo == type
      ))
      .first()
    )
    
    if passagem:
      try:
        db.session.delete(passagem)
        db.session.commit()
        return jsonify({'error': False, 'title': 'Remoção Concluída', 'text': ''})

      except Exception as e:
        db.session.rollback()
        print(f'Erro ao remover a passagem: {str(e)}')

  return jsonify({'error': True, 'title': 'Remoção Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir a passagem.'})


@app.route("/del_myPoint_contraturno", methods=['DELETE'])
@login_required
@roles_required("aluno")
def del_myPoint_contraturno():
  user = return_my_user()
  if user:
    passagem = (
      Passagem.query.filter_by(
        Aluno_id=user.id,
        passagem_fixa=True,
        passagem_contraturno=True
      )
      .first()
    )

    if passagem:
      try:
        db.session.delete(passagem)
        db.session.commit()
        return jsonify({'error': False, 'title': 'Remoção Concluída', 'text': ''})

      except Exception as e:
        db.session.rollback()
        print(f'Erro ao remover a passagem: {str(e)}')

  return jsonify({'error': True, 'title': 'Remoção Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir a passagem.'})


@app.route("/del_vehicle/<name_line>/<surname>", methods=['DELETE'])
@login_required
@roles_required("motorista")
def del_vehicle(name_line, surname):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relationship = return_relationship(linha.codigo)
    if relationship and relationship != 'membro':
      veiculo = Onibus.query.filter_by(Linha_codigo=linha.codigo, apelido=surname).first()
      if veiculo:
        try:
          db.session.delete(veiculo)
          db.session.commit()
          return jsonify({'error': False, 'title': 'Veículo Excluído', 'text': f'Todos registros relacionados a <strong>{surname}</strong> foram excluídos.'})
        
        except Exception as e:
          db.session.rollback()
          print(f'Erro ao remover o veículo: {str(e)}')

  return jsonify({'error': True, 'title': 'Exclusão Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir o veículo.'})


@app.route("/del_point/<name_line>/<name_point>", methods=['DELETE'])
@login_required
@roles_required("motorista")
def del_point(name_line, name_point):
  linha = Linha.query.filter_by(nome=name_line).first()
  if linha:
    relationship = return_relationship(linha.codigo)
    if relationship and relationship != 'membro':
      ponto = Ponto.query.filter_by(nome=name_point, Linha_codigo=linha.codigo).first()
      if ponto:
        try:
          db.session.delete(ponto)
          db.session.commit()
          return jsonify({'error': False, 'title': 'Ponto Excluído', 'text': f'Todos registros relacionados a <strong>{name_point.capitalize()}</strong> foram excluídos.'})
        
        except Exception as e:
          db.session.rollback()
          print(f'Erro ao remover o veículo: {str(e)}')

  return jsonify({'error': True, 'title': 'Exclusão Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir o ponto.'})


@app.route("/del_route", methods=['POST'])
@login_required
@roles_required("motorista")
def del_route():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data and 'password' in data:
    permission = check_permission(data)
    hr_par = data['time_par']; hr_ret = data['time_ret']
    surname = data['surname']

    if permission == 'autorizado':
      if hr_par and hr_ret and surname:
        rota = return_route(data['Linha_codigo'], surname, data['shift'], hr_par, hr_ret, data['pos'])

        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
            
          try:
            db.session.delete(rota)
            db.session.commit()

            return jsonify({'error': False, 'title': 'Rota Excluída', 'text': f'Todas as relações com veículos, pontos e vínculos de alunos relacionados a esta rota foram excluídos.'})
          
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao excluir a rota: {str(e)}')
    
    elif permission == 'senha incorreta':
      return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})
  
  return jsonify({'error': True, 'title': 'Exclusão Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar excluir a rota.'})


@app.route("/del_relationship_point_route/<name_line>/<surname>/<shift>/<hr_par>/<hr_ret>/<type>/<name_point>", methods=['DELETE'])
@login_required
@roles_required("motorista")
def del_relationship_point_route(name_line, surname, shift, hr_par, hr_ret, type, name_point):
  pos = request.args.get('pos')
  if name_line and surname and shift and hr_par and hr_ret and type and name_point:
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
      relationship = return_relationship(linha.codigo)
      if relationship and relationship != 'membro':
        rota = return_route(linha.codigo, surname, shift, hr_par, hr_ret, pos)
        if rota is not None:
          if not rota:
            return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

          parada = (
            db.session.query(Parada).join(Ponto)
            .filter(db.and_(
              Parada.tipo == type,
              Parada.Rota_codigo == rota.codigo,
              Parada.Ponto_id == Ponto.id,
              Ponto.nome == name_point
            ))
            .first()
          )

          if parada:
            try:
              db.session.delete(parada)
              with db.session.begin_nested():
                paradas = (
                  Parada.query.filter_by(Rota_codigo=rota.codigo, tipo=type)
                  .order_by(Parada.ordem)
                  .all()
                )

                for index, value in enumerate(paradas):
                  value.ordem = index + 1
              db.session.commit()

              return jsonify({'error': False, 'title': 'Relação Removida', 'text': f'Todos os registros relacionados a <strong>{type.capitalize()} ~> {name_point}</strong> foram excluídos.'})
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao remover o veículo: {str(e)}')

  return jsonify({'error': True, 'title': 'Remoção Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar remover a relação do ponto.'})


@app.route("/del_pass_daily", methods=['POST'])
@login_required
@roles_required("aluno")
def del_pass_daily():
  data = request.get_json()
  if data and 'name_line' in data and 'surname' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data and 'date' in data and 'type' in data and 'name_point' in data:
    linha = Linha.query.filter_by(nome=data['name_line']).first()
    user = return_my_user()

    hr_par = data['time_par']; hr_ret = data['time_ret']
    surname = data['surname']; shift = data['shift']
    date_ = format_date(data['date'], reverse=True)
    
    if linha and user and hr_par and hr_ret and surname and shift:
      route = return_route(linha.codigo, surname, shift, hr_par, hr_ret, data['pos'])
      if route is not None:
        if not route:
          return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
        
        pass_daily = (
          db.session.query(Parada, Passagem).join(Ponto)
          .filter(db.and_(
            Ponto.nome == data['name_point'],
            Parada.Ponto_id == Ponto.id,
            Parada.tipo == data['type'],
            Parada.Rota_codigo == route.codigo,
            Passagem.Parada_codigo == Parada.codigo,
            Passagem.Aluno_id == user.id,
            Passagem.passagem_fixa == False,
            Passagem.data == date_,
            db.not_(db.or_(
              Passagem.migracao_lotado == True,
              Passagem.migracao_manutencao == True
            ))
          ))
          .first()
        )

        if pass_daily:
          parada, passagem = pass_daily
          if check_valid_datetime(date_, parada.horario_passagem):
            try:
              db.session.delete(passagem)
              db.session.commit()
              return jsonify({'error': False, 'title': 'Diária Removida', 'text': f''})

            except Exception as e:
              db.session.rollback()
              print(f'Erro ao remover a diária: {str(e)}')

  return jsonify({'error': True, 'title': 'Remoção Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar remover a diária.'})
