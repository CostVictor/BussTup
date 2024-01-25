from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from app import app


# ~~ DB Security ~~ #

db = SQLAlchemy(app)
    
class User(db.Model, UserMixin):
    __bind_key__ = 'security_db'
    __tablename__ = 'User'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    primary_key = db.Column(db.String(100), nullable=False)
    hash_senha = db.Column(db.LargeBinary(60), nullable=False)
    fs_uniquifier = db.Column(db.String(64), nullable=False)
    aceitou_termo_uso = db.Column(db.Boolean, nullable=False, default=True)


class Role(db.Model, RoleMixin):
    __bind_key__ = 'security_db'
    __tablename__ = 'Role'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    User_id = db.Column(db.BigInteger, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('roles', lazy=True))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# ~~ DB Principal ~~ #

class Linha(db.Model):
    __tablename__ = 'Linha'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    paga = db.Column(db.Boolean, nullable=False)
    ferias = db.Column(db.Boolean, nullable=False, default=0)
    valor_cartela = db.Column(db.Float)
    valor_diaria = db.Column(db.Float)


class Motorista(db.Model):
    __tablename__ = 'Motorista'
    login = db.Column(db.String(100), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    pix = db.Column(db.String(100))


class Onibus(db.Model):
    __tablename__ = 'Onibus'
    placa = db.Column(db.String(7), primary_key=True)
    capacidade = db.Column(db.Integer, nullable=False)
    Linha_codigo = db.Column(db.BigInteger, db.ForeignKey('Linha.codigo'), nullable=False)
    Motorista_login = db.Column(db.String(100), db.ForeignKey('Motorista.login'))
    linha = db.relationship('Linha', backref=db.backref('onibus', lazy=True))
    motorista = db.relationship('Motorista', backref=db.backref('onibus', lazy=True))


class Rota(db.Model):
    __tablename__ = 'Rota'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    turno = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(5), nullable=False)
    em_atividade = db.Column(db.Boolean, nullable=False, default=0)
    horario = db.Column(db.Time)
    Onibus_placa = db.Column(db.String(7), db.ForeignKey('Onibus.placa'), nullable=False)
    onibus = db.relationship('Onibus', backref=db.backref('rotas', lazy=True))


