from flask_security import current_user
from app import cursos, turnos
from sqlalchemy import func
from datetime import date, timedelta, datetime
from app import dias_semana
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


def format_date(data, reverse=False):
  if reverse:
    today = date.today()
    data = data.split('/')

    if today.month == 12:
      year = (today.year + 1) if data[1] == '01' else today.year
    else: year = today.year

    return date(year, int(data[1]), int(data[0]))

  return str(data.day).zfill(2) + '/' + str(data.month).zfill(2)


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
        
        elif campo == 'email':
          if return_user_email(dado):
            erro_text = 'O e-mail definido não está disponível para utilização.'
            inconsistencia = True
            break
  else: return None

  return inconsistencia, erro_title, erro_text, data


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~ Return ~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def return_dates_week(only_valid=False):
  today = date.today()
  week_day = today.weekday()

  if week_day == 5 or week_day == 6:
    day_reference = today + timedelta(days=(7 - week_day))
  else: day_reference = today - timedelta(days=week_day)

  dates = []
  for index in range(5):
    value = day_reference + timedelta(days=index)
    if only_valid:
      if value >= today:
        dates.append(value)
    else:
      dates.append(value)

  return dates


def return_dict(obj, not_includes=[]):
  return {name: value for name, value in vars(obj).items() if name not in not_includes and not name.startswith('_')}


def return_str_bool(boolean: bool):
  if boolean: return 'Sim'
  return 'Não'


def return_day_week(value: str | int, reverse=False):
  if reverse:
    return dias_semana.index(value)
  return dias_semana[value]


def return_relationship(code_line):
  if code_line:
    if current_user.roles[0].name == 'aluno':
      passagem = (
        Passagem.query.filter_by(
        Aluno_id=current_user.primary_key,
        passagem_fixa=True
        )
        .first()
      )

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

      check = check_myRoute(shift)
      if check:
        return check
      
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
    .order_by(Rota.horario_partida, Onibus.apelido)
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
      'quantidade': count_part_route(rota.codigo, formated=False)
    }
    retorno.append(dados)
  
  return retorno


def return_ignore_route(shift):
  if shift == 'Matutino':
    return 'retorno'
  return 'partida'


def return_user_email(email: str):
  check_aluno = Aluno.query.filter_by(email=email).first()
  check_motorista = Motorista.query.filter_by(email=email).first()
  retorno = {}

  if check_aluno:
    retorno['principal'] = check_aluno
    retorno['sessao'] = (
      User.query.filter_by(primary_key=check_aluno.id)
      .first()
    )

  elif check_motorista:
    retorno['principal'] = check_motorista
    retorno['sessao'] = (
      db.session.query(User)
      .filter_by(primary_key=check_motorista.id)
      .first()
    )
  
  if retorno:
    return retorno
  return None


def return_stop_atual(route, type_):
  all_stops = (
    db.session.query(Parada)
    .filter(db.and_(
      Parada.Rota_codigo == route.codigo,
      Parada.tipo == type_
    ))
    .order_by(Parada.ordem)
    .all()
  )

  if all_stops:
    stops_passou = (
      db.session.query(Parada).join(Registro_Passagem)
      .filter(db.and_(
        Registro_Passagem.Parada_codigo == Parada.codigo,
        Parada.Rota_codigo == route.codigo,
        Parada.tipo == type_,
        Registro_Passagem.data == date.today(),
      ))
      .all()
    )
    if stops_passou:
      if len(stops_passou) == len(all_stops):
        return all_stops[-1]
      return all_stops[len(stops_passou) + 1]
    return all_stops[0]
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
        
        elif permission == 'adm' and 'password' in data:
          if relationship.adm:
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
  if vehicle_id and time:
    time_formated = []
    for value in time:
      time_formated.append(format_time(value, reverse=True))

    if (
      Rota.query.filter(db.and_(
        Rota.Onibus_id == vehicle_id,
        db.or_(
          Rota.horario_partida.in_(time_formated),
          Rota.horario_retorno.in_(time_formated)
        ) 
      ))
      .first()
    ):
      return True
  return False


def check_myRoute(shift):
  if current_user.roles[0].name == 'aluno':
    user = return_my_user()
    myRoute = (
      db.session.query(Rota).join(Parada).join(Passagem)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == True,
        Passagem.passagem_contraturno == (False if shift.capitalize() == user.turno else True)
      ))
      .first()
    )
    if myRoute:
      return myRoute
  return None


def check_valid_password(password: str):
  uper = False; lower = False
  number = False; simbol = False

  if len(password) >= 10:
    for c in password:
      if c.isupper():
        uper = True

      elif c.islower():
        lower = True
      
      elif c.isdigit():
        number = True
      
      elif not c.isalnum():
        simbol = True
  
  return (uper and lower and number and simbol)


