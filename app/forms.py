from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class FormConfirm(FlaskForm):
  usuario = StringField('Usuário', validators=[DataRequired()])
  senha = PasswordField('Senha', validators=[DataRequired(), Length(min=10)])
  botao = SubmitField('Confirmar')


class FormReplaceUser(FlaskForm):
  novo_usuario = StringField('Novo usuário de Login', validators=[DataRequired(), Length(min=10)])
  botao = SubmitField('Salvar')


class FormReplacePassword(FlaskForm):
  nova_senha = PasswordField('Nova senha', validators=[DataRequired(), Length(min=10)])
  senha_conf = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('nova_senha', message='A senha de confirmação é diferente da senha definida.')])
  botao = SubmitField('Salvar')
