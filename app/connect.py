import pymysql
from pymysql import cursors

conf_db = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'busstup',
    'autocommit': True,
    'cursorclass': cursors.DictCursor
}

class db:
    def __init__(self) -> None:
        self.conect = pymysql.connect(**conf_db)
        self.cursor = self.conect.cursor()

        self.__inserir = 'INSERT INTO {} VALUES {}'
        self.__selecionar = 'SELECT {} FROM {}'
        self.__atualizar = 'UPDATE {} SET {}'
        self.__deletar = 'DELETE FROM {}'
        self.__condicao = ' WHERE {}'
    
    @staticmethod
    def printar(value):
        print()
        print()
        print(value)
        print()
        print()

    def execute(self, command: str, placeholders=False):
        if placeholders:
            self.cursor.execute(command, placeholders)
        else: self.cursor.execute(command)
    
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
            retorno = self.cursor.fetchall()
            if retorno:
                if len(retorno) > 1: return retorno
                return retorno[0]

        else: print('ERROR: Tabelas não referênciadas nos campos de pesquisa do dicionário.')

    def update(self, table: str, set: str, where: str):
        command = self.__atualizar.format(table.capitalize(), set)
        command += self.__condicao.format(where)
        self.execute(command)

    def delete(self, table: str, where: str):
        command = self.__deletar.format(table.capitalize())
        command += self.__condicao.format(where)
        self.execute(command)

database = db()


# ~~ Testes
