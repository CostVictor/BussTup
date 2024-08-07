from flask import render_template, request, jsonify, flash
from flask_security import current_user, login_required
from app import app, cursos, turnos, cidades, dias_semana
from flask_jwt_extended import decode_token
from datetime import datetime
from app.utilities import *
from app.database import *
from app.tasks import *
from app.forms import *
import bcrypt


@app.route("/")
@app.route("/index")
@app.route("/login")
def index():
  if not sched.running:
    sched.start()
    sched.add_job('enviar_email', enviar_email, trigger='date', run_date=datetime.now())
    sched.add_job(
      None, transferir_por_defeito, trigger='date', 
      run_date=datetime.now(), max_instances=30
    )
  return render_template('auth/login.html')


@app.route("/register")
def cadastro():
  return render_template('auth/register.html', cursos=cursos, turnos=turnos)


@app.route("/page_user")
@login_required
def pag_usuario():
  abas = ['agenda', 'rota', 'linhas', 'chat']
  local = request.args.get('local')
  local = local if local and local in abas else 'agenda'

  role = current_user.roles[0].name
  return render_template('blog/page_user.html', role=role, turnos=turnos, dias_semana=dias_semana, cidades=cidades, local=local)


@app.route("/route/<name_line>/<surname>/<shift>/<time_par>/<time_ret>")
@login_required
def pag_rota(name_line, surname, shift, time_par, time_ret):
  local_page = request.args.get('local_page')
  linha = Linha.query.filter_by(nome=name_line).first()

  if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
    rota = return_route(linha.codigo, surname, shift, time_par, time_ret, None)
    if rota:
      user = return_my_user()
      role = current_user.roles[0].name
      relationship = return_relationship(linha.codigo)

      pass_daily = False
      if role == 'aluno':
        today = date.today()
        check_daily = (
          db.session.query(Parada).join(Passagem)
          .filter(db.and_(
            Passagem.Parada_codigo == Parada.codigo,
            Parada.Rota_codigo == rota.codigo,
            Passagem.data == today,
            Passagem.passagem_fixa == False,
            Passagem.Aluno_id == user.id
          ))
          .all()
        )
        if check_daily:
          for daily in check_daily:
            if check_valid_datetime(today, daily.horario_passagem, add_limit=0.25):
              pass_daily = True
              break
      
      if (relationship and relationship != 'não participante') or pass_daily:
        return render_template('blog/route.html', name_line=name_line, role=role, local_page=local_page, rota=rota, dias_semana=dias_semana, horario_partida=format_time(rota.horario_partida), horario_retorno=format_time(rota.horario_retorno))

  return 'Rota não encontrada.'


@app.route("/line/<name_line>")
@login_required
def pag_linha(name_line):
  local_page = request.args.get('local_page')
  linha = Linha.query.filter_by(nome=name_line).first()

  if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
    role = current_user.roles[0].name
    dates = [format_date(data) for data in return_dates_week()]

    return render_template('blog/line.html', name_line=name_line, role=role, turnos=turnos, dias_semana=dias_semana, cidades=cidades, dates=dates, local_page=local_page)
  
  return 'Linha não encontrada.'


@app.route("/profile_user")
@login_required
def perfil_usuario():
  local_page = request.args.get('local_page')
  role = current_user.roles[0].name
  return render_template('blog/profile_user.html', role=role, local_page=local_page)


@app.route("/recover/<token>", methods=['GET', 'POST'])
def recuperar(token):
  finalizado = False
  try:
    decode = decode_token(token)
    user = User.query.filter_by(id=decode['sub']).first()
    if user:
      check_token = AccessToken.query.filter_by(
        User_id=user.id, type='recuperacao', token=token
      ).first()

      if check_token:
        if decode['dado'] == 'usuario':
          texto = 'Defina seu novo usuário:'
          form = FormReplaceUser()

          if form.validate_on_submit():
            new_user = form.novo_usuario.data

            if check_dis_login(new_user):
              try:
                user.login = new_user
                db.session.delete(check_token)
                db.session.commit()
                finalizado = True

              except Exception as e:
                db.session.rollback()
                print(f'Erro ao alterar o dado do usuário: {str(e)}')
            
            else:
              flash('O nome de usuário definido não atende aos critérios de cadastro para ser utilizado como login. Por favor, escolha outro nome.', 'info')

        else:
          texto = 'Defina sua nova senha:'
          form = FormReplacePassword()

          if form.validate_on_submit():
            new_password = form.nova_senha.data
            if check_valid_password(new_password):
              try:
                user.password_hash = bcrypt.hashpw(
                  new_password.encode('utf-8'), bcrypt.gensalt()
                )
                db.session.delete(check_token)
                db.session.commit()
                finalizado = True

              except Exception as e:
                db.session.rollback()
                print(f'Erro ao alterar o dado do usuário: {str(e)}')

            else:
              flash('A senha especificada não é válida. Ela deve conter pelo menos uma letra maiúscula, uma letra minúscula, um número e um caractere especial.', 'info')
          
          else:
            if form.senha_conf.errors:
              flash('A senha especificada na confirmação é diferente da senha definida.')

        return render_template("blog/recover.html", token=token, form=form, texto=texto, dado=decode['dado'], finalizado=finalizado)
      
    return jsonify({'mensagem': 'Token inválido'}), 401
  
  except Exception as e:
    print(f'Erro ao validar o token: {str(e)}')
    check = AccessToken.query.filter_by(token=token).first()
    if check:
      try:
        db.session.delete(check)
        db.session.commit()

      except Exception as e:
        print(f'Erro ao invalidar o token: {str(e)}')

    return jsonify({'mensagem': 'Token inválido'}), 401



@app.route("/teste")
def teste():
  sched.add_job(
    None, transferir_por_defeito, trigger='date', 
    run_date=datetime.now(), max_instances=30
  )
  return ''
