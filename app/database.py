from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from app import app, turnos, dias_semana


# ~~ DB Security ~~ #

db = SQLAlchemy(app)

class Restriction(db.Model):
    __bind_key__ = 'db_session'
    __tablename__ = 'Restriction'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ip_acesso = db.Column(db.String(32), nullable=False)
    tentativas = db.Column(db.Integer, nullable=False)

    
class User(db.Model, UserMixin):
    __bind_key__ = 'db_session'
    __tablename__ = 'User'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.LargeBinary(60), nullable=False)
    primary_key = db.Column(db.BigInteger, nullable=False)
    fs_uniquifier = db.Column(db.String(64), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    analysis = db.Column(db.Boolean, nullable=False, default=False)
    aceitou_termo_uso_dados = db.Column(db.Boolean, nullable=False, default=True)


class Role(db.Model, RoleMixin):
    __bind_key__ = 'db_session'
    __tablename__ = 'Role'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum('aluno', 'motorista', 'administrador'), nullable=False)
    User_id = db.Column(db.BigInteger, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('roles', lazy=True))


class Access_Device(db.Model):
    __bind_key__ = 'db_session'
    __tablename__ = 'Access_Device'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dispositivo = db.Column(db.String(60), nullable=False)
    User_id = db.Column(db.BigInteger, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('devices', lazy=True))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# ~~ DB Principal ~~ #

class Motorista(db.Model):
    __tablename__ = 'Motorista'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    pix = db.Column(db.String(100))


class Linha(db.Model):
    __tablename__ = 'Linha'
    codigo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    paga = db.Column(db.Boolean, nullable=False)
    ferias = db.Column(db.Boolean, nullable=False, default=False)
    valor_cartela = db.Column(db.Numeric(5, 2))
    valor_diaria = db.Column(db.Numeric(4, 2))


class Onibus(db.Model):
    __tablename__ = 'Onibus'
    placa = db.Column(db.String(7), primary_key=True)
    capacidade = db.Column(db.Integer, nullable=False)
    Linha_codigo = db.Column(db.Integer, db.ForeignKey('Linha.codigo'), nullable=False)
    Motorista_id = db.Column(db.Integer, db.ForeignKey('Motorista.id'))
    linha = db.relationship('Linha', backref=db.backref('onibus', lazy=True))
    motorista = db.relationship('Motorista', backref=db.backref('onibus', lazy=True))


class Rota(db.Model):
    __tablename__ = 'Rota'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    turno = db.Column(db.Enum(*turnos), nullable=False)
    em_partida = db.Column(db.Boolean, nullable=False, default=False)
    em_retorno = db.Column(db.Boolean, nullable=False, default=False)
    horario_partida = db.Column(db.Time, nullable=False)
    horario_retorno = db.Column(db.Time, nullable=False)
    Linha_codigo = db.Column(db.BigInteger, db.ForeignKey('Linha.codigo'), nullable=False)
    Onibus_placa = db.Column(db.String(7), db.ForeignKey('Onibus.placa'))
    linha = db.relationship('Linha', backref=db.backref('rotas', lazy=True))
    onibus = db.relationship('Onibus', backref=db.backref('rotas', lazy=True))


