var templates = document.getElementById('templates_model')
var models = document.importNode(templates.content, true)

function action_popup(popup, card, id, obj_click) {
    if (id === 'edit_vehicle_capacidade') {
        const placa_capacidade = extract_info(obj_click, 'placa')
        popup.querySelector('span').textContent = placa_capacidade
        card.querySelector('h2').textContent = `Digite a capacidade de ${placa_capacidade}:`

   } else if (id === 'edit_vehicle_motorista') {
        const data = {
            'principal': [document.getElementById('interface_nome').textContent],
            'secondary': {}
        }

        const placa_vehicle = extract_info(obj_click, 'placa')
        const info_atual = extract_info(obj_click, 'motorista')
        popup.querySelector('span').textContent = placa_vehicle
        card.querySelector('h2').textContent = `Selecione o motorista de ${placa_vehicle}:`

        const container = document.getElementById('edit_vehicle_motorista_container')
        container.innerHTML = ''

        let option_nenhum = true
        if (info_atual === 'Nenhum') {
            option_nenhum = false
        }
        include_options_container(container, 'option_driver', data, option_nenhum)

   } else if (id === 'config_motorista') {
       card.querySelector('h1').textContent = extract_info(obj_click, 'nome')

   } else if (id === 'config_aluno') {
       card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'title')

   } else if (id === 'config_point') {
       config_popup_point(extract_info(obj_click, 'nome'))

    } else if (id === 'config_route') {
        config_popup_route(obj_click)
        document.getElementById('config_route_pos').textContent = obj_click.querySelector('span').textContent
        
   } else if (id === 'config_line') {
        card.querySelector('h1').textContent = extract_info(obj_click, 'nome')
        card.querySelector('p#config_line_cidade').textContent = extract_info(obj_click, 'cidade')
        const options_ferias = document.getElementById('config_line_options_ferias')
        const options_gratuidade = document.getElementById('config_line_options_gratuidade')
        const info_ferias = document.getElementById('interface_ferias')
        const area_paga = document.getElementById('area_paga')

        if (info_ferias.className.includes('inactive')) {
            config_bool(options_ferias, 'Não')
        } else {config_bool(options_ferias, 'Sim')}

        if (area_paga.className.includes('inactive')) {
            config_bool(options_gratuidade, 'Não')
        } else {config_bool(options_gratuidade, 'Sim')}

   } else if (id === 'add_vehicle' || id === 'add_route') {
        const data = {
            'principal': [document.getElementById('interface_nome').textContent],
            'secondary': {}
        }
       const container = card.querySelector('div#' + popup.id + '_options_container')
       container.innerHTML = ''
       const option = id === 'add_vehicle' ? 'option_driver' : 'option_vehicle'
       include_options_container(container, option, data)

   } else if (id == 'promover_motorista' || id === 'rebaixar_motorista' || id === 'del_ponto' || id === 'del_linha') {
       card.querySelector('h2').textContent = extract_info(obj_click, 'nome')
       
   } else if (id === 'del_vehicle') {
       card.querySelector(`h2#${id}_placa`).textContent = extract_info(obj_click, 'placa')
       
   } else if (id === 'config_relacao_ponto_rota') {
       card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'nome')
       card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(obj_click, 'number')
       card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(obj_click, 'horario')

   } else if (id === 'edit_route_onibus') {
       const data = {
           'principal': [document.getElementById('interface_nome').textContent],
           'secondary': {'plate_ignore': extract_info(obj_click, 'onibus')}
       }
       const container = document.getElementById(id + '_container')
       container.innerHTML = ''

       let option_nenhum = true
       if (data.secondary.plate_ignore === 'Não definido') {
           option_nenhum = false
       }
       include_options_container(container, 'option_vehicle', data, option_nenhum)

   } else if (id === 'add_point_route') {
       const container = document.getElementById(id + '_container')
       const data = return_data_route(null, format_dict_url=true)

       let tipo = obj_click.id.trim().split('_')
       tipo = tipo[tipo.length - 1]

       data['principal'].push(tipo)
       container.innerHTML = ''
       container.classList.remove('inactive')
       popup.querySelector('span').textContent = tipo
       include_options_container(container, 'option_point', data, false, true)

   } else if (id === 'config_rel_point_route') {
        const data = return_data_route(null, format_dict_url=true)
        data.principal.push(obj_click.id.includes('partida') ? 'partida' : 'retorno')
        data.principal.push(extract_info(obj_click, 'nome'))
        document.getElementById('config_rel_point_route_ordem').textContent = extract_info(obj_click, 'number')
        config_popup_relationship(data)
   }
}


