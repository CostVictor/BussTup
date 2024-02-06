from flask_security import current_user
from app import cursos, turnos
from sqlalchemy import func
from app.database import *
import bcrypt


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~ Format ~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def format_money(value):
    if value: return str(value).replace('.', ',')
    return '--'


def format_time(time, reverse=False):
    if reverse:
        time = time.replace('h', '').strip()
        time = time.split(':')
        if len(time) == 1:
            return f'{time[0]}:00'
        return ':'.join(time)

    hr = time.strftime('%H')
    mn = time.strftime('%M')

    if int(mn) != 0:
        return f'{hr}:{mn} h'
    return f'{hr} h'


def format_data():...


def capitalize(name, role):
    name = name.split(' ')
    if role != 'motorista' and len(name) < 3:
        return False

    for index, palavra in enumerate(name):
        if palavra:
            palavra = palavra.lower()
            if palavra != 'da' and palavra != 'do' and palavra != 'de':
                palavra = palavra.capitalize()
            name[index] = palavra
            
    return ' '.join(name)


def format_register(dadosAdquiridos):
    inconsistencia = False
    erro_title = 'Cadastro Interrompido'
    erro_text = ''

    if 'data' in dadosAdquiridos:
        data = dadosAdquiridos['data']

        if 'curso' in data or 'turno' in data:
            data['role'] = 'aluno'
        else: data['role'] = 'motorista'

        if 'login' in data and len(data['login']) >= 10 and 'password' in data and len(data['password']) >= 10:
            senha = data.pop('password').encode('utf-8')
            data['password_hash'] = bcrypt.hashpw(senha, bcrypt.gensalt())
        else:
            erro_text = 'Ocorreu um erro inesperado ao realizar o cadastro. Por favor, revise os dados e tente novamente.'
            inconsistencia = True

        if not inconsistencia:
            for campo, dado in data.items():
                if campo == 'login':
                    if not check_dis_login(dado):
                        erro_text = 'O nome de usuário definido não atende aos critérios de cadastro para ser utilizado como login. Por favor, escolha outro nome.'
                        inconsistencia = True
                        break

                elif campo == 'nome':
                    name = capitalize(dado, data['role'])

                    if not name:
                        erro_text = 'O nome definido não atende aos critérios de cadastro do aluno. Por favor, defina seu nome completo.'
                        inconsistencia = True
                        break
                
                    data[campo] = name
                
                elif campo == 'curso':
                    if not dado in cursos:
                        erro_text = 'O curso definido não está presente entre as opções disponíveis.'
                        inconsistencia = True
                        break
                        
                elif campo == 'turno':
                    if not dado in turnos:
                        erro_text = 'O turno definido não está presente entre as opções disponíveis.'
                        inconsistencia = True
                        break
    else: return None

    return inconsistencia, erro_title, erro_text, data


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~ Return ~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def return_dict(obj, not_includes=[]):
    return {name: value for name, value in vars(obj).items() if name not in not_includes and not name.startswith('_')}


def return_relationship(code_line):
    if code_line:
        if current_user.roles[0].name == 'aluno':
            passagem = Passagem.query.filter_by(
                Aluno_id=current_user.primary_key,
                passagem_fixa=True,
                passagem_contraturno=False
            ).first()

            if passagem:
                line = passagem.parada.ponto.linha
                if line.codigo == code_line:
                    relationship = 'participante'
                else: relationship = 'não participante'
            else: relationship = None
        else:
            relationship = Membro.query.filter_by(Motorista_id=current_user.primary_key, Linha_codigo=code_line).first()
            if relationship:
                if relationship.dono:
                    relationship = 'dono'
                elif relationship.adm:
                    relationship = 'adm'
                else: relationship = 'membro'
            else: relationship = None
        return relationship
    return None


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~ Check ~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

def check_permission(data, permission='adm'):
    if data and 'name_line' in data:
        code_line = Linha.query.filter_by(nome=data['name_line']).first()
        if code_line:
            code_line = code_line.codigo
            relationship = Membro.query.filter_by(Motorista_id=current_user.primary_key, Linha_codigo=code_line).first()
            if relationship:
                if permission == 'dono':
                    if relationship.dono and 'password' in data:
                        if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.password_hash):
                            data['Linha_codigo'] = code_line
                            del data['name_line']
                            return 'autorizado'
                        return 'senha incorreta'
                else:
                    if relationship.adm:
                        data['Linha_codigo'] = code_line
                        del data['name_line']
                        return 'autorizado'
    return 'não autorizado'


def count_part_route(route):
    quantidade = (db.session.query(func.count(func.distinct(Passagem.Aluno_id)))
        .filter(
            db.and_(
                Passagem.Parada_Ponto_id.in_([ponto.id for ponto in route.pontos]),
                Passagem.passagem_fixa == True
            )
        )
        .scalar()
    )
    if not quantidade: quantidade = 0
    return quantidade
