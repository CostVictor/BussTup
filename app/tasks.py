from flask_jwt_extended import create_access_token, decode_token
from flask_apscheduler import APScheduler
from flask_mail import Message
from flask import render_template, url_for
from app import app, mail
from datetime import datetime, timedelta, date
from app.utilities import *
from sqlalchemy import func
from app.database import *


sched = APScheduler()
sched.init_app(app)


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ Sched Optional ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def enviar_email():
  with app.app_context():
    email = SendEmail.query.first()
    if email:
      data = email.data
      if email.type == 'recuperar':
        user = User.query.filter_by(id=data['id']).first()

        if user:
          check = AccessToken.query.filter_by(User_id=user.id, type='recuperacao').first()
          criar_token = True

          if check:
            try:
              decode_token(check)
              criar_token = False
            except: 
              with db.session.begin_nested():
                try:
                  db.session.delete(check)
                  db.session.commit()

                except Exception as e:
                  db.session.rollback()
                  criar_token = False
                  print(f'Erro ao remover token inválido: {str(e)}')

          if criar_token:
            validade = timedelta(minutes=10)
            token = create_access_token(user.id, additional_claims={'dado': data['dado']}, expires_delta=validade)
            register_token = AccessToken(token=token, User_id=user.id)

            msg = Message('Recuperação de Conta - BussTup', recipients=[email.to])
            msg.html = render_template(
              'models/model_email.html',
              url=url_for('recuperar', token=token, _external=True),
              type=email.type,
              nome=data['nome'],
              dado=data['dado']
            )

            try:
              db.session.delete(email)
              db.session.add(register_token)
              db.session.commit()
              mail.send(msg)
            
            except Exception as e:
              db.session.rollback()
              print(f'Erro ao enviar o email: {str(e)}')

        if not user or check:
          try:
            db.session.delete(email)
            db.session.commit()
          
          except Exception as e:
            db.session.rollback()
            print(f'Erro ao remover email repetido: {str(e)}')
    
    moment = datetime.now() + timedelta(seconds=2)
    sched.add_job('enviar_email', enviar_email, trigger='date', run_date=moment)


'''~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ Sched 00:00 ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~'''

'~~~~ Sat ~~~~'

@sched.task('cron', id='criar_registro_aluno', day_of_week='sat', hour=0)
def criar_registro_aluno():
  with app.app_context():
    dates = return_dates_week()
    not_record = Aluno.query.all()

    if not_record:
      with db.session.begin_nested():
        for user in not_record:
          contraturnos_fixos = (
            db.session.query(Contraturno_Fixo.dia_fixo)
            .filter_by(Aluno_id=user.id).all()
          )
          contraturnos_fixos = [value[0] for value in contraturnos_fixos]

          for value in dates:
            contraturno = (value.weekday() in contraturnos_fixos)
            db.session.add(Registro_Aluno(data=value, Aluno_id=user.id, contraturno=contraturno))
            
      db.session.commit()


@sched.task('cron', id='criar_registro_rota', day_of_week='sat', hour=0)
def criar_registro_rota():
  with app.app_context():
    dates = return_dates_week()
    not_record = Rota.query.all()

    if not_record:
      with db.session.begin_nested():
        for route in not_record:
          for date_ in dates:
            for type_ in ['partida', 'retorno']:
              db.session.add(Registro_Rota(data=date_, Rota_codigo=route.codigo, tipo=type_))

      db.session.commit()


@sched.task('cron', id='criar_calendario_linha', day_of_week='sat', hour=0)
def criar_calendario_linha():
  with app.app_context():
    dates = return_dates_week()
    not_record = Linha.query.all()

    if not_record:
      with db.session.begin_nested():
        for line in not_record:
          for date_ in dates:
            db.session.add(Registro_Linha(Linha_codigo=line.codigo, data=date_))

      db.session.commit()


'~~~~ Every Day ~~~~'

