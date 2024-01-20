from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy, PrimaryKeyConstraint
from app import app
import numpy as np


# ~~ DB Security ~~ #

db_security = SQLAlchemy(app)
    
class User(db_security.Model, UserMixin):
    __bind_key__ = 'security_db'
    __tablename__ = 'User'
    id = db_security.Column(db_security.BigInteger, primary_key=True, autoincrement=True)
    active = db_security.Column(db_security.Boolean, nullable=False, default=True)
    primary_key = db_security.Column(db_security.String(100), nullable=False)
    hash_senha = db_security.Column(db_security.LargeBinary(60), nullable=False)
    fs_uniquifier = db_security.Column(db_security.String(64), nullable=False)
    aceitou_termo_uso = db_security.Column(db_security.Boolean, nullable=False, default=True)


class Role(db_security.Model, RoleMixin):
    __bind_key__ = 'security_db'
    __tablename__ = 'Role'
    id = db_security.Column(db_security.BigInteger, primary_key=True, autoincrement=True)
    name = db_security.Column(db_security.String(15), nullable=False)
    User_id = db_security.Column(db_security.BigInteger, db_security.ForeignKey('User.id'), nullable=False)
    user = db_security.relationship('User', backref=db_security.backref('roles', lazy=True))


user_datastore = SQLAlchemyUserDatastore(db_security, User, Role)
security = Security(app, user_datastore)


# ~~ DB Principal ~~ #

db_primary = SQLAlchemy(app)

class Linha(db_primary.Model):
    __tablename__ = 'Linha'
    codigo = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    nome = db_primary.Column(db_primary.String(100), nullable=False)
    cidade = db_primary.Column(db_primary.String(100), nullable=False)
    paga = db_primary.Column(db_security.Boolean, nullable=False)
    ferias = db_primary.Column(db_security.Boolean, nullable=False, default=0)
    valor_cartela = db_primary.Column(db_primary.Float)
    valor_diaria = db_primary.Column(db_primary.Float)


class Motorista(db_primary.Model):
    __tablename__ = 'Motorista'
    login = db_primary.Column(db_primary.String(100), primary_key=True)
    nome = db_primary.Column(db_primary.String(100), nullable=False)
    telefone = db_primary.Column(db_primary.String(15), nullable=False)
    pix = db_primary.Column(db_primary.String(100))


class Onibus(db_primary.Model):
    __tablename__ = 'Onibus'
    placa = db_primary.Column(db_primary.String(7), primary_key=True)
    capacidade = db_primary.Column(db_primary.Integer, nullable=False)
    Linha_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Linha.codigo'), nullable=False)
    Motorista_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Motorista.login'))
    linha = db_primary.relationship('Linha', backref=db_primary.backref('onibus', lazy=True))
    motorista = db_primary.relationship('Motorista', backref=db_primary.backref('onibus', lazy=True))


class Rota(db_primary.Model):
    __tablename__ = 'Rota'
    codigo = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    turno = db_primary.Column(db_primary.String(10), nullable=False)
    tipo = db_primary.Column(db_primary.String(5), nullable=False)
    em_atividade = db_primary.Column(db_security.Boolean, nullable=False, default=0)
    horario = db_primary.Column(db_primary.Time)
    Onibus_placa = db_primary.Column(db_primary.String(7), db_primary.ForeignKey('Onibus.placa'), nullable=False)
    onibus = db_primary.relationship('Onibus', backref=db_primary.backref('rotas', lazy=True))


class Aluno(db_primary.Model):
    __tablename__ = 'Aluno'
    login = db_primary.Column(db_primary.String(100), primary_key=True)
    nome = db_primary.Column(db_primary.String(100), nullable=False)
    curso = db_primary.Column(db_primary.String(50), nullable=False)
    turno = db_primary.Column(db_primary.String(10), nullable=False)
    telefone = db_primary.Column(db_primary.String(15), nullable=False)
    email = db_primary.Column(db_primary.String(100), nullable=False)


class Registro_Aluno(db_primary.Model):
    __tablename__ = 'Registro_Aluno'
    codigo = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    data = db_primary.Column(db_primary.Date, nullable=False)
    ida = db_primary.Column(db_security.Boolean, nullable=False, default=1)
    contraturno = db_primary.Column(db_security.Boolean, nullable=False, default=0)
    presente_ida = db_primary.Column(db_security.Boolean, nullable=False, default=0)
    presente_volta = db_primary.Column(db_security.Boolean, nullable=False, default=0)
    Aluno_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Aluno.login'), nullable=False)
    aluno = db_primary.relationship('Aluno', backref=db_primary.backref('registros', lazy=True))


class Ponto(db_primary.Model):
    __tablename__ = 'Ponto'
    id = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    nome = db_primary.Column(db_primary.String(100), nullable=False)
    tempo_tolerancia = db_primary.Column(db_primary.String(1))
    linkGPS = db_primary.Column(db_primary.String(200))
    Linha_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Linha.codigo'), nullable=False)
    linha = db_primary.relationship('Linha', backref=db_primary.backref('pontos', lazy=True))


