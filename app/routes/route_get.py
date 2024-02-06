from flask_security import login_required, roles_required, current_user
from flask import request, jsonify
from app.utilities import *
from app.database import *
from app import app


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Profile ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_profile", methods=['GET'])
@login_required
def get_perfil():
    data = {}
    role = current_user.roles[0].name
    user = return_my_user()

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


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~ GET Page user ~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_association", methods=['GET'])
@login_required
def get_association():
    response = {'conf': True}

    if current_user.roles[0].name == 'aluno':
        if Passagem.query.filter_by(
            Aluno_id=current_user.primary_key,
            passagem_fixa=True,
            passagem_contraturno=False
        ).first():
            response['conf'] = True
    else:
        user = return_my_user()
        if user and user.linhas:
            response['conf'] = True

    return jsonify(response)


@app.route("/get_lines", methods=['GET'])
@login_required
def get_lines():
    role = current_user.roles[0].name
    data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}
    query = Membro.query.filter_by(dono=True).join(Linha).order_by(Linha.nome).all()

    if query:
        user = return_my_user()
        if role == 'aluno':
            passagem = Passagem.query.filter_by(
                Aluno_id=user.id,
                passagem_fixa=True,
                passagem_contraturno=False
            ).first()
            if passagem:
                data['minha_linha'] = passagem.parada.ponto.linha.nome
        
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


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~ GET Interface Line ~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

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
        
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver", methods=['GET'])
@login_required
def get_interface_driver():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relacoes = Membro.query.filter_by(Linha_codigo=linha.codigo).all()
            motoristas = {}
            retorno = {
                'error': False,
                'role': current_user.roles[0].name, 
                'relacao': return_relationship(linha.codigo),
                'data': motoristas
            }

            for relacao in relacoes:
                motorista = relacao.motorista
                dict_motorista = return_dict(motorista, not_includes=['id', 'email', 'pix'])

                if relacao.dono:
                    if 'dono' not in motoristas:
                        motoristas['dono'] = []

                    dict_dono = return_dict(motorista, not_includes=['id', 'email'])
                    motoristas['dono'].append(dict_dono)

                    if not motorista.pix:
                        dict_dono['pix'] = 'Não definido'
                
                elif relacao.adm:
                    if 'adm' not in motoristas:
                        motoristas['adm'] = []
                    motoristas['adm'].append(dict_motorista)
                
                else:
                    if 'membro' not in motoristas:
                        motoristas['membro'] = []
                    motoristas['membro'].append(dict_motorista)
            
            return jsonify(retorno)
            
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-veicle", methods=['GET'])
@login_required
@roles_required("motorista")
def get_interface_veicle():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        user = return_my_user()
        if linha and user:
            retorno = {
                'error': False, 
                'relacao': return_relationship(linha.codigo),
                'meu_nome': user.nome,
                'data': []
            }
            veicles = Onibus.query.filter_by(Linha_codigo=linha.codigo).order_by(Onibus.placa).all()
            for veicle in veicles:
                dict_veicle = return_dict(veicle, not_includes=['Linha_codigo', 'Motorista_id'])
                dict_veicle['motorista_nome'] = veicle.motorista.nome if veicle.motorista else 'Nenhum'
                retorno['data'].append(dict_veicle)
            
            return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-points", methods=['GET'])
