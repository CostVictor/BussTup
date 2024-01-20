from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/busstup'
app.config['SQLALCHEMY_BINDS'] = {
    'security_db': 'mysql://root@localhost/busstup_security'
}

# ~~ Configurações do pool para db busstup
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'max_overflow': 5   
}

# ~~ Configurações do pool para db busstup_security
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

from app.routes import route_action, route_get, route_stream, route_page
