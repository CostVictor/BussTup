from flask_security import login_user, logout_user, login_required, roles_required, current_user
from app.utilities import format_register, check_permission, capitalize, return_relationship
from app import app, limiter, cidades, turnos
from flask import request, jsonify
from app.database import *
import bcrypt


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Session ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/logout")
@login_required
def logout():
    logout_user()


@app.route("/authenticate_user", methods=['POST'])
@limiter.limit('5 per minute')
def autenticar_usuario():
    data = request.get_json()

    if data and 'login' in data and 'password' in data:
        user = user_datastore.find_user(primary_key=data['login'])

        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.hash_senha):
            login_user(user)

            return jsonify({'error': False, 'redirect': '/page_user'})
        
    return jsonify({'error': True, 'title': 'Falha de login', 'text': 'Verifique suas credenciais e tente novamente.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Message ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/create_message", methods=['POST'])
@roles_required('motorista')
def enviar_email():...


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~ Inserts ~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/register_user", methods=['POST'])
@limiter.limit('5 per minute')
def cadastro_usuario():
    info = format_register(request.get_json())
    if info:
        inconsistencia, title, text, data = info
        if inconsistencia:
            return jsonify({'error': True, 'title': title, 'text': text})
    
        create_user(data)
        if return_user(data['login']):
            return jsonify({'error': False, 'title': 'Usuário cadastrado', 'text': ''})
    
    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao tentar realizar o cadastro.'})
    

@app.route("/create_line", methods=['POST'])
@login_required
@roles_required("motorista")
def create_line():
    data = request.get_json()

    if data and 'data' in data and 'codigo' not in data:
        data = data['data']

        if 'nome' in data and 'cidade' in data:
            if not data['cidade'] in cidades:
                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})

            if not Linha.query.filter_by(nome=data['nome']).first():
                data['ferias'] = False
                linha = Linha(**data)
                db.session.add(linha)
                db.session.commit()

                relacao = Linha_has_Motorista(Linha_codigo=linha.codigo, Motorista_login=current_user.primary_key, motorista_dono=True, motorista_adm=True)
                db.session.add(relacao)
                db.session.commit()

                query = db.session.query(Linha_has_Motorista).filter(
                    db.and_(
                        Linha_has_Motorista.Motorista_login == current_user.primary_key,
                        Linha_has_Motorista.Linha_codigo == linha.codigo
                    )
                ).first()

                if query:
                    return jsonify({'error': False, 'title': 'Linha cadastrada', 'text': 'Sua linha foi cadastrada e está disponível para utilização. Você foi adicionado como usuário dono.'})
            else:
                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Já existe uma linha com o nome especificado.'}) 

    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a linha.'})


@app.route("/create_veicle", methods=['POST'])
@login_required
@roles_required("motorista")
def create_veicle():
    data = request.get_json()
    permission = check_permission(data)
    if permission == 'autorizado' and 'placa' in data and 'motorista_nome' in data:
        data['Linha_codigo'] = data.pop('code_line')
        motorista_nome = data.pop('motorista_nome')
        verify_placa = Onibus.query.filter_by(placa=data['placa']).first()
        
        if motorista_nome != 'Nenhum':
            subquery = db.session.query(Linha_has_Motorista.Motorista_login).filter(Linha_has_Motorista.Linha_codigo == data['Linha_codigo']).subquery()
            motoria_login = db.session.query(Motorista.login).filter(
                db.and_(
                    Motorista.nome == motorista_nome,
                    Motorista.login.in_(subquery.select())
                )
            ).all()
            
            if not verify_placa:
                if motoria_login and len(motoria_login) == 1:
                    data['Motorista_login'] = motoria_login[0].login
                    verify_not_dis = Onibus.query.filter_by(Motorista_login=data['Motorista_login'], Linha_codigo=data['Linha_codigo']).first()

                    report = False
                    if verify_not_dis:
                        del data['Motorista_login']
                        report = True
                    
                    onibus = Onibus(**data)
                    db.session.add(onibus)
                    db.session.commit()

                    if Onibus.query.filter_by(placa=onibus.placa).first():
                        if report:
                            return jsonify({'error': False, 'title': 'Veículo adicionado', 'text': f'Ao realizar o cadastro, identificamos que o(a) motorista {motorista_nome} já possui vínculo com outro veículo. O condutor deste veículo foi definido como: Nenhum.'})
                        
                        return jsonify({'error': False, 'title': 'Veículo adicionado', 'text': f'O veículo foi adicionado e está disponível para utilização. {motorista_nome} foi definido(a) como condutor(a).'})

                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'O cadastro não pôde ser concluído devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
        else:
            if not verify_placa:
                onibus = Onibus(**data)
                db.session.add(onibus)
                db.session.commit()

                if Onibus.query.filter_by(placa=onibus.placa).first():
                    return jsonify({'error': False, 'title': 'Veículo adicionado', 'text': 'O veículo foi adicionado e está disponível para utilização. O condutor deste veículo foi definido como: Nenhum.'})
                
                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao realizar o cadastro do veículo.'}) 

        return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Identificamos a existência de um veículo cadastrado com a mesma placa em nosso banco de dados. Por favor, revise as informações e tente novamente.'})

    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o veículo.'})    


