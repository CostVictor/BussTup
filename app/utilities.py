from app.database import db
from datetime import timedelta, datetime
from flask_security import current_user
import difflib, bcrypt, numpy as np

# ~~ Cursos e turnos
cursos = ['informática', 'química', 'agropecuária']
turnos = ['matutino', 'vespertino', 'noturno']


def capitalize(string):
    nome = string.split(' ')
    for index, palavra in enumerate(nome):
        if palavra:
            palavra = palavra.lower()
            if palavra != 'da' and palavra != 'do' and palavra != 'de':
                palavra = palavra.capitalize()
            nome[index] = palavra
    return ' '.join(nome)


def formatTel(dado):
    ddd = dado[:2]
    telefone = dado[2:]
    if telefone[0] != '9':
        return False
    return f'({ddd}) {telefone[:5]}-{telefone[5:]}'


def formatData(dadosAdquiridos):
    if dadosAdquiridos:
        inconsistencia = False
        erro_titulo = ''
        erro_texto = ''

        tabela = dadosAdquiridos['table']
        data = dadosAdquiridos['data']
        for campo, dado in data.items():
            if campo == 'matricula':
                print(dado, type(dado))
                if db.select(tabela, where={'where': 'matricula = %s', 'value': dado}):
                    erro_titulo = 'Usuário existente'
                    erro_texto = 'Já existe um usuário registrado na matrícula especificada.'
                    inconsistencia = True; break
            elif campo == 'nome':
                nome = capitalize(dado)
                if tabela == 'motorista':
                    if db.select(tabela, where={'where': 'nome = %s', 'value': nome}):
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
                value_telefone = formatTel(dado)
                if not value_telefone:
                    erro_titulo = 'Telefone inválido'
                    erro_texto = 'O telefone especificado é inválido.'
                    inconsistencia = True; break
                data[campo] = value_telefone

        senha = data['senha'].encode('utf-8'); del data['senha']
        hash_senha = bcrypt.hashpw(senha, bcrypt.gensalt())
        return tabela, data, hash_senha, inconsistencia, erro_titulo, erro_texto


def return_dates():
    hoje = datetime.now()
    dia_semana = hoje.weekday()
    dias_ate_segunda = (dia_semana + 1) % 7
    if dia_semana == 5 or dia_semana == 6:
        dias_ate_segunda = 7 - dia_semana
        segunda = hoje + timedelta(days=dias_ate_segunda)
    else: segunda = hoje - timedelta(days=dias_ate_segunda)

    datas_semana = []
    for index in range(5):
        data_dia = segunda + timedelta(days=index)
        data_dia = f'"{data_dia.strftime("%Y-%m-%d")}"'
        datas_semana.append(data_dia)
        
    return datas_semana


def return_relationship(codigo_linha):
    if current_user.primary_key.isdigit():
        ponto = db.select('Aluno_has_Ponto', data='Ponto_id', where={'where': 'Aluno_matricula = %s', 'value': current_user.primary_key})

        if ponto:
            id_ponto = ponto[0]['Ponto_id']
            verify = db.select('Ponto', where={'where': 'id = %s AND Linha_codigo = %s', 'value': (id_ponto, codigo_linha)})

            if verify: relacao = 'participante'
            else: relacao = 'de outra linha'
        else: relacao = None
    else:
        verify = db.select('Linha_has_Motorista', where={'where': 'Motorista_nome = %s AND Linha_codigo = %s', 'value': (current_user.primary_key, codigo_linha)})

        if verify:
            if verify['motorista_dono']:
                relacao = 'dono'
            elif verify['motorista_adm']:
                relacao = 'adm'
            else: relacao = 'membro'
        else: relacao = None
    return relacao


def return_code(name_line, permission='motorista_adm'):
    codigo_linha = db.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': name_line})['codigo']
    relacao = db.select('Linha_has_Motorista', where={'where': 'Linha_codigo = %s AND Motorista_nome = %s', 'value': (codigo_linha, current_user.primary_key)})

    if relacao and relacao[permission]:
        return codigo_linha
    return False
