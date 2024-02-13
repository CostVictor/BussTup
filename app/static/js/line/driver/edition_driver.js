function create_vehicle() {
    const name_line = document.getElementById('interface_nome').textContent
    const placa = document.getElementById('add_vehicle_placa').value
    const capacidade = document.getElementById('add_vehicle_capacidade').value
    const options = return_bool_selected(document.getElementById('add_vehicle_options'))

    let execute = true
    if (options) {
        const container = document.getElementById('add_vehicle_options_container')
        const motorista_selected = return_option_selected(container)

        if (!motorista_selected) {
            execute = false
            var title = 'Nenhuma Opção Selecionada'
            var text = 'Selecione uma opção de motorista disponível.'
        }
    }

    if (execute) {
        fetch("/create_vehicle", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'placa': placa, 'capacidade': capacidade, 'motorista_nome': motorista_nome, 'name_line': name_line})
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                close_popup('add_vehicle')
                create_popup(response.title, response.text, 'Ok', 'success')
                loadInterfaceVehicle(name_line)
            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    } else {create_popup(title, text, 'Voltar')}
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
        if (!response.error) {
            close_popup('add_point')
            create_popup(response.title, response.text, 'Ok', 'success')
            loadInterfacePoints(name_line)
        } else {create_popup(response.title, response.text, 'Voltar')}
    })
}


function create_route(event) {
    event.preventDefault()

    const name_line = document.getElementById('interface_nome').textContent
    const turno = document.getElementById('add_route_turno').value.trim()
    const hr_partida = document.getElementById('add_route_horario_partida').value.trim()
    const ht_retorno = document.getElementById('add_route_horario_retorno').value.trim()
    const option_selected = return_bool_selected(document.getElementById('add_route_options'))

    let execute = true
    if (option_selected) {
        const plate_selected = return_option_selected(document.getElementById('add_route_options_container'))

        if (plate_selected) {
            var vehicle = plate_selected.split(' ')[0]
        } else {
            execute = false
            var title = 'Nenhuma Opção Selecionada'
            var text = 'Selecione uma opção de veículo disponível.'
        }
    } else {var vehicle = 'Nenhum'}

    if (execute) {
        const data = {
            'turno': turno, 
            'horario_partida': hr_partida,
            'horario_retorno': ht_retorno,
            'plate': vehicle,
            'name_line': name_line
        }
        
        fetch("/create_route", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                close_popup('add_route')
                create_popup(response.title, response.text, 'Ok', 'success')
                loadInterfaceRoutes(name_line)
            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    } else {create_popup(title, text, 'Voltar')}
}


function create_stop(event) {
    event.preventDefault()
    let execute = true

    const horario_ponto = document.getElementById('add_point_route_horario').value.trim()
    const horario_ponto_reverso = document.getElementById('add_point_route_horario_inverso').value.trim()
    const container_points = document.getElementById('add_point_route_container')
    const container_options = document.getElementById('add_point_route_options')

    let point_selected = return_option_selected(container_points)
    let option_selected = return_bool_selected(container_options)
    if (!point_selected) {
        execute = false
        var title = 'Nenhum Ponto Selecionado'
        var text = 'Por favor, selecione uma opção disponível para proseguir.'
    } else if (option_selected) {
        if (!horario_ponto_reverso) {
            execute = false
            var title = 'Horário não definido'
            var text = 'Nenhum horário para o ponto no trajeto inverso foi definido.'
        }
    }

    if (execute) {
        const data = return_data_route()
        data['name_point'] = point_selected
        data['type'] = document.getElementById('add_point_route_type').textContent
        data['time_pas'] = horario_ponto
        if (option_selected) {
            data['time_pas_2'] = horario_ponto_reverso
        }

        fetch("/create_stop", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                loadInterfaceRoutes(data.name_line)
                config_popup_route(null, return_data_route())
                close_popup('add_point_route')
                create_popup(response.title, response.text, 'Ok', 'success')
            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    } else {create_popup(title, text, 'Voltar')}
}


function edit_line(form_submit, event) {
    event.preventDefault()

    let field = form_submit.id.split('_')
    field = field[field.length - 1]

    if (field === 'cartela' || field === 'diaria') {
        field = 'valor_' + field
    }
    
    let execute = true
    const name_line = document.getElementById('interface_nome').textContent
    const new_value = document.getElementById(`edit_${field}_line_new`)

    const data = {'name_line': name_line, 'field': field, 'new_value': new_value.value.trim()}
    if (field === 'nome' || field === 'cidade') {
        const password = document.getElementById(`edit_${field}_line_conf`).value.trim()
        data['password'] = password

    } else if (field === 'valor_cartela' || field === 'valor_diaria') {
        if (new_value.value === '') {
            var title = 'Campo Vazio'
            var text = 'O campo não pode estar vazio.'
            execute = false
            
        } else if (new_value.value <= 0) {
            var title = 'Valor Inválido'
            var text = 'O valor deve ser maior que 0.'
            execute = false
        }
    }

    if (execute) {
        fetch("/edit_line", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                close_popup(`edit_${field}_line`)

                if (field === 'nome') {
                    const redirect = `line/${encodeURIComponent(new_value.value.trim())}?local_page=linhas`
                    const text = 'Precisaremos recarregar sua página para ajustar a rota de acesso à sua linha.'
                    create_popup(response.title, text, 'Ok', 'success', redirect)
                } else {
                    loadInterfaceLine(name_line, false)
                    create_popup(response.title, response.text, 'Ok', 'success')
                    
                    const local = document.getElementById(`config_line_${field}`)
                    if (local) {local.textContent = new_value.value.trim()}
                }
    
    
            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    } else {create_popup(title, text, 'Voltar')}
}


function edit_config_line_bool(obj_click) {
    if (!obj_click.querySelector('i').className.includes('selected')) {
        const name_line = document.getElementById('interface_nome').textContent
        const opcao = obj_click.querySelector('p').textContent
        const content = document.getElementById('interface_line_content')
        const elements = Array.from(content.children)
        content.classList.add('inactive')

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
            if (!response.error) {
                loadInterfaceLine(name_line, false)
                if (opcao === 'Sim') {
                    animate_itens(elements, 'fadeDown', 0.5, 0.07, 0.07, 0, field)
                } else (animate_itens(elements, 'fadeDown', 0.5, 0.07, 0.07, 0))
                content.classList.remove('inactive')
            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    }
}


function edit_capacidade_veiculo(event) {
    event.preventDefault()

    const name_line = document.getElementById('interface_nome').textContent
    const vehicle_plate = document.getElementById('edit_vehicle_capacidade').querySelector('span').textContent
    const new_value = document.getElementById('edit_vehicle_capacidade_new').value.trim()

    fetch("/edit_vehicle", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': 'capacidade', 'new_value': new_value, 'name_line': name_line, 'plate': vehicle_plate})
    })
    .then(response => response.json())
    .then(response => {
        if (!response.error) {
            close_popup('edit_vehicle_capacidade')
            create_popup(response.title, response.text, 'Ok', 'success')
            loadInterfaceVehicle(name_line)
        } else {create_popup(response.title, response.text, 'Voltar')}
    })
}


function edit_motorista_veiculo() {
    const name_line = document.getElementById('interface_nome').textContent
    const vehicle_plate = document.getElementById('edit_vehicle_motorista').querySelector('span').textContent
    const options_selected = return_option_selected(document.getElementById('edit_vehicle_motorista_container'))

    if (!options_selected) {
        create_popup('Nenhuma Opção Selecionada', 'Por favor, selecione uma opção disponível.', 'Voltar')
    } else {
        fetch("/edit_vehicle", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'field': 'motorista', 'new_value': options_selected, 'name_line': name_line, 'plate': vehicle_plate})
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                close_popup('edit_vehicle_motorista')
                create_popup(response.title, response.text, 'Ok', 'success')
                loadInterfaceVehicle(name_line)
                loadInterfaceRoutes(name_line)
            } else {create_popup(response.title, response.text, 'Voltar')}
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
    const name_point = document.getElementById('config_point_nome').textContent

    fetch("/edit_point", {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'field': field, 'new_value': new_value, 'name_line': name_line, 'name_point': name_point})
    })
    .then(response => response.json())
    .then(response => {
        if (!response.error) {
            close_popup('edit_point_' + field)
            create_popup(response.title, response.text, 'Ok', 'success')
            loadInterfacePoints(name_line)
            document.getElementById('config_point_' + field).textContent = new_value
        } else {create_popup(response.title, response.text, 'Voltar')}
    })
}