@app.route("/create_point", methods=['POST'])
@login_required
@roles_required("motorista")
def create_point():
    data = request.get_json()
    if data and 'name_point' in data and 'name_line' in data and 'id' not in data and 'nome' not in data:
        permission = check_permission(data)
        if permission == 'autorizado':
            data['Linha_codigo'] = data.pop('code_line')
            data['nome'] = data.pop('name_point').lower().capitalize()

            if not Ponto.query.filter_by(nome=data['nome'], Linha_codigo=data['Linha_codigo']).first():
                ponto = Ponto(**data)
                db.session.add(ponto)
                db.session.commit()

                if Ponto.query.filter_by(nome=ponto.nome, Linha_codigo=ponto.Linha_codigo).first():
                    return jsonify({'error': False, 'title': 'Ponto cadastrado', 'text': f'{ponto.nome} foi cadastrado com sucesso.'})
            else:
                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Identificamos que já existe um ponto com esse nome em sua linha. A ação não pôde ser concluída.'})

    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar o ponto.'})


@app.route("/create_route", methods=['POST'])
@login_required
@roles_required("motorista")
def create_route():
    data = request.get_json()
    if data and 'name_line' in data and 'plate' in data and 'turno' in data and 'codigo' not in data:
        permission = check_permission(data)
        if permission == 'autorizado' and 'horario_partida' in data and 'horario_retorno' in data:
            data['Linha_codigo'] = data.pop('code_line')
            data['Onibus_placa'] = data.pop('plate')

            if data['turno'] not in turnos:
                return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'O turno definido não está presente entre as opções disponíveis.'})

            if data['Onibus_placa'] != 'Nenhum':
                veiculo = Onibus.query.filter_by(Linha_codigo=data['Linha_codigo'], placa=data['Onibus_placa']).first()
                if veiculo:
                    rota = Rota(**data)
                    db.session.add(rota)
                    db.session.commit()

                    if Rota.query.filter_by(codigo=rota.codigo).first():
                        return jsonify({'error': False, 'title': 'Rota cadastrada', 'text': f'A rota foi adicionada para {veiculo.placa}.'})
            else:
                del data['Onibus_placa']
                rota = Rota(**data)
                db.session.add(rota)
                db.session.commit()

                if Rota.query.filter_by(codigo=rota.codigo).first():
                    return jsonify({'error': False, 'title': 'Rota cadastrada', 'text': f'A rota foi adicionada à sua linha como desativada e não está disponível para utilização. Configure o veículo da rota para que ela possa entrar em uso.'})

    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'Ocorreu um erro inesperado ao tentar cadastrar a rota.'})


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~ Edit Data ~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/edit_profile", methods=['PATCH'])
@login_required
def edit_perfil():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'password' in data:
        if bcrypt.checkpw(data['password'].encode('utf-8'), current_user.hash_senha):
            field = data['field']
            new_value = data['new_value']
            not_modify = ['login', 'curso', 'turno']

            if field and field not in not_modify and new_value:
                if field == 'senha':
                    new_hash_password = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt())
                    current_user.hash_senha = new_hash_password
                    db.session.commit()

                    if current_user.hash_senha == new_hash_password:
                        return jsonify({'error': False, 'title': 'Edição concluida', 'text': 'Sua senha foi alterada com sucesso.'})
                else:
                    user = return_user(current_user.primary_key)
                    if user and hasattr(user, field) and field != 'login':
                        if field == 'nome':
                            new_value = capitalize(new_value, current_user.roles[0].name)
                            if not new_value:
                                return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'O nome definido não atende aos critérios de cadastro do aluno. Por favor, defina seu nome completo para prosseguir.'})

                        setattr(user, field, new_value)
                        db.session.commit()

                        if getattr(user, field) == new_value:
                            return jsonify({'error': False, 'title': 'Edição concluida', 'text': ''})
        else:
            return jsonify({'error': True, 'title': 'Senha incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'}) 


