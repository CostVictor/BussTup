from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from pymysql import cursors
from app import app
import pymysql

# ~~ Flask Security ~~ #

db_flask = SQLAlchemy(app)
    
class User_flask(db_flask.Model, UserMixin):
    __tablename__ = 'User'
    id = db_flask.Column(db_flask.BigInteger, primary_key=True, autoincrement=True)
    primary_key = db_flask.Column(db_flask.String(100), nullable=False)
    hash_senha = db_flask.Column(db_flask.LargeBinary(60), nullable=False)
    fs_uniquifier = db_flask.Column(db_flask.String(64), nullable=False)
    active = db_flask.Column(db_flask.Boolean, nullable=False, default=True)

class Role_flask(db_flask.Model, RoleMixin):
    __tablename__ = 'Role'
    id = db_flask.Column(db_flask.BigInteger, primary_key=True, autoincrement=True)
    name = db_flask.Column(db_flask.String(15), nullable=False)
    User_id = db_flask.Column(db_flask.BigInteger, db_flask.ForeignKey('User.id'), nullable=False)
    user = db_flask.relationship('User_flask', backref=db_flask.backref('roles', lazy=True))

user_datastore = SQLAlchemyUserDatastore(db_flask, User_flask, Role_flask)
security = Security(app, user_datastore)

with app.app_context():
    db_flask.create_all()

def create_user_flask(tabela, primary_key, hash_senha):
    user = user_datastore.create_user(primary_key=primary_key, hash_senha=hash_senha)
    role = user_datastore.create_role(name=tabela)
    user_datastore.add_role_to_user(user, role)
    db_flask.session.commit()

# ~~ Modelos personalizados ~~ #

conf_db = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'busstup',
    'autocommit': True,
    'cursorclass': cursors.DictCursor
}

class DB:
    def __init__(self) -> None:
        self.__conect = pymysql.connect(**conf_db)
        self.__cursor = self.__conect.cursor()

        self.__inserir = 'INSERT INTO {} VALUES {}'
        self.__selecionar = 'SELECT {} FROM {}'
        self.__atualizar = 'UPDATE {} SET {}'
        self.__deletar = 'DELETE FROM {}'
        self.__condicao = ' WHERE {}'
    
    @staticmethod
    def where_user(primary_key, return_table=False):
        reference = 'nome'
        table = 'motorista'
        if primary_key.isdigit():
            reference = 'matricula'
            table = 'aluno'
        where = f'{reference} = "{primary_key}"'

        if return_table:
            return table, where
        return where

    class User_db:
        def __init__(self, db: object, data: dict) -> None:
            self.db = db
            for key, value in data.items():
                setattr(self, key, value)

        def update(self, field: str, new_value):
            if hasattr(self, field):
                table, where = DB.where_user(self.get_PrimaryKey(), return_table=True)
                self.db.update(table, field, new_value, where)
                setattr(self, field, new_value)
                return True
            return False
        
        def get_PrimaryKey(self):
            if hasattr(self, 'matricula'):
                return self.matricula
            return self.nome
    
    def return_user(self, primary_key):
        table, where = self.where_user(primary_key, return_table=True)
        user_consult = self.select(table, where=where)
        return self.User_db(self, user_consult)

    def execute(self, command: str, placeholders=False):
        if placeholders:
            self.__cursor.execute(command, placeholders)
        else: self.__cursor.execute(command)
    
    def insert(self, table: str, data: dict):
        # INFO: "data" --> {campo da tabela: dado a ser preenchido}
        # EX: {nome: "Victor", idade: 19, ...}
        
        campos = ', '.join(data)
        valores = ', '.join('%s' for _ in data.values())
        command = self.__inserir.format(f'{table.capitalize()} ({campos})', f'({valores})')
        self.execute(command, list(data.values()))

    def select(self, table: str, data=None, where=None):
        # INFO: "data" --> texto OU {nome desejado à pesquisa: item OU (item, tabela do item)}
        # EX: "nome, idade" OU {nome do aluno: "nome" OU ("nome", "aluno")}
        # Os valores só devem ser tuplas quando a pesquisa envolver mais de uma tabela

        executar = True
        pesquisa = '*'; formatar = True
        tabelas = [tabela.capitalize() for tabela in table.split(', ')]

        if data:
            if isinstance(data, str):
                pesquisa = data
                formatar = False
            else:
                campos = [campo for campo in data.keys()]
                valores = [valor for valor in data.values()]

                pesquisa = []
                if len(campos) > 1:
                    for index, valor in enumerate(valores):
                        if isinstance(valor, tuple):
                            item, tabelaAlvo = valor
                            pesquisa.append(f'{tabelaAlvo.capitalize()}.{item} AS {campos[index]}')
                        elif len(tabelas) == 1:
                            pesquisa.append(f'{valor} AS {campos[index]}')
                        else: executar = False
                else:
                    if isinstance(valores[0], tuple):
                        item, tabelaAlvo = valores[0]
                        pesquisa.append(f'{tabelaAlvo.capitalize()}.{item} AS {campos[0]}')
                    else: pesquisa.append(f'{valores[0]} AS {campos[0]}')
        
        if executar:
            tabelas = ', '.join(tabelas)
            pesquisa = ', '.join(pesquisa) if pesquisa != '*' and formatar else pesquisa
            command = self.__selecionar.format(pesquisa, tabelas)
            if where: command += self.__condicao.format(where)

            self.execute(command)
            retorno = self.__cursor.fetchall()
            if retorno:
                if len(retorno) > 1: return retorno
                return retorno[0]

        else: print('ERROR: Tabelas não referênciadas nos campos de pesquisa do dicionário.')

    def update(self, table: str, set: str, new_value, where):
        command = self.__atualizar.format(table.capitalize(), f"{set} = {'%s'}")
        command += self.__condicao.format(where)
        self.execute(command, [new_value])

    def delete(self, table: str, where: str):
        command = self.__deletar.format(table.capitalize())
        command += self.__condicao.format(where)
        self.execute(command)

database = DB()
