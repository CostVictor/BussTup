from flask_security import login_required, roles_required
from flask import request, jsonify
from app.utilities import *
from app.database import *
from app import app


@app.route("/del_point_fixed", methods=['DELETE'])
@login_required
@roles_required("aluno")
def check_register_in():
  data = request.get_json()
  user = return_my_user()

  if user and data and 'type' in data:
    passagem = (
      Passagem.query.filter_by(
        Aluno_id=user.id,
        tipo=data['type'],
        passagem_fixa=True,
        passagem_contraturno=False
      )
      .first()
    )
    
    if passagem:
      try:
        db.session.delete(passagem)
        db.session.commit()
        return jsonify({'error': False, 'title': 'Remoção Concluída', 'text': ''})

      except Exception as e:
        db.session.rollback()
        print(f'Erro ao criar a passagem: {str(e)}')

  return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar excluir a passagem.'})
