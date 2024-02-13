from flask_security import login_required, roles_required, current_user
from flask import request, jsonify
from collections import deque
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

@app.route("/get_interface-line/<name_line>", methods=['GET'])
@login_required
def get_interface_line(name_line):
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
        retorno = {'error': False, 'role': current_user.roles[0].name, 'relacao': return_relationship(linha.codigo)}
        data = return_dict(linha, not_includes=['codigo', 'nome'])

        data['valor_cartela'] = format_money(linha.valor_cartela)
        data['valor_diaria'] = format_money(linha.valor_diaria)
        retorno['data'] = data

        return jsonify(retorno)
        
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver/<name_line>", methods=['GET'])
@login_required
def get_interface_driver(name_line):
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


@app.route("/get_interface-vehicle/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_interface_vehicle(name_line):
    linha = Linha.query.filter_by(nome=name_line).first()
    user = return_my_user()
    if linha and user:
        retorno = {
            'error': False, 
            'relacao': return_relationship(linha.codigo),
            'meu_nome': user.nome,
            'data': []
        }
        vehicles = Onibus.query.filter_by(Linha_codigo=linha.codigo).order_by(Onibus.placa).all()
        for vehicle in vehicles:
            dict_vehicle = return_dict(vehicle, not_includes=['Linha_codigo', 'Motorista_id'])
            dict_vehicle['motorista_nome'] = vehicle.motorista.nome if vehicle.motorista else 'Nenhum'
            retorno['data'].append(dict_vehicle)
        
        return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-points/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_interface_points(name_line):
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
        retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
        pontos = Ponto.query.filter_by(Linha_codigo=linha.codigo).order_by(Ponto.nome).all()
        data = [ponto.nome for ponto in pontos]

        retorno['quantidade'] = count_list(data, 'cadastrado')
        retorno['data'] = data
        return retorno
    
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-routes/<name_line>", methods=['GET'])
@login_required
def get_interface_route(name_line):
    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
        rotas = Rota.query.filter_by(Linha_codigo=linha.codigo).order_by(Rota.horario_partida).all()
        retorno = {'error': False, 'relacao': return_relationship(linha.codigo)}
        retorno['ativas'] = []; retorno['desativas'] = []
        retorno['role'] = current_user.roles[0].name

        for rota in rotas:
            info = {
                'turno': rota.turno,
                'horario_partida': format_time(rota.horario_partida),
                'horario_retorno': format_time(rota.horario_retorno),
                'quantidade': count_part_route(rota)
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
        retorno['quantidade'] = count_list([retorno['ativas'], retorno['desativas']], 'cadastrada', list_unique=False)

        if retorno['role'] == 'aluno':
            del retorno['quantidade']
            del retorno['desativas']

        return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ GET Options ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_interface-option_driver/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_driver(name_line):
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


@app.route("/get_interface-option_vehicle/<name_line>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_vehicle(name_line):
    plate_ignore = request.args.get('plate_ignore')
    
    if plate_ignore == 'Não definido':
        plate_ignore = None

    linha = Linha.query.filter_by(nome=name_line).first()
    if linha:
        relacao = return_relationship(linha.codigo)
        if relacao and relacao != 'membro':
            retorno = {'error': False, 'data': deque()}

            for onibus in linha.onibus:
                if plate_ignore != onibus.placa:
                    motorista = onibus.motorista
                    if motorista:
                        retorno['data'].appendleft(f"{onibus.placa} > {motorista.nome}")
                    else: retorno['data'].append(f"{onibus.placa} > Nenhum")
            
            retorno['data'] = list(retorno['data'])
            return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-option_point/<name_line>/<plate>/<shift>/<hr_par>/<hr_ret>/<type>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_options_point(name_line, plate, shift, hr_par, hr_ret, type):
    pos = request.args.get('pos')

    if name_line and plate and shift and hr_par and hr_ret and type:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relationship = return_relationship(linha.codigo)
            if relationship and relationship != 'membro':
                rota = return_route(linha.codigo, plate, shift, hr_par, hr_ret, pos)
                if rota is not None:
                    if not rota:
                        return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
                
                    not_includes = db.session.query(Ponto.id).join(Parada).filter(
                        db.and_(
                            Parada.Rota_codigo == rota.codigo,
                            Parada.Ponto_id == Ponto.id,
                            Parada.tipo == type
                        )
                    ).subquery()

                    pontos = db.session.query(Ponto.nome).filter(
                        db.and_(
                            Ponto.Linha_codigo == linha.codigo,
                            db.not_(Ponto.id.in_(not_includes.select()))
                        )
                    ).order_by(Ponto.nome).all()

                    return jsonify({'error': False, 'data': [ponto.nome for ponto in pontos]})

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ GET Config ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/get_point/<name_line>/<name_point>", methods=['GET'])
@login_required
@roles_required("motorista")
def get_point(name_line, name_point):
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
                retorno['turnos']['Matutino'] = {'alunos': [], 'contraturno': []}
                retorno['turnos']['Vespertino'] = {'alunos': [], 'contraturno': []}
                retorno['turnos']['Noturno'] = {'alunos': [], 'contraturno': []}
                
                if not dict_ponto['linkGPS']:
                    dict_ponto['linkGPS'] = 'Não definido'
                
                for relacao_parada in ponto.relacoes:
                    rota = relacao_parada.rota

                    if relacao_parada.tipo == 'partida':
                        veiculo = rota.onibus
                        placa = 'Sem veículo'
                        motorista = 'Desativada'

                        if veiculo:
                            placa = veiculo.placa
                            motorista = 'Nenhum'
                            if veiculo.motorista:
                                motorista = veiculo.motorista.nome

                        dados = {
                            'motorista': motorista,
                            'placa': placa,
                            'turno': rota.turno,
                            'horario_partida': format_time(rota.horario_partida),
                            'horario_retorno': format_time(rota.horario_retorno),
                            'quantidade': count_part_route(rota, formated=False)
                        }
                        retorno['utilizacao']['rotas'].append(dados)
                retorno['utilizacao']['quantidade'] = count_list(retorno['utilizacao']['rotas'], 'rota')

                paradas = db.session.query(Parada.codigo).filter_by(Ponto_id=ponto.id).subquery()
                values = (
                    db.session.query(Passagem, Aluno)
                    .filter(db.and_(
                        Passagem.passagem_fixa == True,
                        Passagem.Parada_codigo.in_(paradas.select()),
                        Passagem.Aluno_id == Aluno.id
                    ))
                    .order_by(Aluno.nome)
                    .all()
                )

                for value in values:
                    if value.passagem_contraturno:
                        retorno['turnos'][value.turno]['contraturno'].append(value.nome)
                    else: retorno['turnos'][value.turno]['alunos'].append(value.nome)

                return jsonify(retorno)

    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações do ponto.'})


@app.route("/get_route/<name_line>/<plate>/<shift>/<hr_par>/<hr_ret>", methods=['GET'])
@login_required
def get_route(name_line, plate, shift, hr_par, hr_ret):
    pos = request.args.get('pos')

    if name_line and shift and hr_par and hr_ret:
        linha = Linha.query.filter_by(nome=name_line).first()
        if linha:
            relationship = return_relationship(linha.codigo)
            role = current_user.roles[0].name
            retorno = {'error': False, 'role': role, 'relacao': relationship}
            retorno['data'] = {'partida': {'paradas': []}, 'retorno': {'paradas': []}}
            retorno['msg_desativada'] = False

            user = return_my_user()
            rota = return_route(linha.codigo, plate, shift, hr_par, hr_ret, pos)

            if rota is not None and user:
                if not rota:
                    return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})

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
                    'turno_rota': rota.turno,
                    'horario_partida': format_time(rota.horario_partida),
                    'horario_retorno': format_time(rota.horario_retorno)
                }

                if role == 'aluno':
                    retorno['meu_turno'] = user.turno
                    retorno['msg_cadastrar'] = False
                    retorno['msg_contraturno'] = False

                    if user.turno == rota.turno:
                        retorno['meus_pontos'] = {}

                        values = db.session.query(Passagem, Parada).filter(
                            db.and_(
                                Passagem.Parada_codigo == Parada.codigo,
                                Parada.Rota_codigo == rota.codigo,
                                Passagem.Aluno_id == current_user.primary_key,
                                Passagem.passagem_contraturno == False,
                                Passagem.passagem_fixa == True
                            )
                        ).all()

                        if values:
                            for value in values:
                                ponto = value.ponto
                                retorno['meus_pontos'][value.tipo] = ponto.nome
                        else: retorno['msg_cadastrar'] = True
                    else:
                        retorno['meu_contraturno'] = None

                        ponto_contraturno = (
                            db.session.query(Ponto.nome).join(Parada).join(Passagem)
                            .filter(
                                db.and_(
                                    Ponto.id == Parada.Ponto_id,
                                    Parada.Rota_codigo == rota.codigo,
                                    Passagem.Parada_codigo == Parada.codigo,
                                    Passagem.Aluno_id == current_user.primary_key,
                                    Passagem.passagem_contraturno == True,
                                    Passagem.passagem_fixa == True
                                )
                            )
                            .first()
                        )

                        if ponto_contraturno:
                            retorno['meu_contraturno'] = ''
                        else: retorno['msg_contraturno'] = True

                for tipo in ['partida', 'retorno']:
                    values = db.session.query(Parada, Ponto).filter(
                        db.and_(
                            Parada.Rota_codigo == rota.codigo,
                            Parada.Ponto_id == Ponto.id,
                            Parada.tipo == tipo
                        )
                    ).order_by(Parada.ordem).all()
                    
                    for value in values:
                        info = {
                            'number': value.ordem,
                            'nome': value.nome,
                            'horario': format_time(value.horario_passagem)
                        }
                        retorno['data'][tipo]['paradas'].append(info)
                    retorno['data'][tipo]['quantidade'] = count_list(values, 'definido')

                return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de Carregamento', 'text': 'Ocorreu um erro inesperado ao tentar carregar as informações da rota.'})
