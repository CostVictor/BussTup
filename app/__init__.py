from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os

app = Flask(__name__)

# ~~ Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/busstup'
app.config['SQLALCHEMY_BINDS'] = {
    'db_session': 'mysql+pymysql://root@localhost/busstup_session'
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


# ~~ Security
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECURITY_DEFAULT_REMEMBER_ME'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'auth/login.html'


# ~~ Session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SECURITY_SESSION_SILENT'] = True
app.config['SECURITY_RECOVERABLE'] = True


# ~~ Recovery
app.config['SECURITY_RESET_PASSWORD_WITHIN'] = 900  # 15 minutos
app.config['SECURITY_RESET_PASSWORD_ERROR_VIEW'] = 'auth.forgot_password'
app.config['SECURITY_RESET_PASSWORD_LOGIN_VIEW'] = 'auth.login'
# app.config['SECURITY_RESET_PASSWORD_TEMPLATE'] = ''


# ~~ Cookie
app.config['SESSION_COOKIE_NAME'] = 'btup$session@8401M'
# app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


dias_semana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta')
cursos = ('Agropecuária', 'Informática', 'Manutenção', 'Química')
turnos = ('Matutino', 'Vespertino', 'Noturno')
cidades = ('Apodi',)

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

from app.routes import route_action, route_get, route_stream, route_page