@login_required
@roles_required("motorista")
def get_interface_points():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
            pontos = Ponto.query.filter_by(Linha_codigo=linha.codigo).order_by(Ponto.nome).all()
            data = [ponto.nome for ponto in pontos]
            quantidade = len(data)

            retorno['quantidade'] = f"{quantidade} {'cadastrado' if quantidade == 1 else 'cadastrados'}"
            retorno['data'] = data
            return retorno
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-routes", methods=['GET'])
@login_required
def get_interface_route():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            rotas = Rota.query.filter_by(Linha_codigo=linha.codigo).order_by(Rota.horario_partida).all()
            retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
            retorno['ativas'] = []; retorno['desativas'] = []
            retorno['role'] = current_user.roles[0].name

            for rota in rotas:
                quantidade_alunos = count_part_route(rota)
                quantidade_alunos = f"{quantidade_alunos} {'pessoa' if quantidade_alunos == 1 else 'pessoas'}"
                info = {
                    'turno': rota.turno,
                    'horario_partida': format_time(rota.horario_partida),
                    'horario_retorno': format_time(rota.horario_retorno),
                    'quantidade': quantidade_alunos
                }

                veiculo = rota.onibus
                placa = 'Sem veículo'
                motorista = 'Desativada'

                if veiculo:
                    placa = veiculo.placa
                    motorista = 'Nenhum'
                    if veiculo.motorista:
                        motorista = veiculo.motorista.nome
                    retorno['ativas'].append(info)
                else: retorno['desativas'].append(info)

                info['placa'] = placa
                info['motorista'] = motorista

            quantidade_rotas = len(retorno['ativas']) + len(retorno['desativas'])
            retorno['quantidade'] = f"{quantidade_rotas} {'cadastrada' if quantidade_rotas == 1 else 'cadastradas'}"

            if retorno['role'] == 'aluno':
                del retorno['quantidade']
                del retorno['desativas']

            return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Options ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

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
                    if not Onibus.query.filter_by(Motorista_id=current_user.primary_key, Linha_codigo=linha.codigo).first():
                        user = return_my_user()
                        return jsonify({'error': False, 'data': user.nome})
                    return jsonify({'error': False, 'data': None})

                not_includes = db.session.query(Onibus.Motorista_id).filter(
                    db.and_(Onibus.Linha_codigo == linha.codigo, Onibus.Motorista_id.isnot(None))
                ).subquery()
                
                query = db.session.query(Membro).filter(
                    db.and_(
                        Membro.Linha_codigo == linha.codigo,
                        db.not_(Membro.Motorista_id.in_(not_includes.select()))
                    )
                ).all()
                retorno = [result.motorista.nome for result in query]

                return jsonify({'error': False, 'data': retorno})

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_veicle", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_veicle():
    name_line = request.args.get('name_line')
    if name_line:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relacao = return_relationship(linha.codigo)
            if relacao and relacao != 'membro':
                retorno = {'error': False, 'data': []}

                for onibus in linha.onibus:
                    motorista = onibus.motorista.nome if onibus.motorista else 'Nenhum'
                    retorno['data'].append(f"{onibus.placa} > {motorista}")
                
                return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ GET Config ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_point", methods=['GET'])
@login_required
@roles_required("motorista")
def get_point():
    name_line = request.args.get('name_line')
    name_point = request.args.get('name_point')

    if name_line and name_point:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relationship = return_relationship(linha.codigo)
            if relationship:
                ponto = Ponto.query.filter_by(nome=name_point, Linha_codigo=linha.codigo).first()
                if ponto:
                    retorno = {'error': False, 'relacao': relationship, 'turnos': {}}
                    dict_ponto = return_dict(ponto, not_includes=['id', 'Linha_codigo'])
                    retorno['info'] = dict_ponto
                    retorno['utilizacao'] = {'rotas': []}
                    retorno['turnos']['Matutino'] = {'alunos': []}
                    retorno['turnos']['Vespertino'] = {'alunos': []}
                    retorno['turnos']['Noturno'] = {'alunos': []}
                    
                    if not dict_ponto['linkGPS']:
                        dict_ponto['linkGPS'] = 'Não definido'
                    
                    for relacao_rotas in ponto.rotas:
                        rota = relacao_rotas.rota

                        if rota.tipo == 'partida':
                            veiculo = rota.onibus
                            motorista = 'Nenhum'
                            placa = 'Não definido'
                            if veiculo:
                                placa = veiculo.placa
                                if veiculo.motorista:
                                    motorista = veiculo.motorista.nome

                            dados = {
                                'motorista': motorista,
                                'onibus': placa,
                                'turno': rota.turno,
                                'partida': format_time(rota.horario_partida),
                                'retorno': format_time(rota.horario_retorno)
                            }
                            retorno['utilizacao']['rotas'].append(dados)

                    quantidade_utilizacao = len(retorno['utilizacao']['rotas'])
                    retorno['utilizacao']['quantidade'] = f"{quantidade_utilizacao} {'rota' if quantidade_utilizacao == 1 else 'rotas'}"

                    alunos = db.session.query(Aluno).join(Passagem).filter(
                        db.and_(
                            Aluno.id == Passagem.Aluno_id,
                            Passagem.Parada_Ponto_id == ponto.id
                        )
                    ).order_by(Aluno.nome).all()

                    for aluno in alunos:
                        retorno['turnos'][aluno.turno].append(aluno.nome)
                    
                    quantidade_matutino = len(retorno['turnos']['Matutino']['alunos'])
                    quantidade_vespertino = len(retorno['turnos']['Vespertino']['alunos'])
                    quantidade_noturno = len(retorno['turnos']['Noturno']['alunos'])

                    retorno['turnos']['Matutino']['quantidade'] = f"{quantidade_matutino} {'cadastrado' if quantidade_matutino == 1 else 'cadastrados'}"
                    retorno['turnos']['Vespertino']['quantidade'] = f"{quantidade_vespertino} {'cadastrado' if quantidade_vespertino == 1 else 'cadastrados'}"
                    retorno['turnos']['Noturno']['quantidade'] = f"{quantidade_noturno} {'cadastrado' if quantidade_noturno == 1 else 'cadastrados'}"

                    return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações do ponto.'})


