from flask_jwt_extended import create_access_token, decode_token
from flask_apscheduler import APScheduler
from flask_mail import Message
from flask import render_template, url_for
from app import app, mail
from datetime import datetime, timedelta
from app.utilities import return_dates_week, modify_forecast_route
from app.database import *


sched = APScheduler()
sched.init_app(app)


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
          for value in dates:
            for type in ['partida', 'retorno']:
              db.session.add(Registro_Rota(data=value, Rota_codigo=route.codigo, tipo=type))

      db.session.commit()


@sched.task('cron', id='calcular_previsao', day_of_week='sat', hour=1)
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
          modify_forecast_route(route, record, commit=False)
          
      db.session.commit()
