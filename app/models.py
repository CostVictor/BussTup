from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
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
    aceitou_termos = db_flask.Column(db_flask.Boolean, nullable=False, default=True)

class Role_flask(db_flask.Model, RoleMixin):
    __tablename__ = 'Role'
    id = db_flask.Column(db_flask.BigInteger, primary_key=True, autoincrement=True)
    name = db_flask.Column(db_flask.String(15), nullable=False)
    User_id = db_flask.Column(db_flask.BigInteger, db_flask.ForeignKey('User.id'), nullable=False)
    user = db_flask.relationship('User_flask', backref=db_flask.backref('roles', lazy=True))

user_datastore = SQLAlchemyUserDatastore(db_flask, User_flask, Role_flask)
security = Security(app, user_datastore)
jwt = JWTManager(app)

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
        self._inserir = 'INSERT INTO {} ({}) VALUES ({})'
        self._selecionar = 'SELECT {} FROM {}'
        self._atualizar = 'UPDATE {} SET {} = %s'
        self._deletar = 'DELETE FROM {}'
        self._condicao = ' WHERE {}'

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

    @classmethod
    def execute(self, command: str, placeholders):
        self.open_connect()
        if not isinstance(placeholders, tuple) and not isinstance(placeholders, list):
            placeholders = (placeholders)
        self._cursor.execute(command, placeholders)

    @classmethod
    def open_connect(self):
        self._conect = pymysql.connect(**conf_db)
        self._cursor = self._conect.cursor()
    
    def close_connect(self):
        self._cursor.close()
        self._conect.close()
    
    def return_user(self, primary_key):
        table, where = self.where_user(primary_key, return_table=True)
        user_consult = self.select(table, where=where)
        return self.User_db(self, user_consult)
    
    def format_where(self, condiction: dict):
        if 'where' in condiction:
            condict = self._condicao.format(condiction['where'])
            if 'value' in condiction:
                return condict, condiction['value']
            return condict
        return False
    
    def insert(self, table: str, data: dict):
        # INFO: "data" --> {campo da tabela: dado a ser preenchido}
        # EX: {nome: "Victor", idade: 19, ...}
        
        campos = ', '.join(data)
        valores = ', '.join('%s' for _ in data.values())
        command = self._inserir.format(table.capitalize(), campos, valores)
        self.execute(command, [value for value in data.values()])
        self.close_connect()

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

            command = self._selecionar.format(pesquisa, tabelas)
            sql_where, value_where = self.format_where(where)

            self.execute(command + sql_where, value_where)
            retorno = self._cursor.fetchall()
            self.close_connect()

            if retorno:
                if len(retorno) > 1: return retorno
                return retorno[0]

        else: print('ERROR: Tabelas não referênciadas nos campos de pesquisa do dicionário.')

    def update(self, table: str, set: str, new_value, where):
        command = self._atualizar.format(table, set)
        sql_where, value_where = self.format_where(where)

        self.execute(command + sql_where, (new_value, value_where))
        self.close_connect()

    def delete(self, table: str, where: str):
        command = self._deletar.format(table.capitalize())
        sql_where, value_where = self.format_where(where)

        self.execute(command + sql_where, (value_where))
        self.close_connect()
    
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
    
    @staticmethod
    def format_listDate(list_date, camp_name='data', operator='OR'):
        dates = f' {operator} {camp_name} = '.join(list_date)
        return f'({camp_name} = {dates})'

    @staticmethod
    def format_time(data):
        def converter(value):
            horas = value.seconds // 3600
            minutos = (value.seconds % 3600) // 60
            segundos = value.seconds % 60
            return {'hora': horas, 'minuto': minutos, 'segundo': segundos}
        
        if isinstance(data, list):
            for index, element in enumerate(data):
                if isinstance(element, dict):
                    data[index]['horario'] = converter(element['horario'])
                else: data[index] = converter(element)
            return data
        elif isinstance(data, dict):
            data['horario'] = converter(data['horario'])
            return data
        return converter(data)

    @staticmethod
    def format_date(data):
        def converter(value):
            value = value.strftime("%Y-%m-%d")
            value = value.split('-')
            return {'dia': value[2], 'mes': value[1], 'ano': value[0]}
        
        if isinstance(data, list):
            for index, element in enumerate(data):
                if isinstance(element, dict):
                    data[index]['data'] = converter(element['data'])
                else: data[index] = converter(element)
            return data
        elif isinstance(data, dict):
            data['data'] = converter(data['data'])
            return data
        return converter(data)

database = DB()
