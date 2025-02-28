from flask import Flask
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_mail import Mail
import os

load_dotenv()
app = Flask(__name__)

app.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Database ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_BINDS'] = {
  'db_session': os.getenv("DB_SESSION")
}

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
  'pool_size': 5,
  'max_overflow': 5
}

app.config['SQLALCHEMY_BINDS_OPTIONS'] = {
  'db_session': {
    'pool_size': 5,
    'max_overflow': 2
  }
}


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Security ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SECURITY_DEFAULT_REMEMBER_ME'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'auth/login.html'


'''~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Session ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~'''

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SECURITY_SESSION_SILENT'] = True
app.config['SECURITY_RECOVERABLE'] = True


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Recovery ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

app.config['SECURITY_RESET_PASSWORD_WITHIN'] = 900  # 15 minutos
app.config['SECURITY_RESET_PASSWORD_ERROR_VIEW'] = 'auth.forgot_password'
app.config['SECURITY_RESET_PASSWORD_LOGIN_VIEW'] = 'auth.login'
# app.config['SECURITY_RESET_PASSWORD_TEMPLATE'] = ''


'''~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Email ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~'''

app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


'''~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Cookie ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~'''

app.config['SESSION_COOKIE_NAME'] = os.getenv("SESSION_COOKIE_NAME")
# app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


'''~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ WebToken ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~'''

jwt = JWTManager(app)


'''~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Cheduler ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~'''

app.config['SCHEDULER_API_ENABLED'] = True


'''~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Variable ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~'''

dias_semana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta')
cursos = ('Agropecuária', 'Informática', 'Manutenção', 'Química')
turnos = ('Matutino', 'Vespertino', 'Noturno')
cidades = ('Apodi', 'Campo Grande', 'Caraúbas', 'Felipe Guerra', 'Itaú', 'Rodolfo Fernandes', 'Severiano Melo', 'Umarizal')

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

from app.routes import route_action, route_insert, route_edit, route_get, route_render, route_delete
