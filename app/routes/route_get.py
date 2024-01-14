from flask_security import login_required, current_user
from app.database import db
from flask import request, jsonify
from app.utilities import return_relationship
from app import app


@app.route("/check_line", methods=['POST'])
@login_required
def checkLine():
    key = current_user.primary_key
    response = {'conf': True}
    if key.isdigit():
        if db.select('Aluno_has_Ponto', where={'where': 'Aluno_matricula = %s', 'value': key}):
            response['conf'] = True
    else:
        if db.select('Linha_has_Motorista', where={'where': 'Motorista_nome = %s', 'value': key}):
            response['conf'] = True
    return jsonify(response)


@app.route("/get_profile", methods=['GET'])
@login_required
def get_perfil():
    data = {}
    role = current_user.roles[0].name
    user = db.return_user(current_user.primary_key)

    data['nome'] = user.nome
    data['telefone'] = user.telefone
    data['email'] = user.email

    if role == 'aluno':
        data['curso'] = user.curso
        data['turno'] = user.turno

        if not data['email']:
            data['email'] = 'Não definido'
    else:
        data['pix'] = user.pix
        
        if not data['pix']:
            data['pix'] = 'Não definido'

    return jsonify(data)


@app.route("/get_lines", methods=['GET'])
@login_required
def get_linhas():
    role = current_user.roles[0].name
    data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}

    linhas = db.select('Linha', data='codigo, nome, particular, cidade, ferias', order='nome')
    donos = db.select('Linha_has_Motorista', data='Linha_codigo, Motorista_nome', where={'where': 'motorista_dono = %s', 'value': True})

    if linhas and not isinstance(linhas, list):
        linhas = [linhas]

    if donos and not isinstance(donos, list):
        donos = [donos]

    if role == 'aluno':
        linha_aluno = False
        ponto_id = db.select('Aluno_has_Ponto', data='Ponto_id', where={'where': 'Aluno_matricula = %s', 'value': current_user.primary_key})
        if ponto_id:
            if isinstance(ponto_id, tuple):
                ponto_id = ponto_id[0]['Ponto_id']
            else: ponto_id = ponto_id['Ponto_id']

            linha_aluno_codigo = db.select('Ponto', data='Linha_codigo', where={'where': 'id = %s', 'value': ponto_id})['Linha_codigo']
            linha_aluno = db.select('Linha', data='nome', where={'where': 'codigo = %s', 'value': linha_aluno_codigo})['nome']

    if linhas:
        for linha in linhas:
            if linha['cidade'] not in data['cidades']:
                data['cidades'][linha['cidade']] = []

            data['cidades'][linha['cidade']].append(linha)
            for dono in donos:
                if dono['Linha_codigo'] == linha['codigo']:
                    linha['dono'] = dono['Motorista_nome']

                    if role == 'motorista':
                        if dono['Motorista_nome'] == current_user.primary_key:
                            data['minha_linha'].append(linha)
                    else:
                        if linha_aluno and linha['nome'] == linha_aluno:
                            data['minha_linha'].append(linha)
            del linha['codigo']
            del linha['cidade']
    else: data['identify'] = False
    return jsonify(data)


@app.route("/get_interface-line", methods=['GET'])
@login_required
def get_interfaceLinha():
    name_line = request.args.get('name_line')

    if name_line:
        retorno = {'role': current_user.roles[0].name}
        linha = db.select('Linha', where={'where': 'nome = %s', 'value': name_line})
        retorno['relacao'] = return_relationship(linha['codigo'])

        if not linha['particular']:
            del linha['valor_cartela']
            del linha['valor_diaria']
        else:
            if linha['valor_cartela']:
                linha['valor_cartela'] = f'{linha["valor_cartela"]:.2f}'.replace('.', ',')
            else: linha['valor_cartela'] = 'Não definido'
            
            if linha['valor_diaria']:
                linha['valor_diaria'] = f'{linha["valor_diaria"]:.2f}'.replace('.', ',')
            else: linha['valor_diaria'] = 'Não definido'
        del linha['codigo']
        
        retorno['data'] = linha
        return jsonify(retorno)
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-driver", methods=['GET'])
@login_required
def get_interfaceMotoristas():
    name_line = request.args.get('name_line')

    if name_line:
        motoristas = {}
        codigo_linha = db.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': name_line})
        codigo_linha = codigo_linha['codigo']
        relacao_motoristas = db.select('Linha_has_Motorista', where={'where': 'Linha_codigo = %s', 'value': codigo_linha})

        if not isinstance(relacao_motoristas, list):
            relacao_motoristas = [relacao_motoristas]

        for dados in relacao_motoristas:
            motorista = db.select('Motorista', where={'where': 'nome = %s', 'value': dados['Motorista_nome']})

            if dados['motorista_dono']:
                motoristas['dono'] = [motorista]

                if not motorista['pix']:
                    motorista['pix'] = 'Não definido'

            elif dados['motorista_adm']:
                if 'adm' not in motoristas:
                    motoristas['adm'] = []

                motoristas['adm'].append(motorista)
                del motorista['pix']

            else:
                if 'motoristas' not in motoristas:
                    motoristas['membro'] = []

                motoristas['membro'].append(motorista)
                del motorista['pix']

            del motorista['email']

        retorno = {
            'error': False,
            'role': current_user.roles[0].name,
            'data': motoristas
        }

        if retorno['role'] == 'motorista':
            retorno['relacao'] = return_relationship(codigo_linha)

        return jsonify(retorno)
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações dos motoristas.'})


@app.route("/get_interface-veicle", methods=['GET'])
@login_required
def get_interfaceVeiculo():
    name_line = request.args.get('name_line')

    if name_line:
        retorno = {
            'error': False,
            'role': current_user.roles[0].name,
            'data': None
        }

        codigo_linha = db.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': name_line})
        codigo_linha = codigo_linha['codigo']
        veiculos = db.select('Onibus', where={'where': 'Linha_codigo = %s', 'value': codigo_linha}, order='placa')

        if retorno['role'] == 'motorista':
            retorno['relacao'] = return_relationship(codigo_linha)

        if veiculos:
            if not isinstance(veiculos, list):
                veiculos = [veiculos]

            for veiculo in veiculos:
                del veiculo['Linha_codigo']
                if not veiculo['Motorista_nome']:
                    veiculo['Motorista_nome'] = 'Nenhum'
            retorno['data'] = veiculos

        return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações dos veículos.'})