def check_valid_datetime(date: datetime.date, time=False, add_limit=0):
  now = datetime.now()

  if date > now.date():
    return True
  
  elif date == now.date():
    if time:
      time_check = datetime.combine(date, time)
      if now <= time_check + timedelta(hours=add_limit):
        return True
    else: return True
  
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


def count_part_route(route_code, formated=True):
  quantidade = (db.session.query(func.count(func.distinct(Passagem.Aluno_id)))
    .join(Parada)
    .filter(
      db.and_(
        Passagem.passagem_fixa == True,
        Passagem.Parada_codigo == Parada.codigo,
        Parada.Rota_codigo == route_code
      )
    )
    .scalar()
  )
  if not quantidade: quantidade = 0
  if formated:
    return f"{quantidade} {'pessoa' if quantidade == 1 else 'pessoas'}"
  return quantidade


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Modify / Set ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def set_update_record_route(record):
  now = datetime.now()
  route = record.rota
  date = record.data
  type_ = record.tipo

  if now.date() < date:
    record.atualizar = True
  
  elif date == now.date():
    time = route.horario_partida if type_ == 'partida' else route.horario_retorno
    date_time = datetime.combine(now.date(), time)
    if now <= date_time + timedelta(hours=1):
      record.atualizar = True
    else: record.atualizar = False
  else: record.atualizar = False


def modify_forecast_route(route, record, commit=True):
  type_ = record.tipo
  day = record.data

  reject_contraturno = (type_ == return_ignore_route(route.turno))
  not_includes_daily = (
    db.session.query(func.distinct(Passagem.Aluno_id)).join(Parada).join(Rota)
    .filter(db.and_(
      Parada.Rota_codigo == Rota.codigo,
      Passagem.Parada_codigo == Parada.codigo,
      Rota.turno == route.turno,
      Parada.Rota_codigo != route.codigo,
      Parada.tipo == type_,
      Passagem.passagem_fixa == False,
      db.not_(db.or_(
        Passagem.migracao_lotado == True,
        Passagem.migracao_manutencao == True
      )),
      Passagem.data == day
    ))
    .subquery()
  )

  not_includes_migrate = (
    db.session.query(func.distinct(Passagem.Aluno_id))
    .join(Parada).join(Rota).join(Aluno).join(Registro_Aluno)
    .filter(db.and_(
      Parada.Rota_codigo == Rota.codigo,
      Passagem.Parada_codigo == Parada.codigo,
      Passagem.Aluno_id == Aluno.id,
      Registro_Aluno.Aluno_id == Aluno.id,
      Rota.turno == route.turno,
      Parada.Rota_codigo != route.codigo,
      Parada.tipo == type_,
      Passagem.passagem_fixa == False,
      db.or_(
        Passagem.migracao_lotado == True,
        Passagem.migracao_manutencao == True
      ),
      db.not_(db.or_(
        Registro_Aluno.faltara == True,
        db.and_(
          Registro_Aluno.contraturno == False,
          Aluno.turno != Rota.turno
        )
      )),
      Passagem.data == day,
      Registro_Aluno.data == day
    ))
    .subquery()
  )

  count = (
    db.session.query(func.count(func.distinct(Passagem.Aluno_id)))
    .join(Aluno).join(Registro_Aluno).join(Parada).join(Rota)
    .filter(db.and_(
      Rota.codigo == route.codigo,
      Parada.Rota_codigo == Rota.codigo,
      Parada.tipo == type_,

      Passagem.Parada_codigo == Parada.codigo,
      Aluno.id == Passagem.Aluno_id,
      Registro_Aluno.Aluno_id == Aluno.id,
      
      db.not_(db.or_(
        Aluno.id.in_(not_includes_daily.select()),
        db.and_(
          db.not_(db.and_(
            Passagem.passagem_fixa == False,
            Passagem.data == day
          )),
          Aluno.id.in_(not_includes_migrate.select())
        )
      )),
      Registro_Aluno.data == day,
      db.or_(
        db.and_(
          Passagem.passagem_fixa == True,
          Registro_Aluno.faltara == False,
          db.or_(
            (
              db.and_(
                Aluno.turno == route.turno,
                db.not_(Registro_Aluno.contraturno)
              )
              if reject_contraturno
              else (Aluno.turno == route.turno)
            ),
            db.and_(
              Aluno.turno != route.turno,
              Registro_Aluno.contraturno
            )
          )
        ),
        db.and_(
          db.not_(Passagem.passagem_fixa),
          Passagem.data == day,
          db.not_(db.and_(
            db.or_(
              Passagem.migracao_lotado == True,
              Passagem.migracao_manutencao == True
            ),
            db.or_(
              Registro_Aluno.faltara == True,
              db.and_(
                Registro_Aluno.contraturno == False,
                Aluno.turno != Rota.turno
              )
            )
          ))
        )
      )
    ))
    .scalar()
  )
  
  record.previsao_pessoas = count
  record.atualizar = False

  if commit:
    db.session.commit()