class Aluno(db.Model):
    __tablename__ = 'Aluno'
    login = db.Column(db.String(100), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    curso = db.Column(db.String(50), nullable=False)
    turno = db.Column(db.String(10), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Registro_Aluno(db.Model):
    __tablename__ = 'Registro_Aluno'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    ida = db.Column(db.Boolean, nullable=False, default=1)
    contraturno = db.Column(db.Boolean, nullable=False, default=0)
    presente_ida = db.Column(db.Boolean, nullable=False, default=0)
    presente_volta = db.Column(db.Boolean, nullable=False, default=0)
    Aluno_login = db.Column(db.String(100), db.ForeignKey('Aluno.login'), nullable=False)
    aluno = db.relationship('Aluno', backref=db.backref('registros', lazy=True))


class Ponto(db.Model):
    __tablename__ = 'Ponto'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    tempo_tolerancia = db.Column(db.String(1))
    linkGPS = db.Column(db.String(200))
    Linha_codigo = db.Column(db.BigInteger, db.ForeignKey('Linha.codigo'), nullable=False)
    linha = db.relationship('Linha', backref=db.backref('pontos', lazy=True))


class Rota_has_Ponto(db.Model):
    __tablename__ = 'Rota_has_Ponto'
    Rota_codigo = db.Column(db.BigInteger, db.ForeignKey('Rota.codigo'), primary_key=True, nullable=False)
    Ponto_id = db.Column(db.BigInteger, db.ForeignKey('Ponto.id'), primary_key=True, nullable=False)
    ordem = db.Column(db.String(2), nullable=False)
    hora_passagem = db.Column(db.TIME, nullable=False)
    rota = db.relationship('Rota', backref=db.backref('pontos', lazy=True))
    ponto = db.relationship('Ponto', backref=db.backref('rotas', lazy=True))


class Cartela_Ticket(db.Model):
    __tablename__ = 'Cartela_Ticket'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    estado = db.Column(db.String(8), nullable=False)
    validade = db.Column(db.Integer, nullable=False)
    dt_inicial = db.Column(db.Date, nullable=False)
    quant_tickets = db.Column(db.Integer, nullable=False)
    dt_ultimo_registro = db.Column(db.Date)
    Linha_codigo = db.Column(db.BigInteger, db.ForeignKey('Linha.codigo'), nullable=False)
    Aluno_login = db.Column(db.String(100), db.ForeignKey('Aluno.login'), nullable=False)
    linha = db.relationship('Linha', backref=db.backref('cartelas', lazy=True))
    aluno = db.relationship('Aluno', backref=db.backref('cartelas', lazy=True))


class Aluno_has_Ponto(db.Model):
    __tablename__ = 'Aluno_has_Ponto'
    Ponto_id = db.Column(db.BigInteger, db.ForeignKey('Ponto.id'), primary_key=True, nullable=False)
    Aluno_login = db.Column(db.String(100), db.ForeignKey('Aluno.login'), primary_key=True, nullable=False)
    acao = db.Column(db.String(6), nullable=False)
    esperar = db.Column(db.Boolean, nullable=False, default=False)
    tipo = db.Column(db.String(10), nullable=False)
    dt_validade_temporario = db.Column(db.Date)
    dt_validade_espera = db.Column(db.Date)
    ponto = db.relationship('Ponto', backref=db.backref('associados', lazy=True))
    aluno = db.relationship('Aluno', backref=db.backref('associacao', lazy=True))


class Contraturno_Fixo(db.Model):
    __tablename__ = 'Contraturno_Fixo'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    numero_do_dia = db.Column(db.String(1), nullable=False)
    Aluno_login = db.Column(db.String(100), db.ForeignKey('Aluno.login'), nullable=False)
    aluno = db.relationship('Aluno', backref=db.backref('contraturnos_fixos', lazy=True))


class Linha_has_Motorista(db.Model):
    __tablename__ = 'Linha_has_Motorista'
    Linha_codigo = db.Column(db.BigInteger, db.ForeignKey('Linha.codigo'), primary_key=True, nullable=False)
    Motorista_login = db.Column(db.String(100), db.ForeignKey('Motorista.login'), primary_key=True, nullable=False)
    motorista_dono = db.Column(db.Boolean, nullable=False, default=False)
    motorista_adm = db.Column(db.Boolean, nullable=False, default=False)
    linha = db.relationship('Linha', backref=db.backref('motoristas_associados', lazy=True))
    motorista = db.relationship('Motorista', backref=db.backref('linhas', lazy=True))


class Registro_Passagem(db.Model):
    __tablename__ = 'Registro_Passagem'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    passou = db.Column(db.Boolean, nullable=False, default=False)
    Rota_has_Ponto_Rota_codigo = db.Column(db.BigInteger, nullable=False)
    Rota_has_Ponto_Ponto_id = db.Column(db.BigInteger, nullable=False)
    rota_ponto = db.relationship(
        'Rota_has_Ponto', 
        primaryjoin='and_(Registro_Passagem.Rota_has_Ponto_Rota_codigo == Rota_has_Ponto.Rota_codigo, Registro_Passagem.Rota_has_Ponto_Ponto_id == Rota_has_Ponto.Ponto_id)', 
        foreign_keys="[Registro_Passagem.Rota_has_Ponto_Rota_codigo, Registro_Passagem.Rota_has_Ponto_Ponto_id]", 
        backref=db.backref('registros', lazy=True)
    )


class Registro_Rota(db.Model):
    __tablename__ = 'Registro_Rota'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=False)
    previsao_pessoas = db.Column(db.Integer, nullable=False)
    Rota_codigo = db.Column(db.BigInteger, db.ForeignKey('Rota.codigo'), nullable=False)
    rota = db.relationship('Rota', backref=db.backref('registros', lazy=True))


with app.app_context():
    db.create_all()


def create_user(data):
    hash_senha = data.pop('hash_senha')
    role = data.pop('role')

    if role == 'aluno':
        user = Aluno(**data)
    else: user = Motorista(**data)
    db.session.add(user)

    user_security = user_datastore.create_user(primary_key=data['login'], hash_senha=hash_senha)
    role_user = user_datastore.create_role(name=role)
    user_datastore.add_role_to_user(user_security, role_user)
    
    db.session.commit()


def return_user(str_login):
    motorista = Motorista.query.filter_by(login = str_login).first()
    if motorista: return motorista

    aluno = Aluno.query.filter_by(login = str_login).first()
    if aluno: return aluno

    return None
