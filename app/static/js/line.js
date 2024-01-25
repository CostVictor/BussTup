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
        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
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
                }
            }

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
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
        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
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

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}
