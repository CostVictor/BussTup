// ~~ Edição ~~ //

function edit_nome_linha() {
    const new_name = document.getElementById('edit_nome_linha_new').value
    const password = document.getElementById('edit_nome_linha_conf').value
    const name_line = document.getElementById('interface_nome').textContent

    fetch("/edit_line", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': 'nome', 'password': password, 'new_value': new_name, 'name_line': name_line})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('edit_nome_linha')
            loadInterfaceLine(new_name, false)
            create_popup(response['title'], response['text'], 'Ok', 'success')
            document.getElementById('config_linha_nome').textContent = new_name

        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function edit_cidade_linha() {
    const new_cidade = document.getElementById('edit_cidade_linha_new').value
    const password = document.getElementById('edit_cidade_linha_conf').value
    const name_line = document.getElementById('interface_nome').textContent

    fetch("/edit_line", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': 'cidade', 'password': password, 'new_value': new_cidade, 'name_line': name_line})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('edit_cidade_linha')
            loadInterfaceLine(name_line, false)
            create_popup(response['title'], response['text'], 'Ok', 'success')
            document.getElementById('config_linha_cidade').textContent = new_cidade

        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function edit_config_bool(obj_click) {
    if (!obj_click.querySelector('i').className.includes('selected')) {
        const name_line = document.getElementById('interface_nome').textContent
        const opcao = obj_click.querySelector('p').textContent

        let field = 'paga'
        let new_value = false
    
        if (obj_click.parentNode.id.includes('ferias')) {field = 'ferias'}
        if (opcao === 'Sim') {
            new_value = true
            config_bool(obj_click.parentNode, 'Sim')
        } else {config_bool(obj_click.parentNode, 'Não')}
        
        fetch("/edit_line", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': field, 'new_value': new_value, 'name_line': name_line})
        })
        .then(response => response.json())
        .then(response => {
            if (!response['error']) {
                loadInterfaceLine(name_line, false)
            } else {create_popup(response['title'], response['text'], 'Voltar')}
        })
    }
}


function edit_valor_linha(event) {
    event.preventDefault()

    const msg = document.getElementById('edit_valor_msg').textContent
    const input_new_value = document.getElementById('edit_valor_new')
    const name_line = document.getElementById('interface_nome').textContent

    if (input_new_value.value === '') {
        input_new_value.setCustomValidity('Preencha este campo.')
        input_new_value.reportValidity()

    } else if (input_new_value.value <= 0) {
        input_new_value.setCustomValidity('O valor deve ser maior que 0.')
        input_new_value.reportValidity()

    } else {
        let field = 'valor_cartela'
    
        if (msg.includes('diária')) {
            field = 'valor_diaria'
        }
    
        fetch("/edit_line", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': field, 'new_value': input_new_value.value, 'name_line': name_line})
        })
        .then(response => response.json())
        .then(response => {
            if (!response['error']) {
                cancel_popup_edit('edit_valor')
                create_popup(response['title'], response['text'], 'Ok', 'success')
                loadInterfaceLine(name_line, false)
            } else {create_popup(response['title'], response['text'], 'Voltar')}
        })
    }
}


function edit_capacidade_veiculo(event) {
    event.preventDefault()

    const name_line = document.getElementById('interface_nome').textContent
    const veicle_plate = document.getElementById('edit_veicle_capacidade').querySelector('span').textContent
    const new_value = document.getElementById('edit_veicle_capacidade_new').value.trim()

    fetch("/edit_veicle", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': 'capacidade', 'new_value': new_value, 'name_line': name_line, 'plate': veicle_plate})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('edit_veicle_capacidade')
            create_popup(response['title'], response['text'], 'Ok', 'success')
            loadInterfaceVeicle(name_line)
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function edit_motorista_veiculo() {
    const name_line = document.getElementById('interface_nome').textContent
    const veicle_plate = document.getElementById('edit_veicle_motorista').querySelector('span').textContent
    const options = document.getElementById('edit_veicle_motorista_container')
    const option_selected = options.querySelector('[class*="selected"]')

    if (!option_selected) {
        create_popup('Nenhuma opção selecionada', 'Por favor, selecione uma opção disponível.', 'Voltar')
    } else {
        const new_value = option_selected.querySelector('p').textContent
        fetch("/edit_veicle", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': 'motorista', 'new_value': new_value, 'name_line': name_line, 'plate': veicle_plate})
        })
        .then(response => response.json())
        .then(response => {
            if (!response['error']) {
                cancel_popup_edit('edit_veicle_motorista')
                create_popup(response['title'], response['text'], 'Ok', 'success')
                loadInterfaceVeicle(name_line)
            } else {create_popup(response['title'], response['text'], 'Voltar')}
        })
    }
}


function edit_point(form_submit, event) {
    event.preventDefault()

    let field = form_submit.id.split('_')
    field = field[field.length - 1]
    if (field === 'tolerancia') {field = 'tempo_tolerancia'}

    const new_value = form_submit.querySelector('input').value.trim()
    const name_line = document.getElementById('interface_nome').textContent
    const name_point = document.getElementById('edit_ponto_' + field).querySelector('span').textContent

    fetch("/edit_point", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': field, 'new_value': new_value, 'name_line': name_line, 'name_point': name_point})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('edit_ponto_' + field)
            create_popup(response['title'], response['text'], 'Ok', 'success')
            loadInterfacePoints(name_line)
            document.getElementById('config_ponto_' + field).textContent = new_value
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


// ~~ Criação ~~ //

function create_veicle() {
    const name_line = document.getElementById('interface_nome').textContent
    const placa = document.getElementById('add_veicle_placa').value
    const capacidade = document.getElementById('add_veicle_capacidade').value
    const options = document.getElementById('add_veicle_options')
    let motorista_nome = 'Nenhum'

    icon_selected = options.querySelector('i.selected')
    text_selected = icon_selected.parentNode.querySelector('p').textContent

    if (text_selected === 'Sim') {
        const container = document.getElementById('add_veicle_options_container')
        const motorista_selected = container.querySelector('div.selected')

        if (motorista_selected) {
            motorista_nome = motorista_selected.querySelector('p').textContent
        }
    }

    fetch("/create_veicle", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'placa': placa, 'capacidade': capacidade, 'motorista_nome': motorista_nome, 'name_line': name_line})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('add_veicle')
            create_popup(response['title'], response['text'], 'Ok', 'success')
            loadInterfaceVeicle(name_line)
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function create_point(event) {
    event.preventDefault()

    const name_line = document.getElementById('interface_nome').textContent
    const name_point = document.getElementById('add_point_nome').value.trim()
    const tolerance_point = document.getElementById('add_point_tolerancia').value.trim()
    const gps_point = document.getElementById('add_point_gps').value.trim()

    let data = {
        'name_point': name_point,
        'tempo_tolerancia': tolerance_point,
        'linkGPS': gps_point,
        'name_line': name_line
    }
    if (!gps_point) {
        delete data.linkGPS
    }
    if (!tolerance_point) {
        delete data.tempo_tolerancia
    }

    fetch("/create_point", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('add_point')
            create_popup(response['title'], response['text'], 'Ok', 'success')
            loadInterfacePoints(name_line)
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}

function create_route(event) {
    event.preventDefault()

    const name_line = document.getElementById('interface_nome').textContent
    const turno = document.getElementById('add_route_turno').value.trim()
    const hr_partida = document.getElementById('add_route_horario_partida').value.trim()
    const ht_retorno = document.getElementById('add_route_horario_retorno').value.trim()

    const options = document.getElementById('add_route_options')
    let option_selected = options.querySelector('[class*="selected"]')
    option_selected = option_selected.parentNode.querySelector('p').textContent

    let veicle = 'Nenhum'
    if (option_selected == 'Sim') {
        const plate_selected = document.getElementById('add_route_options_container').querySelector('[class*="selected"]')

        if (plate_selected) {
            veicle = plate_selected.textContent.trim().split(' ')[0]
        }
    }

    const data = {
        'turno': turno, 
        'horario_partida': hr_partida,
        'horario_retorno': ht_retorno,
        'plate': veicle,
        'name_line': name_line
    }
    
    fetch("/create_route", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('add_route')
            create_popup(response['title'], response['text'], 'Ok', 'success')
            loadInterfaceRoutes(name_line)
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


// ~~ Carregamento ~~ //

function loadInterfaceLine(name_line, load_complete = true) {
    fetch(`/get_interface-line?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            let adm = false
            const aviso_entrada = document.getElementById('interface_linha_entrar')
            aviso_entrada.classList.add('inactive')

            if (response['role'] === 'motorista') {
                const config_linha = document.getElementById('interface_config')
                config_linha.classList.add('inactive')

                if (response['relacao']) {
                    if (response['relacao'] === 'dono') {
                        config_linha.classList.remove('inactive')
                        adm = true
                    } else if (response['relacao'] === 'adm') {adm = true}
                } else {aviso_entrada.classList.remove('inactive')}
            } else {
                const sem_relacao = document.getElementById('interface_sem_participacao')
                const cadastrar = document.getElementById('interface_cadastrar')
                const bloqueio = document.getElementById('interface_bloqueio')

                sem_relacao.classList.remove('inactive')
                cadastrar.classList.remove('inactive')
                bloqueio.classList.add('inactive')

                if (response['relacao']) {
                    if (response['relacao'] === 'não participante') {
                        sem_relacao.classList.add('inactive')
                        cadastrar.classList.add('inactive')
                        bloqueio.classList.remove('inactive')
                    }
                } else {aviso_entrada.classList.remove('inactive')}
            }

            for (dado in response['data']) {
                if (dado === 'paga') {
                    const area_precos = document.getElementById('area_precos')
                    if (!response['data'][dado]) {
                        area_precos.classList.add('inactive')
                    } else {area_precos.classList.remove('inactive')}

                } else if (dado === 'ferias') {
                    const info_ferias = document.getElementById('interface_ferias')
                    if (!response['data'][dado]) {
                        info_ferias.classList.add('inactive')
                    } else {info_ferias.classList.remove('inactive')}

                } else {
                    const info = document.getElementById(`interface_${dado}`)
                    const edit = document.getElementById(info.id.replace('interface', 'edit'))
                    info.textContent = response['data'][dado]

                    if (edit) {
                        if (adm) {
                            edit.classList.remove('inactive')
                        } else {edit.classList.add('inactive')}
                    }
                }
            }

            if (load_complete) {
                loadInterfaceDriver(name_line)
                if (response['role'] === 'motorista') {
                    loadInterfaceVeicle(name_line)
                    loadInterfacePoints(name_line)
                }
                loadInterfaceRoutes(name_line)
            }
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function loadInterfaceDriver(name_line) {
    fetch(`/get_interface-driver?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const data = response['data']
            const local_motorista = document.getElementById('area_motoristas')
            const elements_remove = Array.from(local_motorista.children)
            elements_remove.forEach(element => {
                if (element.id.includes('motorista')) {
                    local_motorista.removeChild(element)
                }
            })

            const model_motorista = document.getElementById('model_motorista')
            for (tipo in data) {
                for (pos in data[tipo]) {
                    const motorista = model_motorista.cloneNode(true)
                    motorista.id = `motorista_${tipo}-${pos}`
                    
                    const ids = motorista.querySelectorAll('[id*="model_motorista"]')
                    ids.forEach(element => {
                        element.id = element.id.replace('model_motorista', motorista.id)
                    })
                    for (info in data[tipo][pos]) {
                        const tag = motorista.querySelector(`[id*="${info}"]`)
                        tag.textContent = data[tipo][pos][info]
                    }

                    const dono = motorista.querySelector('[id*="dono"]')
                    const adm = motorista.querySelector('[id*="adm"]')
                    if (response['role'] === 'motorista') {
                        if (response['relacao'] === 'dono' && tipo !== 'dono') {
                            const btn_config = motorista.querySelector('[id*="btn"]')
                            btn_config.classList.remove('inactive')
                        }
                    }
                    if (tipo === 'dono') {
                        dono.classList.remove('inactive')
                        adm.classList.remove('inactive')
                    } else if (tipo === 'adm') {
                        adm.classList.remove('inactive')
                    }

                    motorista.classList.remove('inactive')
                    local_motorista.appendChild(motorista)
                }
            }
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function loadInterfaceVeicle(name_line) {
    fetch(`/get_interface-veicle?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const area_onibus = document.getElementById('area_onibus')
            const container_veicles = document.getElementById('area_onibus_content')
            const division = area_onibus.querySelector('h1.page__division')
            const btn_add = document.getElementById('area_onibus_btn_add')
            
            const data = response['data']
            container_veicles.innerHTML = ''
            division.classList.add('inactive')
            btn_add.classList.add('inactive')
            
            if (response['relacao'] === 'dono' || response['relacao'] === 'adm') {
                btn_add.classList.remove('inactive')
                if (data.length) {division.classList.remove('inactive')}
            }

            const model_veicle = document.getElementById('model_onibus')    
            for (veicle in data) {
                const element = model_veicle.cloneNode(true)
                element.id = `veiculo_${veicle}`

                const ids = element.querySelectorAll('[id*="model_onibus"]')
                ids.forEach(item => {
                    item.id = item.id.replace('model_onibus', element.id)
                    if (item.id.includes('delete') && (response['relacao'] === 'dono' || response['relacao'] == 'adm')) {
                        item.classList.remove('inactive')
                    }
                })

                for (dado in data[veicle]) {
                    const value = data[veicle][dado]

                    if (dado === 'motorista_nome') {
                        const motorista_nome = element.querySelector('[id*="motorista"]')
                        motorista_nome.textContent = value
                        if (response['relacao']) {
                            if (response['relacao'] === 'membro') {
                                if (value === 'Nenhum' || value === response['meu_nome']) {
                                    const icon = motorista_nome.parentNode.querySelector('i')
                                    icon.classList.remove('inactive')
                                }
                            } else {
                                const icon = motorista_nome.parentNode.querySelector('i')
                                icon.classList.remove('inactive')
                            }
                        }
                        dado = 'nome'
                    }
                    const tag_info = element.querySelector(`[id*="${dado}"]`)
                    tag_info.textContent = value
                    if (dado !== 'nome' && (response['relacao'] === 'dono' || response['relacao'] == 'adm')) {
                        let icon = tag_info.parentNode.querySelector('i')
                        if (!icon) {icon = tag_info.parentNode.parentNode.querySelector('i')}
                        icon.classList.remove('inactive')
                    }
                }

                element.classList.remove('inactive')
                container_veicles.appendChild(element)
            }

        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function loadInterfacePoints(name_line) {
    fetch(`/get_interface-points?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const model = document.getElementById('interface_model_ponto')
            const local_pontos = document.getElementById('interface_pontos_local')
            const division = document.getElementById('interface_pontos_division')
            const add_ponto = document.getElementById('interface_pontos_add')

            const relacao = response['relacao']
            const data = response['data']
            
            local_pontos.innerHTML = ''
            document.getElementById('interface_pontos_quantidade').textContent = response['quantidade']
            division.classList.add('inactive')
            add_ponto.classList.add('inactive')
            if (data.length) {
                if (relacao && relacao !== 'membro') {
                    division.classList.remove('inactive')
                    add_ponto.classList.remove('inactive')
                }

                for (index in data) {
                    const ponto = model.cloneNode(true)
                    ponto.id = `${local_pontos.id}-ponto_${index}`
                    const text = ponto.querySelector('p')
                    text.textContent = data[index]
                    text.id = ponto.id + '_nome'
    
                    if (relacao) {
                        ponto.onclick = function() {
                            open_popup_edit('config_ponto', this)
                        }
                        ponto.querySelector('i').classList.remove('inactive')
                        ponto.classList.add('grow')
                    }
                    
                    ponto.classList.remove('inactive')
                    local_pontos.appendChild(ponto)
                }
            } else {
                if (relacao && relacao !== 'membro') {
                    add_ponto.classList.remove('inactive')
                }
            }
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}


function loadInterfaceRoutes(name_line) {
    const model_route = document.getElementById('model_interface_rota')
    function load_route(list_itens, container_include) {
        for (index in list_itens) {
            const route = model_route.cloneNode(true)
            route.id = `${container_include.id}-rota_${index}`

            ids = route.querySelectorAll(`[id*="${model_route.id}"]`)
            ids.forEach(element => {
                element.id = element.id.replace(model_route.id, route.id)
            })

            const dados = list_itens[index]
            for (dado in dados) {
                const info = route.querySelector(`[id*="${dado}"]`)
                info.textContent = dados[dado]
            }
            route.classList.remove('inactive')
            container_include.appendChild(route)
        }
    }

    fetch(`/get_interface-routes?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const local_ativas = document.getElementById('interface_rotas_ativas')
            const ativas = response['ativas']

            local_ativas.innerHTML = ''
            if (response['role'] == 'motorista') {
                const container_desativas = document.getElementById('interface_rotas_desativas')
                const local_desativas = container_desativas.querySelector('div')
                const desativas = response['desativas']

                local_desativas.innerHTML = ''
                container_desativas.classList.add('inactive')

                document.getElementById('interface_rotas_quantidade').textContent = response['quantidade']
                const route_division = document.getElementById('interface_rotas_division')
                const route_add = document.getElementById('interface_rotas_add')

                route_division.classList.add('inactive')
                route_add.classList.add('inactive')
                if (response['relacao'] && response['relacao'] !== 'membro') {
                    route_add.classList.remove('inactive')
                    if (ativas.length || desativas.length) {
                        route_division.classList.remove('inactive')
                        if (desativas.length) {
                            container_desativas.classList.remove('inactive')
                        }
                    }
                }
                load_route(desativas, local_desativas)
            }
            load_route(ativas, local_ativas)
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}
