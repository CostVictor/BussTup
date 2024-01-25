from flask_security import login_required, roles_required, current_user
from flask import request, jsonify
from app.utilities import return_dict, return_relationship, format_money
from sqlalchemy.orm import aliased
from app.database import *
from app import app


@app.route("/get_association", methods=['GET'])
@login_required
def get_association():
    response = {'conf': True}

    user = return_user(current_user.primary_key)
    if user:
        if current_user.roles[0].name == 'aluno':
            if user.associacao:
                response['conf'] = True
        else:
            if user.linhas:
                response['conf'] = True

    return jsonify(response)


@app.route("/get_profile", methods=['GET'])
@login_required
def get_perfil():
    data = {}
    role = current_user.roles[0].name
    user = return_user(current_user.primary_key)

    data['nome'] = user.nome
    data['telefone'] = user.telefone
    data['email'] = user.email

    if role == 'aluno':
        data['curso'] = user.curso
        data['turno'] = user.turno
    else:
        data['pix'] = user.pix
        
        if not data['pix']:
            data['pix'] = 'Não definido'

    return jsonify(data)


@app.route("/get_lines", methods=['GET'])
@login_required
def get_lines():
    role = current_user.roles[0].name
    data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}
    query = Linha_has_Motorista.query.filter_by(motorista_dono=True).join(Linha).order_by(Linha.nome).all()

    if query:
        user = return_user(current_user.primary_key)
        if role == 'aluno':
            if user.associacao:
                data['minha_linha'] = user.associacao[0].ponto.linha.nome
        
        for result in query:
            linha = result.linha
            dict_linha = {'nome': linha.nome, 'ferias': linha.ferias, 'paga': linha.paga}

            if linha.cidade not in data['cidades']:
                data['cidades'][linha.cidade] = []
        
            data['cidades'][linha.cidade].append(dict_linha)
            dict_linha['dono'] = result.motorista.nome

            if role == 'motorista' and dict_linha['dono'] == user.nome:
                data['minha_linha'].append(dict_linha)
            
    else: data['identify'] = False
    return jsonify(data)


@app.route("/get_interface-line", methods=['GET'])
@login_required
def get_interface_line():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            retorno = {'error': False, 'role': current_user.roles[0].name, 'relacao': return_relationship(linha.codigo)}
            data = return_dict(linha, not_includes=['codigo'])

            data['valor_cartela'] = format_money(linha.valor_cartela)
            data['valor_diaria'] = format_money(linha.valor_diaria)
            retorno['data'] = data

            return jsonify(retorno)
        
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver", methods=['GET'])
@login_required
def get_interface_driver():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relacoes = Linha_has_Motorista.query.filter_by(Linha_codigo=linha.codigo).all()
            motoristas = {}
            retorno = {
                'error': False,
                'role': current_user.roles[0].name, 
                'relacao': return_relationship(linha.codigo),
                'data': motoristas
            }

            for relacao in relacoes:
                motorista = relacao.motorista
                dict_motorista = return_dict(motorista, not_includes=['login', 'email', 'pix'])

                if relacao.motorista_dono:
                    if 'dono' not in motoristas:
                        motoristas['dono'] = []

                    dict_dono = return_dict(motorista, not_includes=['login', 'email'])
                    motoristas['dono'].append(dict_dono)

                    if not motorista.pix:
                        dict_dono['pix'] = 'Não definido'
                
                elif relacao.motorista_adm:
                    if 'adm' not in motoristas:
                        motoristas['adm'] = []
                    motoristas['adm'].append(dict_motorista)
                
                else:
                    if 'membro' not in motoristas:
                        motoristas['membro'] = []
                    motoristas['membro'].append(dict_motorista)
            
            return jsonify(retorno)
            
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_driver", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_driver():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relacao = return_relationship(linha.codigo)
            if relacao:
                if relacao == 'membro':
                    if not Onibus.query.filter_by(Motorista_login=current_user.primary_key, Linha_codigo=linha.codigo).first():
                        user = return_user(current_user.primary_key)
                        return jsonify({'error': False, 'data': user.nome})
                    return jsonify({'error': False, 'data': None})

                not_includes = db.session.query(Onibus.Motorista_login).filter(
                    db.and_(Onibus.Linha_codigo == linha.codigo, Onibus.Motorista_login.isnot(None))
                ).subquery()
                
                query = db.session.query(Linha_has_Motorista).filter(
                    db.and_(
                        Linha_has_Motorista.Linha_codigo == linha.codigo,
                        db.not_(Linha_has_Motorista.Motorista_login.in_(not_includes.select()))
                    )
                ).all()
                retorno = [result.motorista.nome for result in query]

                return jsonify({'error': False, 'data': retorno})

    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-veicle", methods=['GET'])
@login_required
def get_interface_veicle():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        user = return_user(current_user.primary_key)
        if linha and user:
            retorno = {
                'error': False, 
                'relacao': return_relationship(linha.codigo),
                'meu_nome': user.nome,
                'data': []
            }
            veicles = Onibus.query.filter_by(Linha_codigo=linha.codigo).order_by(Onibus.placa).all()
            for veicle in veicles:
                dict_veicle = return_dict(veicle, not_includes=['Linha_codigo', 'Motorista_login'])
                dict_veicle['motorista_nome'] = veicle.motorista.nome if veicle.motorista else 'Nenhum'
                retorno['data'].append(dict_veicle)
            
            return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})
