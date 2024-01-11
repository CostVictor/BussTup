from flask_security import login_required, current_user
from app.models import database
from flask import request, jsonify
from app.format import return_relacao
from app import app


@app.route("/checar_linha", methods=['GET'])
@login_required
def checkLine():
    key = current_user.primary_key
    response = {'conf': True}
    if key.isdigit():
        if database.select('Aluno_has_Ponto', where={'where': 'Aluno_matricula = %s', 'value': key}):
            response['conf'] = True
    else:
        if database.select('Linha_has_Motorista', where={'where': 'Motorista_nome = %s', 'value': key}):
            response['conf'] = True
    return jsonify(response)


@app.route("/get_perfil", methods=['GET'])
@login_required
def get_perfil():
    data = {}
    role = current_user.roles[0].name
    user = database.return_user(current_user.primary_key)

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


@app.route("/get_linhas", methods=['GET'])
@login_required
def get_linhas():
    role = current_user.roles[0].name
    data = {'role': role, 'identify': True, 'cidades': {}, 'minha_linha': []}

    linhas = database.select('Linha', data='codigo, nome, particular, cidade, ferias', order='nome')
    donos = database.select('Linha_has_Motorista', data='Linha_codigo, Motorista_nome', where={'where': 'motorista_dono = %s', 'value': True})

    if linhas and not isinstance(linhas, list):
        linhas = [linhas]

    if donos and not isinstance(donos, list):
        donos = [donos]

    if role == 'aluno':
        linha_aluno = False
        ponto_id = database.select('Aluno_has_Ponto', data='Ponto_id', where={'where': 'Aluno_matricula = %s', 'value': current_user.primary_key})
        if ponto_id:
            if isinstance(ponto_id, tuple):
                ponto_id = ponto_id[0]['Ponto_id']
            else: ponto_id = ponto_id['Ponto_id']

            linha_aluno_codigo = database.select('Ponto', data='Linha_codigo', where={'where': 'id = %s', 'value': ponto_id})['Linha_codigo']
            linha_aluno = database.select('Linha', data='nome', where={'where': 'codigo = %s', 'value': linha_aluno_codigo})['nome']

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


@app.route("/get_interface-linha", methods=['POST'])
@login_required
def get_interfaceLinha():
    data = request.get_json()

    if data:
        retorno = {'role': current_user.roles[0].name}
        linha = database.select('Linha', where={'where': 'nome = %s', 'value': data['nome_linha']})

        if retorno['role'] == 'motorista':
            retorno['relacao'] = return_relacao(linha['codigo'])

        if not linha['particular']:
            del linha['valor_cartela']
            del linha['valor_diaria']
        else:
            linha['valor_cartela'] = f'{linha["valor_cartela"]:.2f}'.replace('.', ',')
            linha['valor_diaria'] = f'{linha["valor_diaria"]:.2f}'.replace('.', ',')
        del linha['codigo']
        
        retorno['data'] = linha
        return jsonify(retorno)
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações da linha.'})


@app.route("/get_interface-motorista", methods=['POST'])
@login_required
def get_interfaceMotoristas():
    data = request.get_json()

    if data:
        motoristas = {}
        codigo_linha = database.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['nome_linha']})
        codigo_linha = codigo_linha['codigo']
        relacao_motoristas = database.select('Linha_has_Motorista', where={'where': 'Linha_codigo = %s', 'value': codigo_linha})

        if not isinstance(relacao_motoristas, list):
            relacao_motoristas = [relacao_motoristas]

        for dados in relacao_motoristas:
            motorista = database.select('Motorista', where={'where': 'nome = %s', 'value': dados['Motorista_nome']})

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
            retorno['relacao'] = return_relacao(codigo_linha)

        return jsonify(retorno)
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações dos motoristas.'})


@app.route("/get_interface-veiculo", methods=['POST'])
@login_required
def get_interfaceVeiculo():
    data = request.get_json()

    if data:
        retorno = {
            'error': False,
            'role': current_user.roles[0].name,
            'data': None
        }

        codigo_linha = database.select('Linha', data='codigo', where={'where': 'nome = %s', 'value': data['nome_linha']})
        codigo_linha = codigo_linha['codigo']
        veiculos = database.select('Onibus', where={'where': 'Linha_codigo = %s', 'value': codigo_linha}, order='placa')

        if veiculos:
            if retorno['role'] == 'motorista':
                retorno['relacao'] = return_relacao(codigo_linha)

            if not isinstance(veiculos, list):
                veiculos = [veiculos]

            for veiculo in veiculos:
                del veiculo['Linha_codigo']
                if not veiculo['Motorista_nome']:
                    veiculo['Motorista_nome'] = 'Nenhum'
            retorno['data'] = veiculos

        return jsonify(retorno)
    
    return jsonify({'error': True, 'title': 'Erro de carregamento', 'text': 'Ocorreu um erro inesperado ao carregar as informações dos veículos.'})
