from app.connect import database
import difflib, bcrypt, numpy as np

# ~~ Cursos e turnos
cursos = ['informática', 'química', 'agropecuária']
turnos = ['matutino', 'vespertino', 'noturno']

def capitalizar(string):
    nome = string.split(' ')
    for index, palavra in enumerate(nome):
        if palavra:
            palavra = palavra.lower()
            if palavra != 'da' and palavra != 'do' and palavra != 'de':
                palavra = palavra.capitalize()
            nome[index] = palavra
    return ' '.join(nome)

def validar_usuario(data):
    tabela = data['table']
    condiction = f'{"nome" if tabela == "motorista" else "matricula"} = {data["user"]}'
    usuario = database.select(tabela, where=condiction)

    if usuario:
        if bcrypt.checkpw(data['password'].encode('utf-8'), usuario['hash_senha']):...

def formatData(dadosAdquiridos):
    if dadosAdquiridos:
        inconsistencia = False
        erro_titulo = ''
        erro_texto = ''

        tabela = dadosAdquiridos['table']
        data = dadosAdquiridos['data']
        for campo, dado in data.items():
            if campo == 'matricula':
                if database.select(tabela, where=f'matricula = "{dado}"'):
                    erro_titulo = 'Usuário existente'
                    erro_texto = 'Já existe um usuário registrado na matrícula especificada.'
                    inconsistencia = True; break
            elif campo == 'nome':
                nome = capitalizar(dado)
                if tabela == 'motorista':
                    if database.select(tabela, where=f'nome = "{nome}"'):
                        erro_titulo = 'Usuário existente'
                        erro_texto = 'Já existe um usuário registrado no nome especificado.'
                        inconsistencia = True; break
                data[campo] = nome
            elif campo == 'curso':
                cursoDefinido = dado.lower()
                comparacoes = np.array([difflib.SequenceMatcher(None, curso, cursoDefinido).ratio() for curso in cursos])
                cursoIdentify = np.argmax(comparacoes)
                data[campo] = cursos[cursoIdentify].capitalize()
            elif campo == 'turno':
                turnoDefinido = dado.lower()
                if turnoDefinido == 'manha' or turnoDefinido == 'manhã':
                    data[campo] = 'Matutino'
                elif turnoDefinido == 'tarde':
                    data[campo] = 'Vespertino'
                elif turnoDefinido == 'noite':
                    data[campo] = 'Noturno'
                else:
                    comparacoes = np.array([difflib.SequenceMatcher(None, turno, turnoDefinido).ratio() for turno in turnos])
                    turnoIdentify = np.argmax(comparacoes)
                    data[campo] = turnos[turnoIdentify].capitalize()
            elif campo == 'telefone':
                ddd = dado[:2]
                telefone = dado[2:]
                if telefone[0] != '9':
                    erro_titulo = 'Telefone inválido'
                    erro_texto = 'O telefone especificado é inválido.'
                    inconsistencia = True; break
                data[campo] = f'({ddd}) {telefone[:5]}-{telefone[5:]}'

        senha = data['senha'].encode('utf-8')
        del data['senha']; data['salt'] = bcrypt.gensalt()
        data['hash_senha'] = bcrypt.hashpw(senha, data['salt'])
        return tabela, data, inconsistencia, erro_titulo, erro_texto
