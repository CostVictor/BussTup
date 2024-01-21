from app.database import db
from datetime import timedelta, datetime
from flask_security import current_user
import bcrypt, numpy as np

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


def formatData(dadosAdquiridos):
    if dadosAdquiridos:
        inconsistencia = False
        erro_titulo = ''
        erro_texto = ''

        tabela = dadosAdquiridos['table']
        data = dadosAdquiridos['data']

        for campo, dado in data.items():
            if campo == 'login':...

            elif campo == 'nome':...

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


def check_permission(data, permission='motorista_adm'):
    code_line = db.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['name_line']})
    if code_line:
        relacao = db.select('Linha_has_Motorista', where={'where': 'Linha_codigo = %s AND Motorista_nome = %s', 'value': (code_line['codigo'], current_user.primary_key)})

        if relacao and relacao[permission]:
            data['code_line'] = code_line['codigo']
            if permission == 'motorista_dono':
                if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.hash_senha):
                    return 'autorizado'
                return 'senha incorreta'
            return 'autorizado'
    return 'nao autorizado'