@app.route("/get_route", methods=['GET'])
@login_required
def get_route():
    name_line = request.args.get('name_line')
    plate = request.args.get('plate')
    shift = request.args.get('shift')
    hora_partida = request.args.get('time_par')
    hora_retorno = request.args.get('time_ret')
    pos = request.args.get('pos')

    if name_line and shift and hora_partida and hora_retorno:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relationship = return_relationship(linha.codigo)
            role = current_user.roles[0].name
            retorno = {'error': False, 'role': role, 'relacao': relationship}
            retorno['data'] = {'partida': {}, 'retorno': {}}
            retorno['msg_desativada'] = False

            if plate == 'Sem veículo':
                plate = None

            user = return_my_user()
            if plate:
                rota = Rota.query.filter_by(
                    Onibus_placa=plate,
                    Linha_codigo=linha.codigo,
                    horario_partida=format_time(hora_partida, reverse=True),
                    horario_retorno=format_time(hora_retorno, reverse=True),
                    turno=shift
                ).all()
            else:
                rota = Rota.query.filter(
                    Rota.Onibus_placa.is_(None),
                    Rota.Linha_codigo == linha.codigo,
                    Rota.horario_partida == format_time(hora_partida, reverse=True),
                    Rota.horario_retorno == format_time(hora_retorno, reverse=True),
                    Rota.turno == shift
                ).all()

            if rota and user:  
                if len(rota) > 1:
                    if pos: rota = rota[int(pos)]
                    else: return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
                else: rota = rota[0]

                veiculo = rota.onibus
                motorista = 'Nenhum'
                placa = 'Não definido'
                if veiculo:
                    placa = veiculo.placa
                    if veiculo.motorista:
                        motorista = veiculo.motorista.nome
                else: retorno['msg_desativada'] = True
                        
                retorno['info'] = {
                    'motorista': motorista,
                    'onibus': placa,
                    'turno': rota.turno,
                    'partida': format_time(rota.horario_partida),
                    'retorno': format_time(rota.horario_retorno)
                }

                if role == 'aluno':
                    retorno['meu_turno'] = user.turno
                    retorno['msg_cadastrar'] = False
                    retorno['msg_contraturno'] = False

                    if user.turno == rota.turno:
                        retorno['meus_pontos'] = {}
                        passagens = Passagem.query.filter_by(
                            Parada_Rota_codigo=rota.codigo,
                            Aluno_id=current_user.primary_key,
                            passagem_contraturno=False,
                            passagem_fixa=True
                        ).all()

                        if passagens:
                            for passagem in passagens:
                                parada = passagem.parada
                                ponto = parada.ponto
                                retorno['meus_pontos'][parada.tipo] = ponto.nome
                        else: retorno['msg_cadastrar'] = True
                    else:
                        retorno['meu_contraturno'] = None
                        nome = db.session.query(Ponto.nome).join(Passagem).filter(
                            db.and_(
                                Passagem.Parada_Rota_codigo == rota.codigo,
                                Passagem.Aluno_id == current_user.primary_key,
                                Passagem.passagem_contraturno == True,
                                Passagem.passagem_fixa == True
                            )
                        ).first()

                        if nome:
                            retorno['meu_contraturno'] = nome
                        else: retorno['msg_contraturno'] = True

                paradas_partida = db.session.query(Ponto.nome).join(Parada).filter(
                    db.and_(
                        Ponto.id == Parada.Ponto_id,
                        Parada.Rota_codigo == rota.codigo,
                        Parada.tipo == 'partida'
                    )
                ).order_by(Parada.ordem).all()
                retorno['data']['partida']['paradas'] = paradas_partida
                retorno['data']['partida']['quantidade'] = f"{len(paradas_partida)} {'definido' if len(paradas_partida) == 1 else 'definidos'}"

                paradas_retorno = db.session.query(Ponto.nome).join(Parada).filter(
                    db.and_(
                        Ponto.id == Parada.Ponto_id,
                        Parada.Rota_codigo == rota.codigo,
                        Parada.tipo == 'retorno'
                    )
                ).order_by(Parada.ordem).all()
                retorno['data']['retorno']['paradas'] = paradas_partida
                retorno['data']['retorno']['quantidade'] = f"{len(paradas_retorno)} {'definido' if len(paradas_retorno) == 1 else 'definidos'}"

                return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações da rota.'})