function loadInterfaceVehicle(name_line) {
    fetch(`/get_interface-vehicle/${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response.error) {
            const area_onibus = document.getElementById('area_onibus')
            const container_vehicles = document.getElementById('area_onibus_content')
            const division = area_onibus.querySelector('h1.page__division')
            const btn_add = document.getElementById('area_onibus_btn_add')
            
            const data = response.data
            container_vehicles.innerHTML = ''
            division.classList.add('inactive')
            btn_add.classList.add('inactive')
            
            if (response.relacao === 'dono' || response.relacao === 'adm') {
                btn_add.classList.remove('inactive')
                if (data.length) {division.classList.remove('inactive')}
            }

            const model_vehicle = models.querySelector('#model_onibus')    
            for (vehicle in data) {
                const element = model_vehicle.cloneNode(true)
                element.id = `veiculo_${vehicle}`

                const ids = element.querySelectorAll('[id*="model_onibus"]')
                ids.forEach(item => {
                    item.id = item.id.replace('model_onibus', element.id)
                    if (item.id.includes('delete') && (response.relacao === 'dono' || response.relacao == 'adm')) {
                        item.classList.remove('inactive')
                    }
                })

                for (dado in data[vehicle]) {
                    const value = data[vehicle][dado]

                    if (dado === 'motorista_nome') {
                        const motorista_nome = element.querySelector('[id*="motorista"]')
                        motorista_nome.textContent = value
                        if (response.relacao) {
                            if (response.relacao === 'membro') {
                                if (value === 'Nenhum' || value === response.meu_nome) {
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
                    if (dado !== 'nome' && (response.relacao === 'dono' || response.relacao == 'adm')) {
                        let icon = tag_info.parentNode.querySelector('i')
                        if (!icon) {icon = tag_info.parentNode.parentNode.querySelector('i')}
                        icon.classList.remove('inactive')
                    }
                }

                element.classList.remove('inactive')
                container_vehicles.appendChild(element)
            }

        } else {create_popup(response.title, response.text, 'Voltar')}
    })
}


function loadInterfacePoints(name_line) {
    fetch(`/get_interface-points/${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response.error) {
            const model = models.querySelector('#interface_model_ponto')
            const local_pontos = document.getElementById('interface_pontos_local')
            const division = document.getElementById('interface_pontos_division')
            const add_ponto = document.getElementById('interface_pontos_add')

            const relacao = response.relacao
            const data = response.data
            
            local_pontos.innerHTML = ''
            document.getElementById('interface_pontos_quantidade').textContent = response.quantidade
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
                            open_popup('config_point', this)
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
        } else {create_popup(response.title, response.text, 'Voltar')}
    })
}


function create_aluno(list_aluno, container, model_aluno) {
    for (index in list_aluno) {
        const aluno = model_aluno.cloneNode(true)
        aluno.id = `${container.id}-aluno_${index}`
        const nome = aluno.querySelector('p')
        nome.textContent = list_aluno[index]
        nome.id = aluno.id + '_nome'

        if (index) {
            if (list_aluno[index - 1] === nome.textContent) {
                const aluno_ant = document.getElementById(`${container.id}-aluno_${index - 1}`)
                const span_ant = aluno_ant.querySelector('span')
                if (!span_ant.textContent) {span_ant.textContent = 0}
                aluno.querySelector('span').textContent = parseInt(span_ant.textContent) + 1
            }
        }

        if (response.relacao !== 'membro') {
            aluno.classList.add('grow')
            aluno.querySelector('i').classList.remove('inactive')
            aluno.onclick = function() {
                open_popup('config_aluno', this)
            }
        }
        aluno.classList.remove('inactive')
        container.appendChild(aluno)
    }
}


