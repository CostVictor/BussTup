from flask_security import login_required, roles_required, current_user
from app import app, limiter, cidades, turnos
from flask import request, jsonify
from app.utilities import *
from app.database import *


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Inserts Site ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/register_user", methods=['POST'])
@limiter.limit('5 per minute')
def cadastrar_usuario():
    info = format_register(request.get_json())
    if info:
        inconsistencia, title, text, data = info
        if inconsistencia:
            return jsonify({'error': True, 'title': title, 'text': text})

        if create_user(data):
            return jsonify({'error': False, 'title': 'Usuário Cadastrado', 'text': ''})
    
    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar realizar o cadastro.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~ Inserts Line ~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/create_line", methods=['POST'])
@login_required
@roles_required("motorista")
def create_line():
    data = request.get_json()

    if data and 'data' in data and 'codigo' not in data:
        data = data['data']

        if 'nome' in data and 'cidade' in data:
            if not data['cidade'] in cidades:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})
            
            linha = Linha.query.filter_by(nome=data['nome']).first()
            if linha:
                if not Marcador_Exclusao.query.filter_by(tabela='Linha', key_item=linha.codigo).first():
                    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Já existe uma linha com o nome especificado.'})

            data['ferias'] = False
            linha = Linha(**data)
            try:
                db.session.add(linha)
                with db.session.begin_nested():
                    relacao = Membro(Linha_codigo=linha.codigo, Motorista_id=current_user.primary_key, dono=True, adm=True)
                    db.session.add(relacao)
                db.session.commit()
                return jsonify({'error': False, 'title': 'Linha Cadastrada', 'text': 'Sua linha foi cadastrada e está disponível para utilização. Você foi adicionado(a) como usuário dono.'})

            except Exception as e:
                db.session.rollback()
                print(f'Erro na criação da linha: {str(e)}')

    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a linha.'})


@app.route("/create_vehicle", methods=['POST'])
@login_required
@roles_required("motorista")
def create_vehicle():
    data = request.get_json()
    permission = check_permission(data)
    if permission == 'autorizado' and 'placa' in data and 'motorista_nome' in data:
        motorista_nome = data.pop('motorista_nome')
        verify_placa = Onibus.query.filter_by(placa=data['placa']).first()
        
        if motorista_nome != 'Nenhum':
            subquery = db.session.query(Membro.Motorista_id).filter(Membro.Linha_codigo == data['Linha_codigo']).subquery()
            motoria_id = db.session.query(Motorista.id).filter(
                db.and_(
                    Motorista.nome == motorista_nome,
                    Motorista.id.in_(subquery.select())
                )
            ).all()
            
            if not verify_placa:
                if motoria_id and len(motoria_id) == 1:
                    data['Motorista_id'] = motoria_id[0].id
                    check_not_dis = Onibus.query.filter_by(Motorista_id=data['Motorista_id'], Linha_codigo=data['Linha_codigo']).first()

                    report = False
                    if check_not_dis:
                        del data['Motorista_id']
                        report = True
                    
                    onibus = Onibus(**data)
                    try:
                        db.session.add(onibus)
                        db.session.commit()

                        if report:
                            if motoria_id[0].id == current_user.primary_key:
                                return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'Ao realizar o cadastro, identificamos que você já possui vínculo com outro veículo nesta linha. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
                            
                            return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'Ao realizar o cadastro, identificamos que o(a) motorista <strong>{motorista_nome}</strong> já possui vínculo com outro veículo. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
                        
                        if onibus.Motorista_id == current_user.primary_key:
                            return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'O veículo foi adicionado e está disponível para utilização. Você foi definido(a) como condutor(a).'})
                        
                        return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'O veículo foi adicionado e está disponível para utilização. <strong>{motorista_nome}</strong> foi definido(a) como condutor(a).'})
                        
                    except Exception as e:
                        db.session.rollback()
                        print(f'Erro ao criar o veículo: {str(e)}')
                else:
                    return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'O cadastro não pôde ser concluído devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
        else:
            if not verify_placa:
                onibus = Onibus(**data)

                try:
                    db.session.add(onibus)
                    db.session.commit()

                    return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': 'O veículo foi adicionado e está disponível para utilização. O condutor deste veículo foi definido como: <strong>Nenhum</strong>.'})
                
                except Exception as e:
                    db.session.rollback()
                    print(f'Erro ao criar o veículo: {str(e)}')
            else:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos a existência de um veículo cadastrado com a mesma placa em nosso banco de dados. Por favor, revise as informações e tente novamente.'})

    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o veículo.'})   


@app.route("/create_point", methods=['POST'])
@login_required
@roles_required("motorista")
def create_point():
    data = request.get_json()
    if data and 'name_point' in data and 'name_line' in data and 'id' not in data and 'nome' not in data:
        permission = check_permission(data)
        if permission == 'autorizado':
            data['nome'] = capitalize(data.pop('name_point'), 'motorista')

            ponto_check = Ponto.query.filter_by(nome=data['nome'], Linha_codigo=data['Linha_codigo']).first()
            if ponto_check:
                if not Marcador_Exclusao.query.filter_by(tabela='Ponto', key_item=ponto_check.id).first():
                    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos que já existe um ponto com esse nome em sua linha. A ação não pôde ser concluída.'})

            ponto = Ponto(**data)
            try:
                db.session.add(ponto)
                db.session.commit()

                return jsonify({'error': False, 'title': 'Ponto Cadastrado', 'text': f'<strong>{ponto.nome}</strong> foi cadastrado com sucesso.'})
            
            except Exception as e:
                db.session.rollback()
                print(f'Erro ao criar o ponto: {str(e)}')

    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o ponto.'})


