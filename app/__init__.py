from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/busstup'
app.config['SQLALCHEMY_BINDS'] = {
    'security_db': 'mysql+pymysql://root@localhost/busstup_security'
}

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'max_overflow': 5   
}

app.config['SQLALCHEMY_BINDS_OPTIONS'] = {
    'security_db': {
        'pool_size': 5,
        'max_overflow': 2
    }
}

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECURITY_DEFAULT_REMEMBER_ME'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'auth/login.html'

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

from app.routes import route_action, route_get, route_stream, route_page