function config_popup_point(name_point) {
    const name_line = document.getElementById('interface_nome').textContent
    const get = {'principal': [name_line, name_point]}
    const model_aluno = models.querySelector('#interface_model_aluno')

    fetch('/get_point' + generate_url_dict(get), { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response.error) {
            const data = response.info
            const utilizacao = response.utilizacao
            const turnos = response.turnos

            for (info in data) {
                const local = document.getElementById('config_point_' + info)
                local.textContent = data[info]

                if (response.relacao !== 'membro') {
                    document.getElementById(local.id + '_edit').classList.remove('inactive')
                }
            }

            document.getElementById('config_point_utilizacao_btn').querySelector('p').textContent = utilizacao.quantidade
            const model_rota = models.querySelector('#model_interface_rota')
            const utilizacao_container = document.getElementById('config_point_utilizacao_container')
            utilizacao_container.innerHTML = ''

            for (index in utilizacao.rotas) {
                const route = model_rota.cloneNode(true)
                route.querySelector('div.popup__input_big').classList.add('max')
                route.querySelector('p.display').classList.add('min')
                route.id = `${utilizacao_container.id}-rota_${index}`

                ids = route.querySelectorAll('[id*="interface_model_rota"]')
                ids.forEach(value => {
                    value.id = value.id.replace(model_rota.id, route.id)
                })

                const dados = utilizacao.rotas[index]
                for (dado in dados) {
                    route.querySelector(`[id*="${dado}"]`).textContent = dados[dado]
                }

                if (index) {
                    let qnt = 0
                    const dados_ant = utilizacao.rotas[index - 1]
                    for (num in dados_ant) {
                        if (dados_ant[num] === dados[num]) {qnt++}
                    }

                    if (qnt === Object.keys(dados).length) {
                        const route_ant = document.getElementById(`${utilizacao_container.id}-rota_${index - 1}`)
                        const span_ant = route_ant.querySelector('span')
                        if (!span_ant.textContent) {span_ant.textContent = 0}
                        route.querySelector('span').textContent = parseInt(span_ant.textContent) + 1
                    }
                }

                route.classList.remove('inactive')
                utilizacao_container.appendChild(route)
            }
            
            for (turno in turnos) {
                const btn = document.getElementById(`config_point_${turno}_btn`)
                const container_turno = document.getElementById(`config_point_${turno}_area`)
                const container_contraturno = document.getElementById(`config_point_${turno}_area_contraturno`)

                const info = turnos[turno]
                btn.querySelector('p').textContent = info.quantidade
                create_aluno(info.alunos, container_turno, model_aluno)
                create_aluno(info.container, container_contraturno, model_aluno)
            }

        } else {
            close_popup('config_point')
            create_popup(response.title, response.text, 'Voltar')
        }
    })
}


function set_sequence(obj_child) {
    const container = obj_child.parentNode
    elements = Array.from(container.children)
    elements.forEach((element, index) => {
        const tag_sequence = element.querySelector('[id*="number"]')
        tag_sequence.textContent = index + 1
    })
}


$(function() {
    $(".sortable").sortable({
        handle: '.icon_move',
        tolerance: 'pointer',
        forcePlaceholderSize: true,

        start: function(event, ui) {
            var icon = ui.item.find('i')
            var number = ui.item.find('h4')
            var text = ui.item.find('p')

            icon.addClass('shadow')
            icon.addClass('grabbing')
            number.addClass('shadow')
            text.addClass('shadow')
        },
        stop: function(event, ui) {
            var icon = ui.item.find('i')
            var number = ui.item.find('h4')
            var text = ui.item.find('p')
            
            set_sequence(ui.item[0])
            icon.removeClass('grabbing')
            setTimeout(() => {
                icon.removeClass('shadow')
                number.removeClass('shadow')
                text.removeClass('shadow')
            }, 400)
        },
    })
})