class Rota_has_Ponto(db_primary.Model):
    __tablename__ = 'Rota_has_Ponto'
    Rota_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Rota.codigo'), nullable=False)
    Ponto_id = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Ponto.id'), nullable=False)
    ordem = db_primary.Column(db_primary.String(2), nullable=False)
    hora_passagem = db_primary.Column(db_primary.TIME, nullable=False)
    rota = db_primary.relationship('Rota', backref=db_primary.backref('pontos', lazy=True))
    ponto = db_primary.relationship('Ponto', backref=db_primary.backref('rotas', lazy=True))
    PrimaryKeyConstraint('Rota_codigo', 'Ponto_id')


class Cartela_Ticket(db_primary.Model):
    __tablename__ = 'Cartela_Ticket'
    id = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    estado = db_primary.Column(db_primary.String(8), nullable=False)
    validade = db_primary.Column(db_primary.Integer, nullable=False)
    dt_inicial = db_primary.Column(db_primary.Date, nullable=False)
    quant_tickets = db_primary.Column(db_primary.Integer, nullable=False)
    dt_ultimo_registro = db_primary.Column(db_primary.Date)
    Linha_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Linha.codigo'), nullable=False)
    Aluno_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Aluno.login'), nullable=False)
    linha = db_primary.relationship('Linha', backref='cartelas')
    aluno = db_primary.relationship('Aluno', backref='cartelas')


class Aluno_has_Ponto(db_primary.Model):
    __tablename__ = 'Aluno_has_Ponto'
    Ponto_id = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Ponto.id'), nullable=False)
    Aluno_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Aluno.login'), nullable=False)
    acao = db_primary.Column(db_primary.String(6), nullable=False)
    esperar = db_primary.Column(db_primary.Boolean, nullable=False, default=False)
    tipo = db_primary.Column(db_primary.String(10), nullable=False)
    dt_validade_temporario = db_primary.Column(db_primary.Date)
    dt_validade_espera = db_primary.Column(db_primary.Date)
    ponto = db_primary.relationship('Ponto', backref='alunos_associados')
    aluno = db_primary.relationship('Aluno', backref='pontos_associados')


class Contraturno_Fixo(db_primary.Model):
    __tablename__ = 'Contraturno_Fixo'
    id = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    numero_do_dia = db_primary.Column(db_primary.String(1), nullable=False)
    Aluno_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Aluno.login'), nullable=False)
    aluno = db_primary.relationship('Aluno', backref='contraturnos_fixos')


class Linha_has_Motorista(db_primary.Model):
    __tablename__ = 'Linha_has_Motorista'
    Linha_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Linha.codigo'), nullable=False)
    Motorista_login = db_primary.Column(db_primary.String(100), db_primary.ForeignKey('Motorista.login'), nullable=False)
    motorista_dono = db_primary.Column(db_primary.Boolean, nullable=False, default=False)
    motorista_adm = db_primary.Column(db_primary.Boolean, nullable=False, default=False)
    linha = db_primary.relationship('Linha', backref='motoristas_associados')
    motorista = db_primary.relationship('Motorista', backref='linhas_associadas')


class Registro_Passagem(db_primary.Model):
    __tablename__ = 'Registro_Passagem'
    codigo = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    data = db_primary.Column(db_primary.Date, nullable=False)
    passou = db_primary.Column(db_primary.Boolean, nullable=False, default=False)
    Rota_has_Ponto_Rota_codigo = db_primary.Column(db_primary.BigInteger, nullable=False)
    Rota_has_Ponto_Ponto_id = db_primary.Column(db_primary.BigInteger, nullable=False)
    rota_ponto = db_primary.relationship('Rota_has_Ponto', backref='registros_passagem')


class Registro_Rota(db_primary.Model):
    __tablename__ = 'Registro_Rota'
    codigo = db_primary.Column(db_primary.BigInteger, primary_key=True, autoincrement=True)
    data = db_primary.Column(db_primary.Date, nullable=False)
    quantidade_pessoas = db_primary.Column(db_primary.Integer, nullable=False)
    previsao_pessoas = db_primary.Column(db_primary.Integer, nullable=False)
    Rota_codigo = db_primary.Column(db_primary.BigInteger, db_primary.ForeignKey('Rota.codigo'), nullable=False)
    rota = db_primary.relationship('Rota', backref='registros_rota')


with app.app_context():
    db_security.create_all()
    db_primary.create_all()

def create_user(tabela, primary_key, hash_senha):
    user = user_datastore.create_user(primary_key=primary_key, hash_senha=hash_senha)
    role = user_datastore.create_role(name=tabela)
    user_datastore.add_role_to_user(user, role)
    db_security.session.commit()