class Aluno(db.Model):
    __tablename__ = 'Aluno'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    curso = db.Column(db.String(25), nullable=False)
    turno = db.Column(db.Enum(*turnos), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Registro_Aluno(db.Model):
    __tablename__ = 'Registro_Aluno'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    faltara = db.Column(db.Boolean, nullable=False, default=False)
    contraturno = db.Column(db.Boolean, nullable=False, default=False)
    presente_partida = db.Column(db.Boolean, nullable=False, default=False)
    presente_retorno = db.Column(db.Boolean, nullable=False, default=False)
    Aluno_id = db.Column(db.BigInteger, db.ForeignKey('Aluno.id'), nullable=False)
    aluno = db.relationship('Aluno', backref=db.backref('registros', lazy=True))


class Ponto(db.Model):
    __tablename__ = 'Ponto'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    tempo_tolerancia = db.Column(db.String(2), nullable=False, default='5')
    linkGPS = db.Column(db.String(200))
    Linha_codigo = db.Column(db.Integer, db.ForeignKey('Linha.codigo'), nullable=False)
    linha = db.relationship('Linha', backref=db.backref('pontos', lazy=True))


class Parada(db.Model):
    __tablename__ = 'Parada'
    Rota_codigo = db.Column(db.BigInteger, db.ForeignKey('Rota.codigo'), primary_key=True)
    Ponto_id = db.Column(db.BigInteger, db.ForeignKey('Ponto.id'), primary_key=True)
    tipo = db.Column(db.Enum('partida', 'retorno'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    horario_passagem = db.Column(db.Time, nullable=False)
    rota = db.relationship('Rota', backref=db.backref('pontos', lazy=True))
    ponto = db.relationship('Ponto', backref=db.backref('rotas', lazy=True))


class Cartela_Ticket(db.Model):
    __tablename__ = 'Cartela_Ticket'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    valida = db.Column(db.Boolean, nullable=False, default=True)
    data_expiracao = db.Column(db.Date, nullable=False)
    data_adicao = db.Column(db.Date, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    ultima_atualizacao = db.Column(db.Date)
    Linha_codigo = db.Column(db.Integer, db.ForeignKey('Linha.codigo'), nullable=False)
    Aluno_id = db.Column(db.BigInteger, db.ForeignKey('Aluno.id'), nullable=False)
    linha = db.relationship('Linha', backref=db.backref('cartelas', lazy=True))
    aluno = db.relationship('Aluno', backref=db.backref('cartelas', lazy=True))


class Contraturno_Fixo(db.Model):
    __tablename__ = 'Contraturno_Fixo'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dia_fixo = db.Column(db.Enum(*dias_semana), nullable=False)
    Aluno_id = db.Column(db.String(100), db.ForeignKey('Aluno.id'), nullable=False)
    aluno = db.relationship('Aluno', backref=db.backref('contraturnos_fixos', lazy=True))


class Membro(db.Model):
    __tablename__ = 'Membro'
    Linha_codigo = db.Column(db.Integer, db.ForeignKey('Linha.codigo'), primary_key=True)
    Motorista_id = db.Column(db.Integer, db.ForeignKey('Motorista.id'), primary_key=True)
    dono = db.Column(db.Boolean, nullable=False, default=False)
    adm = db.Column(db.Boolean, nullable=False, default=False)
    linha = db.relationship('Linha', backref=db.backref('membros', lazy=True))
    motorista = db.relationship('Motorista', backref=db.backref('linhas', lazy=True))


class Registro_Parada(db.Model):
    __tablename__ = 'Registro_Parada'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    veiculo_passou = db.Column(db.Boolean, nullable=False, default=False)
    quantidade_no_veiculo = db.Column(db.Integer, nullable=False)
    Parada_Rota_codigo = db.Column(db.BigInteger, nullable=False)
    Parada_Ponto_id = db.Column(db.BigInteger, nullable=False)
    parada = db.relationship(
        'Parada', 
        primaryjoin='and_(Registro_Parada.Parada_Rota_codigo == Parada.Rota_codigo, Registro_Parada.Parada_Ponto_id == Parada.Ponto_id)', 
        foreign_keys="[Registro_Parada.Parada_Rota_codigo, Registro_Parada.Parada_Ponto_id]", 
        backref=db.backref('registros', lazy=True)
    )


class Registro_Rota(db.Model):
    __tablename__ = 'Registro_Rota'
    codigo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum('partida', 'retorno'), nullable=False)
    quantidade_pessoas = db.Column(db.Integer, nullable=False)
    previsao_pessoas = db.Column(db.Integer, nullable=False)
    Rota_codigo = db.Column(db.BigInteger, db.ForeignKey('Rota.codigo'), nullable=False)
    rota = db.relationship('Rota', backref=db.backref('registros', lazy=True))


class Passagem(db.Model):
    __tablename__ = 'Passagem'
    Parada_Rota_codigo = db.Column(db.BigInteger, primary_key=True)
    Parada_Ponto_id = db.Column(db.BigInteger, primary_key=True)
    Aluno_id = db.Column(db.BigInteger, db.ForeignKey('Aluno.id'), primary_key=True)
    passagem_fixa = db.Column(db.Boolean, nullable=False)
    passagem_contraturno = db.Column(db.Boolean, nullable=False)
    pediu_espera = db.Column(db.Boolean, nullable=False, default=False)
    data = db.Column(db.Date)
    aluno = db.relationship('Aluno', backref=db.backref('passagens', lazy=True))
    parada = db.relationship(
        'Parada', 
        primaryjoin='and_(Passagem.Parada_Rota_codigo == Parada.Rota_codigo, Passagem.Parada_Ponto_id == Parada.Ponto_id)', 
        foreign_keys="[Passagem.Parada_Rota_codigo, Passagem.Parada_Ponto_id]", 
        backref=db.backref('passagens', lazy=True)
    )


with app.app_context():
    db.create_all()


def create_user(data):
    login = data.pop('login')
    password_hash = data.pop('password_hash')
    role = data.pop('role')

    if role == 'aluno':
        user = Aluno(**data)
    else: user = Motorista(**data)

    try:
        db.session.add(user)
        with db.session.begin_nested():
            user_session = user_datastore.create_user(login=login, password_hash=password_hash, primary_key=user.id)
            role_user = user_datastore.create_role(name=role)
            user_datastore.add_role_to_user(user_session, role_user)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f'Erro ao cadastrar um usuário: {str(e)}')
        return False


def return_my_user():
    role = current_user.roles[0].name
    if role == 'aluno':
        return Aluno.query.filter_by(id=current_user.primary_key).first()
    return Motorista.query.filter_by(id=current_user.primary_key).first()


def check_dis_login(str_login):
    if User.query.filter_by(login=str_login).first():
        return False
    return True
