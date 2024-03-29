from flask_jwt_extended import create_access_token
from flask_apscheduler import APScheduler
from flask_mail import Message
from flask import render_template, url_for
from app import app, mail
from datetime import timedelta
from app.database import *


sched = APScheduler()
sched.init_app(app)


@sched.task('interval', seconds=5)
def teste():
  with app.app_context():
    email = SendEmail.query.first()
    if email:
      data = email.data
      if email.type == 'recuperar':
        user = User.query.filter_by(id=data['id']).first()

        if user:
          check = AccessToken.query.filter_by(User_id=user.id, type='recuperacao', valid=True).first()
          if not check:
            validade = timedelta(minutes=10)
            token = create_access_token(user.id, additional_claims={'dado': data['dado']}, expires_delta=validade)
            register_token = AccessToken(token=token, User_id=user.id)

            msg = Message('Recuperação de Conta - BussTup', recipients=[email.to])
            msg.html = render_template(
              'models/model_email.html',
              url=url_for('recuperar', token=token, _external=True),
              type=email.type,
              nome=data['nome']
            )

            try:
              mail.send(msg)
              db.session.add(register_token)
              db.session.delete(email)
              db.session.commit()
            
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