function edit_route(obj_reference, event = false) {
    if (event) {event.preventDefault()}
    
    let field = obj_reference.id.split('_')
    field = field[field.length - 1]

    if (field === 'partida' || field === 'retorno') {
        field = 'horario_' + field 
    }

    let execute = true
    if (field === 'onibus') {
        const container = document.getElementById('edit_route_onibus_container')
        const item_selected = container.querySelector('[class*="selected"]')
        if (item_selected) {
            var new_value = item_selected.querySelector('p').textContent.trim().split(' ')[0]
        } else {
            create_popup('Nenhuma Opção Selecionada', 'Por favor, selecione uma opção disponível.', 'Voltar')
            execute = false
        }
    } else {var new_value = obj_reference.querySelector('input').value.trim()}

    if (execute) {
        const data = return_data_route()
        data['field'] = field
        data['new_value'] = new_value

        fetch("/edit_route", {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(response => {
            if (!response.error) {
                const btn_route = document.getElementById('interface_rotas_btn')
                if (field === 'onibus') {action_container(btn_route)}

                loadInterfaceRoutes(data.name_line)
                close_popup('config_route')
                close_popup(obj_reference.id.replace('formulario_', ''))
                create_popup(response.title, response.text, 'Ok', 'success')

            } else {create_popup(response.title, response.text, 'Voltar')}
        })
    }
}