@app.route("/create_route", methods=['POST'])
@login_required
@roles_required("motorista")
def create_route():
    data = request.get_json()
    if data and 'name_line' in data and 'plate' in data and 'turno' in data and 'codigo' not in data:
        permission = check_permission(data)
        if permission == 'autorizado' and 'horario_partida' in data and 'horario_retorno' in data:
            data['Onibus_placa'] = data.pop('plate')
            hr_par = data['horario_partida']
            hr_ret = data['horario_retorno']

            if data['turno'] not in turnos:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'O turno definido não está presente entre as opções disponíveis.'})

            if data['Onibus_placa'] != 'Nenhum':
                veiculo = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], placa=data['Onibus_placa']).first()
                if veiculo:
                    if check_times(veiculo.placa, time=[hr_par, hr_ret]):
                        return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': f'Identificamos a possibilidade de um conflito de horários nesta rota com outra rota já definida para <strong>{veiculo.placa}</strong>. A ação não pôde ser concluída.'})

                    rota = Rota(**data)
                    try:
                        db.session.add(rota)
                        db.session.commit()

                        return jsonify({'error': False, 'title': 'Rota Cadastrada', 'text': f'A rota foi adicionada para o veículo: <strong>{veiculo.placa}</strong>.'})
                    except Exception as e:
                        db.session.rollback()
                        print(f'Erro ao criar a rota: {str(e)}')
            else:
                del data['Onibus_placa']
                rota = Rota(**data)
                try:
                    db.session.add(rota)
                    db.session.commit()

                    return jsonify({'error': False, 'title': 'Rota Cadastrada', 'text': 'A rota foi adicionada à sua linha como desativada e não estará visível para os alunos até que um veículo seja definido. Manteremos esta rota em um local reservado para que você possa configurá-la.'})
                except Exception as e:
                    db.session.rollback()
                    print(f'Erro ao criar a rota: {str(e)}')

    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a rota.'})


@app.route("/create_stop", methods=['POST'])
@login_required
@roles_required("motorista")
def create_stop():
    data = request.get_json()
    if data and 'name_line' in data and 'name_point' in data and 'plate' in data and 'shift' in data and 'time_par' in data and 'time_ret' in data and 'pos' in data and 'type' in data:
        permission = check_permission(data)
        hr_par = data['time_par']; hr_ret = data['time_ret']
        plate = data['plate']; tipo = data['type']
        dis = ['partida', 'retorno']

        if permission == 'autorizado' and tipo in dis and hr_par and hr_ret and plate:
            rota = return_route(data['Linha_codigo'], plate, data['shift'], hr_par, hr_ret, data['pos'])

            if rota is not None:
                if not rota:
                    return jsonify({'error': True, 'title': 'Falha de Identificação', 'text': 'Tivemos um problema ao tentar identificar a rota. Por favor, recarregue a página e tente novamente.'})
                
                ponto = Ponto.query.filter_by(nome=data['name_point'], Linha_codigo=data['Linha_codigo']).first()
                if ponto:
                    if Parada.query.filter_by(tipo=tipo, Rota_codigo=rota.codigo, Ponto_id=ponto.id).first():
                        return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': f'Identificamos que este ponto já está presente no trajeto de <strong>{tipo.capitalize()}</strong>. A ação não pôde ser concluída.'})

                    if 'time_pas' in data:
                        contagem_partida = 0
                        contagem_retorno = 0
                        for parada in rota.paradas:
                            if parada.tipo == 'partida':
                                contagem_partida += 1
                            else: contagem_retorno += 1

                        data_parada = {
                            'Rota_codigo': rota.codigo,
                            'Ponto_id': ponto.id,
                            'horario_passagem': data['time_pas'],
                            'ordem': (contagem_partida + 1) if tipo == 'partida' else (contagem_retorno + 1),
                            'tipo': tipo
                        }
                        parada = Parada(**data_parada)
                        text = f'<strong>{ponto.nome}</strong> foi adicionado ao trajeto de <strong>{tipo.capitalize()}</strong> como último ponto da ordem. Por favor, verifique se esta configuração está correta.'

                        parada_2 = False
                        if 'time_pas_2' in data:
                            data_parada['horario_passagem'] = data['time_pas_2']
                            data_parada['tipo'] = [tipo for tipo in dis if tipo != data_parada['tipo']][0]
                            data_parada['ordem'] = (contagem_partida + 1) if data_parada['tipo'] == 'partida' else (contagem_retorno + 1)

                            if not Parada.query.filter_by(tipo=data_parada['tipo'], Rota_codigo=rota.codigo, Ponto_id=ponto.id).first():
                                parada_2 = Parada(**data_parada)
                                text = f'<strong>{ponto.nome}</strong> foi adicionado aos dois trajetos como os últimos pontos na ordem. Por favor, verifique se essas configurações estão corretas.'
                            else:
                                text = f'<strong>{ponto.nome}</strong> foi adicionado apenas no trajeto <strong>{parada.tipo.capitalize()}</strong> devido a ele já estar presente no trajeto <strong>{data_parada["tipo"]}</strong>. Por favor, verifique se a configuração da ordem está correta.'

                        try:
                            db.session.add(parada)
                            if parada_2:
                                db.session.add(parada_2)
                            db.session.commit()
                            return jsonify({'error': False, 'title': 'Ponto Adicionado', 'text': text})
                        
                        except Exception as e:
                            db.session.rollback()
                            print(f'Erro ao criar parada: {str(e)}')

    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a parada.'})
