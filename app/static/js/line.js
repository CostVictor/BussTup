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
            create_popup(response['title'], '', 'Ok', 'success')
            document.getElementById('config_linha_nome').textContent = new_name

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
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
            create_popup(response['title'], '', 'Ok', 'success')
            document.getElementById('config_linha_cidade').textContent = new_cidade

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}


function edit_config_bool(obj_click) {
    if (!obj_click.querySelector('i').className.includes('selected')) {
        const name_line = document.getElementById('interface_nome').textContent
        const opcao = obj_click.querySelector('p').textContent

        let field = 'particular'
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
            }
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
            cancel_popup_edit('edit_valor')
            if (!response['error']) {
                loadInterfaceLine(name_line, false)
                create_popup(response['title'], '', 'Ok', 'success')
            }
        })
    }
}


// ~~ Criação ~~ //

function create_veiculo() {
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
        body: JSON.stringify({'placa': placa, 'capacidade_sentado': capacidade, 'Motorista_nome': motorista_nome, 'name_line': name_line})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            cancel_popup_edit('add_veicle')
            create_popup(response['title'], response['text'], 'Ok', 'success')
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
                const sem_participacao = document.getElementById('interface_sem_participacao')
                const cadastrar = document.getElementById('interface_cadastrar')
                const bloqueio = document.getElementById('interface_bloqueio')

                sem_participacao.classList.remove('inactive')
                cadastrar.classList.remove('inactive')
                bloqueio.classList.add('inactive')

                if (response['relacao']) {
                    if (response['relacao'] === 'de outra linha') {
                        sem_participacao.classList.add('inactive')
                        cadastrar.classList.add('inactive')
                        bloqueio.classList.remove('inactive')
                    }
                } else {aviso_entrada.classList.remove('inactive')}
            }

            for (dado in response['data']) {
                if (dado === 'particular') {
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

            for (tipo in data) {
                for (pos in data[tipo]) {
                    const model_motorista = document.getElementById('model_motorista')
                    const motorista = model_motorista.cloneNode(true)
                    motorista.id = `motorista_${tipo}_${pos}`
                    
                    const elements = motorista.querySelectorAll('[id*="model_motorista"]')
                    elements.forEach(element => {
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
            
            data = response['data']
            container_veicles.innerHTML = ''
            division.classList.add('inactive')
            btn_add.classList.add('inactive')
            
            if (response['relacao'] === 'dono' || response['relacao'] === 'adm') {
                btn_add.classList.remove('inactive')
                if (data) {division.classList.remove('inactive')}
            }

            const model_veicle = document.getElementById('model_onibus')    
            for (veicle in data) {
                const element = model_veicle.cloneNode(true)
                element.id = `veiculo_${veicle}`

                const ids = element.querySelectorAll('[id*="model_onibus"]')
                ids.forEach(item => {
                    item.id = item.id.replace('model_onibus', element.id)
                })

                for (dado in data[veicle]) {
                    const value = data[veicle][dado]

                    if (dado === 'Motorista_nome') {
                        const motorista_nome = element.querySelector('[id*="motorista"]')
                        motorista_nome.textContent = value
                        dado = 'nome'
                    }
                    const tag_info = element.querySelector(`[id*="${dado}"]`)
                    tag_info.textContent = value
                }

                element.classList.remove('inactive')
                container_veicles.appendChild(element)
            }

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}
