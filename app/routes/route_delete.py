from flask_security import login_required, roles_required
from flask import request, jsonify
from app.utilities import *
from app.database import *
from app import app


@app.route("/del_myPoint_fixed/<type>", methods=['DELETE'])
@login_required
@roles_required("aluno")
def del_myPoint_fixed(type):
  user = return_my_user()

  if user and type:
    passagem = (
      db.session.query(Passagem).join(Parada)
      .filter(db.and_(
        Passagem.Aluno_id == user.id,
        Passagem.passagem_fixa == True,
        Passagem.passagem_contraturno == False,
        Parada.tipo == type
      ))
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
