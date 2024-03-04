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


def return_route(code_line, surname, shift, time_par, time_ret, pos):
  if surname == 'Não definido' or surname == 'Nenhum' or surname == 'Sem veículo':
    surname = None
  
  keys = db.session.query(Rota.codigo).filter_by(Linha_codigo=code_line).subquery()
  not_include = (
    db.session.query(Marcador_Exclusao.key_item)
    .filter(db.and_(
      Marcador_Exclusao.tabela == 'Rota',
      Marcador_Exclusao.key_item.in_(keys.select())
    ))
    .subquery()
  )

  if surname:
    rota = (
      db.session.query(Rota).join(Onibus)
      .filter(db.and_(
        db.not_(Rota.codigo.in_(not_include.select())),
        Onibus.apelido == surname,
        Rota.Linha_codigo == code_line,
        Rota.horario_partida == format_time(time_par, reverse=True),
        Rota.horario_retorno == format_time(time_ret, reverse=True),
        Rota.turno == shift
      ))
      .all()
    )
  else:
    rota = (
      db.session.query(Rota)
      .filter(db.and_(
        db.not_(Rota.codigo.in_(not_include.select())),
        Rota.Onibus_id.is_(None),
        Rota.Linha_codigo == code_line,
        Rota.horario_partida == format_time(time_par, reverse=True),
        Rota.horario_retorno == format_time(time_ret, reverse=True),
        Rota.turno == shift
      ))
      .all()
    )

  if rota:
    if len(rota) > 1:
      if pos and isinstance(pos, str) and pos.isdigit():
        return rota[int(pos)]
      return False
    return rota[0]
  return None


def return_options_route(linha, user):
  retorno = []
  rotas = (
    db.session.query(Rota, Onibus)
    .filter(db.and_(
      Rota.turno == user.turno,
      Rota.Linha_codigo == linha.codigo,
      Rota.Onibus_id == Onibus.id,
      db.not_(Onibus.Motorista_id.is_(None))
    ))
    .order_by(Rota.horario_partida)
    .all()
  )

  for value in rotas:
    rota, onibus = value
    motorista_nome = onibus.motorista.nome

    dados = {
      'motorista': motorista_nome,
      'apelido': onibus.apelido,
      'turno': rota.turno,
      'horario_partida': format_time(rota.horario_partida),
      'horario_retorno': format_time(rota.horario_retorno),
      'quantidade': count_part_route(rota, formated=False)
    }
    retorno.append(dados)
  
  return retorno


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


def check_times(vehicle_id, time=[]):
  if vehicle_id:
    if (
      Rota.query.filter(db.and_(
        Rota.Onibus_id == vehicle_id,
        db.or_(
          Rota.horario_partida.in_(time),
          Rota.horario_retorno.in_(time)
        ) 
      ))
      .first()
    ):
      return True
  return False


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~ Count ~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

def count_list(list: list, name_format: str, list_unique=True):
  quantidade = 0
  if not list_unique:
    for value in list:
      quantidade += len(value)
  else: quantidade = len(list)

  if quantidade != 1:
    name_format += 's'
  return f'{quantidade} {name_format}'


def count_part_route(route, formated=True):
  quantidade = (db.session.query(func.count(func.distinct(Passagem.Aluno_id)))
    .join(Parada)
    .filter(
      db.and_(
        Passagem.passagem_fixa == True,
        Passagem.Parada_codigo == Parada.codigo,
        Parada.Rota_codigo == route.codigo
      )
    )
    .scalar()
  )
  if not quantidade: quantidade = 0
  if formated:
    return f"{quantidade} {'pessoa' if quantidade == 1 else 'pessoas'}"
  return quantidade
