from flask_security import login_user, logout_user, login_required, roles_required, current_user
from app.utilities import format_register, check_permission, capitalize, return_relationship
from app import app, limiter, cidades, turnos
from flask import request, jsonify
from app.database import *
import bcrypt


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Session ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.errorhandler(429)
def return_limitacao(e):
    route = request.endpoint
    if route == 'cadastrar_usuario':
        return jsonify({'error': True, 'title': 'Excesso de Cadastro', 'text': 'Identificamos que você realizou várias tentativas de cadastro em um curto período de tempo. Por questões de segurança, bloqueamos temporariamente o seu acesso.'})
    return jsonify({'error': True, 'title': 'Limite de Tentativas Excedido', 'text': 'Parece que você atingiu o limite de tentativas de login. Por questões de segurança, sua conta foi temporariamente bloqueada. Por favor, tente novamente mais tarde.'}), 429


@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/authenticate_user", methods=['POST'])
@limiter.limit('5 per minute')
def autenticar_usuario():
    data = request.get_json()

    if data and 'login' in data and 'password' in data:
        user = user_datastore.find_user(login=data['login'])

        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash):
            if not user.active:
                role = user.roles[0].name
                if role == 'motorista' and user.analysis:
                    return jsonify({'error': True, 'title': 'Conta em Avaliação', 'text': 'A análise da sua conta de motorista está em andamento por nossa equipe. Destacamos que esse procedimento não envolve a visualização de suas informações de login. Esse protocolo é adotado para novos usuários motoristas, visando garantir a autenticidade do usuário e fortalecer a segurança do site. Assim que a análise for concluída, enviaremos um e-mail para notificá-lo sobre a liberação do acesso.'})
                return jsonify({'error': True, 'title': 'Conta Desativada', 'text': 'Esta conta foi desativada por tempo indefinido.'})
            login_user(user)
            return jsonify({'error': False, 'redirect': '/page_user'})
        
    return jsonify({'error': True, 'title': 'Falha de Login', 'text': 'Verifique suas credenciais e tente novamente.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Inserts ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

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

            if not Linha.query.filter_by(nome=data['nome']).first():
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
            else:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Já existe uma linha com o nome especificado.'}) 

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
                            return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': f'Ao realizar o cadastro, identificamos que o(a) motorista <strong>{motorista_nome}</strong> já possui vínculo com outro veículo. O condutor deste veículo foi definido como: Nenhum.'})
                        
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

                    return jsonify({'error': False, 'title': 'Veículo Adicionado', 'text': 'O veículo foi adicionado e está disponível para utilização. O condutor deste veículo foi definido como: Nenhum.'})
                
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
            data['nome'] = data.pop('name_point').lower().capitalize()
            if not Ponto.query.filter_by(nome=data['nome'], Linha_codigo=data['Linha_codigo']).first():
                ponto = Ponto(**data)
                try:
                    db.session.add(ponto)
                    db.session.commit()

                    return jsonify({'error': False, 'title': 'Ponto Cadastrado', 'text': f'<strong>{ponto.nome}</strong> foi cadastrado com sucesso.'})
                except Exception as e:
                    db.session.rollback()
                    print(f'Erro ao criar o ponto: {str(e)}')
            else:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'Identificamos que já existe um ponto com esse nome em sua linha. A ação não pôde ser concluída.'})

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
            if data['turno'] not in turnos:
                return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'O turno definido não está presente entre as opções disponíveis.'})

            if data['Onibus_placa'] != 'Nenhum':
                
                veiculo = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], placa=data['Onibus_placa']).first()
                if veiculo:
                    rota = Rota(**data)
                    try:
                        db.session.add(rota)
                        db.session.commit()

                        return jsonify({'error': False, 'title': 'Rota Cadastrada', 'text': f'A rota foi adicionada para <strong>{veiculo.placa}</strong>.'})
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


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Edit Data ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_profile", methods=['PATCH'])
@login_required
def edit_perfil():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'password' in data:
        if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.password_hash):
            not_modify = ['id', 'curso', 'turno', 'primary_key', 'fs_uniquifier', 'active', 'analysis', 'aceitou_termo_uso_dados']
            field = data['field']
            new_value = data['new_value']

            if field and field not in not_modify and new_value:
                if field == 'login':
                    if not User.query.filter_by(login=new_value).first():
                        try:
                            current_user.login = new_value
                            db.session.commit()
                            return jsonify({'error': False, 'title': 'Edição Concluída', 'text': 'Seu login foi alterada com sucesso.'})
                        
                        except Exception as e:
                            db.session.rollback()
                            print(f'Erro ao modificar o perfil: {str(e)}')
                            
                    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'O nome de usuário definido não atende aos critérios de cadastro para ser utilizado como login. Por favor, escolha outro nome.'})

                elif field == 'senha':
                    if isinstance(new_value, str):
                        new_password_hash = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
                        try:
                            current_user.password_hash = new_password_hash
                            db.session.commit()
                            return jsonify({'error': False, 'title': 'Edição Concluída', 'text': 'Sua senha foi alterada com sucesso.'})
                        
                        except Exception as e:
                            db.session.rollback()
                            print(f'Erro ao modificar o perfil: {str(e)}')
                else:
                    my_user = return_my_user()
                    if my_user and hasattr(my_user, field) and field != 'id':
                        if field == 'nome':
                            new_value = capitalize(new_value, current_user.roles[0].name)
                            if not new_value:
                                return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'O nome definido não atende aos critérios de cadastro do aluno. Por favor, defina seu nome completo para prosseguir.'})

                        try:
                            setattr(my_user, field, new_value)
                            db.session.commit()
                            return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
                        
                        except Exception as e:
                            db.session.rollback()
                            print(f'Erro ao modificar o perfil: {str(e)}')
        else:
            return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'}) 


