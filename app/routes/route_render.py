from flask import render_template, request, jsonify, flash
from flask_security import current_user, login_required
from app import app, cursos, turnos, cidades, dias_semana
from flask_jwt_extended import decode_token, get_jwt_identity, get_jwt
from app.database import *
from app.forms import *
import bcrypt


@app.route("/")
@app.route("/index")
@app.route("/login")
def index():
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


@app.route("/line/<name_line>")
@login_required
def pag_linha(name_line):
  local_page = request.args.get('local_page')
  linha = Linha.query.filter_by(nome=name_line).first()

  if linha and not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
    role = current_user.roles[0].name
    return render_template('blog/line.html', name_line=name_line, role=role, turnos=turnos, cidades=cidades, local_page=local_page)
  return 'Linha não encontrada.'


@app.route("/profile_user")
@login_required
def perfil_usuario():
  local_page = request.args.get('local_page')
  role = current_user.roles[0].name
  return render_template('blog/profile_user.html', role=role, local_page=local_page)


@app.route("/recover/<token>", methods=['GET', 'POST'])
def recuperar(token):
  try:
    decode = decode_token(token)
    user = User.query.filter_by(id=decode['identity']).first()

    if user:
      check_token = AccessToken.query.filter_by(
        User_id=user.id, type='recuperacao', token=token, valid=True
      ).first()

      if check_token:
        if decode['dado'] == 'usuario':
          form = FormReplaceUser()

          if form.validate_on_submit():
            new_user = form.data.novo_usuario

            if check_dis_login(new_user):
              try:
                user.login = new_user
                check_token.valid = False
                db.session.commit()
                flash('Seu usuário foi alterado com sucesso.', 'success')

              except Exception as e:
                db.session.rollback()
                print(f'Erro ao alterar o dado do usuário: {str(e)}')
            
            flash('O nome de usuário definido não atende aos critérios de cadastro para ser utilizado como login. Por favor, escolha outro nome.', 'info')

        else:
          form = FormReplacePassword()

          if form.validate_on_submit():
            new_password = form.data.nova_senha
            try:
              user.password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), bcrypt.gensalt()
              )
              check_token.valid = False
              db.session.commit()
              flash('Sua senha foi alterada com sucesso.', 'success')

            except Exception as e:
              db.session.rollback()
              print(f'Erro ao alterar o dado do usuário: {str(e)}')

        return render_template("blog/recover.html", token=token, form=form, dado=decode['dado'])
      
    return jsonify({'mensagem': 'Token inválido'}), 401
  
  except:
    check = AccessToken.query.filter_by(token=token).first()
    if check:
      try:
        check.valid = False
        db.session.commit()

      except Exception as e:
        print(f'Erro ao invalidar o token: {str(e)}')

    return jsonify({'mensagem': 'Token inválido'}), 401