@sched.task('cron', id=None, hour=0, max_instances=30)
def transferir_por_defeito():
  with app.app_context():
    dates = return_dates_week(only_valid=True)
    today = date.today()

    if today in dates:
      data = (
        db.session.query(Manutencao, Migracao)
        .filter(db.and_(
          Migracao.Manutencao_codigo == Manutencao.codigo,
          Manutencao.data_fim.is_(None)
        ))
        .all()
      )
      vehicle_atual = None
      all_students = []

      if data:
        for manutencao, migracao in data:
          vehicle_alvo = Onibus.query.filter_by(id=migracao.onibus_alvo).first()
          line_indis = (
            db.session.query(Linha).join(Registro_Linha)
            .filter(db.and_(
              Registro_Linha.Linha_codigo == Linha.codigo,
              Linha.codigo == vehicle_alvo.Linha_codigo,
              Registro_Linha.data == today,
              db.or_(
                Linha.ferias == True,
                Registro_Linha.funcionando == False
              )
            ))
            .first()
          )

          if not line_indis:
            if not vehicle_atual:
              vehicle_atual = manutencao.onibus

              all_students = [value[0] for value in (
                db.session.query(Passagem.Aluno_id)
                .join(Parada).join(Rota).join(Aluno).join(Registro_Aluno)
                .filter(db.and_(
                  Passagem.Parada_codigo == Parada.codigo,
                  Parada.Rota_codigo == Rota.codigo,
                  Passagem.Aluno_id == Aluno.id,
                  Registro_Aluno.Aluno_id == Aluno.id,
                  Rota.turno == migracao.turno_alvo,
                  Rota.Onibus_id == vehicle_atual.id,
                  db.or_(
                    Aluno.turno == migracao.turno_alvo,
                    db.and_(
                      Passagem.passagem_contraturno == True,
                      Registro_Aluno.contraturno == True,
                      Registro_Aluno.data == today
                    )
                  ),
                  db.not_(db.and_(
                    Registro_Aluno.data == today,
                    Registro_Aluno.faltara == True
                  ))
                ))
                .all()
              )]

            if vehicle_alvo:
              routes_dis = (
                db.session.query(Rota, Registro_Rota)
                .filter(db.and_(
                  Registro_Rota.Rota_codigo == Rota.codigo,
                  Rota.Onibus_id == vehicle_alvo.id,
                  Rota.turno == migracao.turno_alvo,
                  Registro_Rota.previsao_pessoas < vehicle_alvo.capacidade,
                  Registro_Rota.data == today
                ))
                .all()
              )

              for route, record in routes_dis:
                limit_range = vehicle_alvo.capacidade - record.previsao_pessoas
                stops_dis = Parada.query.filter_by(Rota_codigo=route.codigo, tipo=record.tipo).all()

                for stop in stops_dis:
                  if check_valid_datetime(today, stop.horario_passagem, add_limit=0.1):
                    if not limit_range:
                      break

                    combine = datetime.combine(today, stop.horario_passagem)
                    time_ant = combine - timedelta(minutes=15)
                    time_dep = combine + timedelta(minutes=15)

                    not_includes = (
                      db.session.query(Passagem.Aluno_id).join(Parada)
                      .filter(db.and_(
                        Passagem.Parada_codigo == Parada.codigo,
                        Passagem.Aluno_id.in_(all_students),
                        Passagem.passagem_fixa == False,
                        Parada.horario_passagem.between(time_ant.time(), time_dep.time())
                      ))
                      .subquery()
                    )
                    students_dis = (
                      db.session.query(func.distinct(Passagem.Aluno_id))
                      .join(Aluno).join(Registro_Aluno).join(Parada)
                      .filter(db.and_(
                        Passagem.Parada_codigo == Parada.codigo,
                        Passagem.Aluno_id == Aluno.id,
                        Passagem.Aluno_id.in_(all_students),
                        db.not_(Passagem.Aluno_id.in_(not_includes.select())),
                        Registro_Aluno.Aluno_id == Aluno.id,
                        Registro_Aluno.data == today,
                        Parada.Ponto_id == stop.Ponto_id,
                        Parada.tipo == stop.tipo,
                        db.not_(db.or_(
                          db.and_(
                            Aluno.turno == migracao.turno_alvo,
                            Registro_Aluno.contraturno == True,
                            Parada.tipo == return_ignore_route(route.turno)
                          ),
                          db.and_(
                            Aluno.turno != migracao.turno_alvo,
                            db.or_(
                              db.and_(
                                Aluno.turno == 'Matutino',
                                Parada.tipo != 'retorno'
                              ),
                              db.and_(
                                db.or_(
                                  Aluno.turno == 'Vespertino',
                                  Aluno.turno == 'Noturno'
                                ),
                                Parada.tipo != 'partida'
                              )
                            )
                          )
                        )),
                      ))
                      .all()
                    )

                    if students_dis:
                      len_students = len(students_dis)
                      range_ = limit_range if limit_range <= len_students else len_students

                      record.atualizar = True
                      records_atual = (
                        db.session.query(Registro_Rota).join(Rota)
                        .filter(db.and_(
                          Registro_Rota.Rota_codigo == Rota.codigo,
                          Registro_Rota.tipo == stop.tipo,
                          Rota.turno == route.turno,
                          Rota.Onibus_id == vehicle_atual.id
                        ))
                        .all()
                      )
                      for record_atual in records_atual:
                        record_atual.atualizar = True

                      for index in range(range_):
                        db.session.add(Passagem(
                          passagem_fixa=False,
                          passagem_contraturno=False,
                          migracao_manutencao=True,
                          Parada_codigo=stop.codigo,
                          Aluno_id=students_dis[index][0],
                          data=today
                        ))
                        limit_range -= 1
            else:
              db.session.delete(migracao)

          db.session.commit()


'''~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ Sched 01:00 ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~'''

@sched.task('cron', id='calcular_previsao', hour=1)
def calcular_previsao():
  with app.app_context():
    dates = return_dates_week()
    data = (
      db.session.query(Rota, Registro_Rota)
      .filter(db.and_(
        Registro_Rota.Rota_codigo == Rota.codigo,
        Registro_Rota.data.in_(dates)
      ))
      .all()
    )
    if data:
      with db.session.begin_nested():
        for route, record in data:
          reference = route.horario_partida if record.tipo == 'partida' else route.horario_retorno
          if check_valid_datetime(record.data, reference):
            modify_forecast_route(route, record, commit=False)
          else:
            record.atualizar = False
          
      db.session.commit()