@app.route("/edit_line", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_linha_valor():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'name_line' in data:
        reference = 'dono' if data['field'] == 'nome' or data['field'] == 'cidade' else 'adm'
        permission = check_permission(data, reference)

        if permission == 'autorizado':
            if data['field'] == 'nome':
                check = Linha.query.filter_by(nome=data['new_value']).first()
                if check:
                    if check.codigo == data['Linha_codigo']:
                        return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Você deve definir um nome diferente do atual.'})
                    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Já existe uma linha cadastrada com este nome. Por favor, escolha um nome diferente para prosseguir.'})
                
            elif data['field'] == 'cidade':
                if not data['new_value'] in cidades:
                    return jsonify({'error': True, 'title': 'Edição Interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})
            
            linha = Linha.query.filter_by(codigo=data['Linha_codigo']).first()
            if linha and hasattr(linha, data['field']):
                if data['field'] != 'codigo':
                    try:
                        setattr(linha, data['field'], data['new_value'])
                        db.session.commit()
                        return jsonify({'error': False, 'title': 'Alteração Concluída', 'text': ''})
                    
                    except Exception as e:
                        db.session.rollback()
                        print(f'Erro ao modificar a linha: {str(e)}')
        
        elif permission == 'senha incorreta':
            return jsonify({'error': True, 'title': 'Senha Incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'}) 


@app.route("/edit_vehicle", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_vehicle():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'name_line' in data and 'plate' in data:
        field = data['field']; new_value = data['new_value']
        not_modify = ['placa', 'Linha_codigo', 'Motorista_id']

        if field and field not in not_modify and new_value and data['plate']:
            linha = Linha.query.filter_by(nome=data['name_line']).first()
            code_line = linha.codigo if linha else None

            relationship = return_relationship(code_line)
            vehicle = Onibus.query.filter_by(Linha_codigo=code_line, placa=data['plate']).first() if relationship else False

            if vehicle:
                if relationship == 'membro':
                    if field == 'motorista':
                        if vehicle.Motorista_id:
                            if vehicle.Motorista_id == current_user.primary_key and new_value == 'Nenhum':
                                try:
                                    vehicle.Motorista_id = None
                                    db.session.commit()
                                    return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você não possui mais relação com <strong>{vehicle.placa}</strong>.'}) 
                                
                                except Exception as e:
                                    db.session.rollback()
                                    print(f'Erro ao editar o veículo: {str(e)}')
                        else:
                            user = return_my_user()
                            if user and new_value == user.nome:
                                if Onibus.query.filter_by(Linha_codigo=code_line, Motorista_id=current_user.primary_key).first():
                                    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                                
                                try:
                                    vehicle.Motorista_id = current_user.primary_key
                                    db.session.commit()
                                    return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você foi definido como condutor de <strong>{vehicle.placa}</strong>.'})
                                
                                except Exception as e:
                                    db.session.rollback()
                                    print(f'Erro ao editar o veículo: {str(e)}')
                else:
                    user = return_my_user()
                    if user:
                        if field == 'motorista':
                            motorista = None
                            if new_value != 'Nenhum':
                                subquery = db.session.query(Membro.Motorista_id).filter(
                                    Membro.Linha_codigo == code_line
                                ).subquery()

                                motorista = db.session.query(Motorista).filter(
                                    db.and_(
                                        Motorista.nome == new_value,
                                        Motorista.id.in_(subquery.select())
                                    )
                                ).all()

                                if not motorista:
                                    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})

                                if len(motorista) != 1:
                                    return jsonify({'error': True, 'title': 'Cadastro Interrompido', 'text': 'A edição não pôde ser concluída devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
                                motorista = motorista[0]

                                if Onibus.query.filter_by(Motorista_id=motorista.id, Linha_codigo=code_line).first():
                                    if new_value == user.nome:
                                        return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Identificamos que o(a) motorista selecionado(a) já possui vínculo com outro veículo.'})
                                
                                new_value = motorista.id
                            else: new_value = None

                            try:
                                vehicle.Motorista_id = new_value
                                db.session.commit()
                            
                                if new_value:
                                    if motorista.id == current_user.primary_key:
                                        return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'Você foi definido(a) como condutor(a) de <strong>{vehicle.placa}</strong>.'})
                                    return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'{motorista.nome} foi definido(a) como condutor(a) de <strong>{vehicle.placa}</strong>.'}) 
                                return jsonify({'error': False, 'title': 'Edição Concluída', 'text': f'O condutor de <strong>{vehicle.placa}</strong> foi definido como: Nenhum.'}) 
                            
                            except Exception as e:
                                db.session.rollback()
                                print(f'Erro ao editar o veículo: {str(e)}')
                        else:
                            if new_value.isdigit():
                                new_value = int(new_value)
                                try:
                                    vehicle.capacidade = new_value
                                    db.session.commit()
                                    return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
                                
                                except Exception as e:
                                    db.session.rollback()
                                    print(f'Erro ao editar o veículo: {str(e)}')

    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


@app.route("/edit_point", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_point():
    data = request.get_json()
    if data and 'name_line' in data and 'name_point' in data and 'field' in data and 'new_value' in data:
        not_modify = ['id', 'Linha_codigo']
        if data['field'] not in not_modify:
            permission = check_permission(data)
            if permission == 'autorizado':
                if data['field'] == 'nome':
                    data['new_value'] = data['new_value'].lower().capitalize()
                    if Ponto.query.filter_by(Linha_codigo=data['Linha_codigo'], nome=data['new_value']).first():
                        return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Identificamos a existência de um ponto com o mesmo nome já cadastrado em sua linha. A ação não pôde ser concluída.'})

                ponto = Ponto.query.filter_by(Linha_codigo=data['Linha_codigo'], nome=data['name_point']).first()
                if ponto and hasattr(ponto, data['field']):
                    try:
                        setattr(ponto, data['field'], data['new_value'])
                        db.session.commit()
                        return jsonify({'error': False, 'title': 'Edição Concluída', 'text': ''})
                    
                    except Exception as e:
                        db.session.rollback()
                        print(f'Erro ao editar o ponto: {str(e)}')
    
    return jsonify({'error': True, 'title': 'Edição Interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})
