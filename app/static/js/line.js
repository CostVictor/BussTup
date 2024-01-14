// ~~ Edit ~~ //

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
                loadInterfaceLinha(false, name_line, false)
            }
        })
    }
}


function edit_valor() {
    const msg = document.getElementById('edit_valor_msg').textContent
    const new_value = document.getElementById('edit_valor_new').value
    const name_line = document.getElementById('interface_nome').textContent
    let field = 'valor_cartela'

    if (msg.includes('diária')) {
        field = 'valor_diaria'
    }

    fetch("/edit_line", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': field, 'new_value': new_value, 'name_line': name_line})
    })
    .then(response => response.json())
    .then(response => {
        cancel_popup_edit('edit_valor')
        if (!response['error']) {
            loadInterfaceLinha(false, name_line, false)
            create_popup(response['title'], '', 'Ok', 'success')
        }
    })
}


// ~~ Carregamento ~~ //

function loadInterfaceLinha(obj_linha, nome_linha = false, load_complete = true) {
    if (nome_linha) {
        name_reference = nome_linha
    } else {
        name_reference = obj_linha.querySelector('[id*="nome"]').textContent
    }
    fetch(`/get_interface-line?name_line=${encodeURIComponent(name_reference)}`, { method: 'GET' })
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
                    } else if (response['relacao'] === 'adm') {
                        adm = true
                    }
                } else {aviso_entrada.classList.remove('inactive')}
            } else {
                if (response['relacao']) {
                    if (response['relacao'] === 'de outra linha') {

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
                setTimeout(() => {
                    loadMotoristaInterface(name_reference)
                }, 100)
            
                if (response['role'] === 'motorista') {
                    setTimeout(() => {
                        loadVeiculoInterface(name_reference)
                    }, 200)
                }
            }

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}


function loadMotoristaInterface(nome_linha) {
    fetch(`/get_interface-driver?name_line=${encodeURIComponent(nome_linha)}`, { method: 'GET' })
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
                    if (response['role'] === 'motorista' && response['relacao'] === 'dono' && tipo !== 'dono') {
                        const btn_config = motorista.querySelector('[id*="btn"]')
                        btn_config.classList.remove('inactive')
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


function loadVeiculoInterface(nome_linha) {
    fetch(`/get_interface-veicle?name_line=${encodeURIComponent(nome_linha)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const area_onibus = document.getElementById('area_onibus')
            const division = area_onibus.querySelector('h1.page__division')
            const btn_add = area_onibus.querySelector('div.justify')
            data = response['data']

            if (response['relacao'] === 'dono' || response['relacao'] === 'adm') {
                if (data) {
                    division.classList.remove('inactive')
                } else {division.classList.add('inactive')}
            } else {
                division.classList.add('inactive')
                btn_add.classList.add('inactive')
            }

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}