@app.route("/edit_line", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_linha_valor():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'name_line' in data:
        reference = 'motorista_dono' if data['field'] == 'nome' or data['field'] == 'cidade' else 'motorista_adm'
        permission = check_permission(data, reference)

        if permission == 'autorizado':
            if data['field'] == 'nome':
                check = Linha.query.filter_by(nome=data['new_value']).first()
                if check:
                    if check.codigo == data['code_line']:
                        return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Você deve definir um nome diferente do atual.'})
                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Já existe uma linha cadastrada com este nome. Por favor, escolha um nome diferente para prosseguir.'})
                
            elif data['field'] == 'cidade':
                if not data['new_value'] in cidades:
                    return jsonify({'error': True, 'title': 'Edição interrompido', 'text': 'A cidade definida não está presente entre as opções disponíveis.'})
            
            linha = Linha.query.filter_by(codigo=data['code_line']).first()
            if linha and hasattr(linha, data['field']):
                if data['field'] != 'codigo':
                    setattr(linha, data['field'], data['new_value'])
                    db.session.commit()

                    return jsonify({'error': False, 'title': 'Alteração concluida', 'text': ''})
        
        elif permission == 'senha incorreta':
            return jsonify({'error': True, 'title': 'Senha incorreta', 'text': 'A senha especificada está incorreta. A edição não pôde ser concluída.'})

    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'}) 


@app.route("/edit_veicle", methods=['PATCH'])
@login_required
@roles_required("motorista")
def edit_veicle():
    data = request.get_json()
    if data and 'field' in data and 'new_value' in data and 'name_line' in data and 'plate' in data:
        field = data['field']; new_value = data['new_value']
        not_modify = ['placa', 'Linha_codigo', 'Motorista_login']

        if field and field not in not_modify and new_value and data['plate']:
            linha = Linha.query.filter_by(nome=data['name_line']).first()
            code_line = linha.codigo if linha else None

            relationship = return_relationship(code_line)
            veicle = Onibus.query.filter_by(Linha_codigo=code_line, placa=data['plate']).first() if relationship else False

            if veicle:
                if relationship == 'membro':
                    if field == 'motorista':
                        if veicle.Motorista_login:
                            if veicle.Motorista_login == current_user.primary_key and new_value == 'Nenhum':
                                veicle.Motorista_login = None
                                db.session.commit()

                                if not veicle.Motorista_login:
                                    return jsonify({'error': False, 'title': 'Edição concluida', 'text': f'Você não possui mais relação com {veicle.placa}.'}) 
                        else:
                            user = return_user(current_user.primary_key)
                            if user and new_value == user.nome:
                                if Onibus.query.filter_by(Linha_codigo=code_line, Motorista_login=current_user.primary_key).first():
                                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                                
                                veicle.Motorista_login = current_user.primary_key
                                db.session.commit()

                                if veicle.Motorista_login == current_user.primary_key:
                                    return jsonify({'error': False, 'title': 'Edição concluida', 'text': f'Você foi definido como condutor de {veicle.placa}.'})   
                else:
                    user = return_user(current_user.primary_key)
                    if user:
                        if field == 'motorista':
                            motorista = None
                            if new_value != 'Nenhum':
                                subquery = db.session.query(Linha_has_Motorista.Motorista_login).filter(
                                    Linha_has_Motorista.Linha_codigo == code_line
                                ).subquery()

                                motorista = db.session.query(Motorista).filter(
                                    db.and_(
                                        Motorista.nome == new_value,
                                        Motorista.login.in_(subquery.select())
                                    )
                                ).all()

                                if not motorista:
                                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})

                                if len(motorista) != 1:
                                    return jsonify({'error': True, 'title': 'Cadastro interrompido', 'text': 'A edição não pôde ser concluída devido à existência de mais de um usuário motorista com o mesmo nome na linha.'})
                                motorista = motorista[0]

                                if Onibus.query.filter_by(Motorista_login=motorista.login, Linha_codigo=code_line).first():
                                    if new_value == user.name:
                                        return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Você não pode possuir mais de uma relação com um veículo em uma mesma linha.'})
                                    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': f'Identificamos que o(a) motorista selecionado(a) já possui vínculo com outro veículo.'})
                                
                                new_value = motorista.login
                            else: new_value = None

                            veicle.Motorista_login = new_value
                            db.session.commit()
                            
                            if veicle.Motorista_login == new_value:
                                if new_value:
                                    if motorista.login == current_user.primary_key:
                                        return jsonify({'error': False, 'title': 'Edição concluida', 'text': f'Você foi definido(a) como condutor(a) de {veicle.placa}.'})
                                    return jsonify({'error': False, 'title': 'Edição concluida', 'text': f'{motorista.nome} foi definido(a) como condutor(a) de {veicle.placa}.'}) 
                                return jsonify({'error': False, 'title': 'Edição concluida', 'text': f'O condutor de {veicle.placa} foi definido como: Nenhum.'}) 
                        else:
                            if new_value.isdigit():
                                new_value = int(new_value)
                                veicle.capacidade = new_value
                                db.session.commit()

                                if veicle.capacidade == new_value:
                                    return jsonify({'error': False, 'title': 'Edição concluída', 'text': ''})

    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})


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
                    if Ponto.query.filter_by(Linha_codigo=data['code_line'], nome=data['new_value']).first():
                        return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Identificamos a existência de um ponto com o mesmo nome já cadastrado em sua linha. A ação não pôde ser concluída.'})

                ponto = Ponto.query.filter_by(Linha_codigo=data['code_line'], nome=data['name_point']).first()
                if ponto and hasattr(ponto, data['field']):
                    setattr(ponto, data['field'], data['new_value'])
                    db.session.commit()

                    if getattr(ponto, data['field']) == data['new_value']:
                        return jsonify({'error': False, 'title': 'Edição concluida', 'text': ''}) 
    
    return jsonify({'error': True, 'title': 'Edição interrompida', 'text': 'Ocorreu um erro inesperado ao tentar modificar a informação.'})
