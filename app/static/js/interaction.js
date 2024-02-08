function action_popup(popup, card, id, obj_click) {
    switch (id) {
        case 'edit_valor':
            card.querySelector('h2').textContent = `Digite o novo valor da ${obj_click.id.includes('cartela') ? 'cartela' : 'diária'}:`
            break
        
        case 'edit_vehicle_capacidade':
            const placa_capacidade = extract_info(obj_click, 'placa')
            popup.querySelector('span').textContent = placa_capacidade
            card.querySelector('h2').textContent = `Digite a capacidade de ${placa_capacidade}:`
            break

        case 'edit_vehicle_motorista':
            const name_line = {'name_line': document.getElementById('interface_nome').textContent}
            const placa_vehicle = extract_info(obj_click, 'placa')
            const info_atual = extract_info(obj_click, 'motorista')
            popup.querySelector('span').textContent = placa_vehicle
            card.querySelector('h2').textContent = `Selecione o motorista de ${placa_vehicle}:`

            const container_vehicle_motoristas = document.getElementById('edit_vehicle_motorista_container')
            container_vehicle_motoristas.innerHTML = ''

            let option_nenhum = true
            if (info_atual === 'Nenhum') {
                option_nenhum = false
            }
            include_options_container(container_vehicle_motoristas, 'option_driver', name_line, option_nenhum)
            break

        case 'config_motorista':
            card.querySelector('h1').textContent = extract_info(obj_click, 'nome')
            break

        case 'config_aluno':
            card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'title')
            break
        
        case 'config_point':
            config_popup_point(extract_info(obj_click, 'nome'))
            break
        
        case 'config_route':
            config_popup_route(obj_click)
            break
        
        case ('edit_ponto_nome'):
            popup.querySelector('span').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'edit_ponto_tempo_tolerancia':
            popup.querySelector('span').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'edit_ponto_linkGPS':
            popup.querySelector('span').textContent = extract_info(obj_click, 'nome')
            break

        case 'config_line':
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
            break
        
        case 'add_vehicle':
            const container_motoristas = card.querySelector('div#' + popup.id + '_options_container')
            container_motoristas.innerHTML = ''
            include_options_container(container_motoristas, 'option_driver')
            break
        
        case 'add_route':
            const container_vehicles = card.querySelector('div#' + popup.id + '_options_container')
            container_vehicles.innerHTML = ''
            include_options_container(container_vehicles, 'option_vehicle')
            break

        case 'promover_motorista':
            card.querySelector('h2').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'rebaixar_motorista':
            card.querySelector('h2').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'del_ponto':
            card.querySelector('h2').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'del_linha':
            card.querySelector('h2').textContent = extract_info(obj_click, 'nome')
            break
        
        case 'del_vehicle':
            card.querySelector(`h2#${id}_placa`).textContent = extract_info(obj_click, 'placa')
            break

        case 'config_relacao_ponto_rota':
            card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'nome')
            card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(obj_click, 'number')
            card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(obj_click, 'horario')
            break
    }
}


function action_container(obj_click, set_limit = false) {
    const icon = obj_click.querySelector('i')
    const container = document.getElementById(obj_click.id.replace('btn', 'container'))
    const elements = Array.from(container.children)
    obj_click.style.transition = '0s ease'
    container.removeAttribute('style')

    if (obj_click.id.includes('veiculo')) {
        const motorista_nome = obj_click.querySelectorAll('h3')
        motorista_nome.forEach((element, index) => {
            if (!index) {
                if (icon.className.includes('open')) {
                    element.classList.remove('max_width')
                } else {element.classList.add('max_width')}
            } else {
                if (icon.className.includes('open')) {
                    element.classList.remove('inactive')
                } else {element.classList.add('inactive')}
            }
        })
    }

    animate_itens(elements)
    if (icon.className.includes('open')) {
        container.classList.add('inactive')
        icon.classList.remove('open')

        elements.forEach(element => {
            element.classList.remove('selected')
        })
    } else {
        container.classList.remove('inactive')
        container.scrollTop = 0
        icon.classList.add('open')

        if (set_limit) {
            set_limitScroll(container, set_limit)
        } else {
            set_limitScroll(container)
        }
    }

    const btn_children = container.querySelectorAll('[id*="btn"]')
    if (btn_children) {
        btn_children.forEach(btn => {
            const icon = btn.querySelector('i')
            if (icon.className.includes('open')) {
                action_container(btn)
            }
        })
    }

    const rolament = container.querySelector('div.scroll_vertical')
    if (rolament) { rolament.scrollTop = 0 }

    elements.forEach(element => {
        if (element.className.includes('scroll')) {
            set_limitScroll(element)
        }
    })
}


function open_popup(id, obj_click=false) {
    document.body.classList.add('no-scroll')
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    popup.classList.remove('inactive')
    popup.classList.remove('close')
    card.classList.remove('close')

    if (obj_click) {
        action_popup(popup, card, id, obj_click)
    }
}


function close_popup(id, reset_bool = false, reference_bool = 'Não') {
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    const scrolls = popup.querySelectorAll('div.scroll_vertical')

    card.classList.add('close')
    popup.classList.add('close')
    setTimeout(() => {
        popup.classList.add('inactive')
        document.body.classList.remove('no-scroll')
        
        if (popup.querySelector('form')) {
            const inputs = popup.querySelectorAll('input')
            inputs.forEach(element => {
                element.classList.remove('input_error')
                element.value = ''
            })
        }
        if (reset_bool) {
            const options = card.querySelectorAll('div.popup__input.bool')
            options.forEach(element => {
                const icon = element.querySelector('i')
                const text = element.querySelector('p')
                if (text.textContent !== reference_bool) {
                    icon.className = 'bi bi-circle popup__icon ratio'
                } else {
                    const titles = popup.querySelectorAll('h3.popup__text.info.space')
                    const containers = popup.querySelectorAll('[id*="container"]')

                    icon.className = 'bi bi-check2-circle popup__icon ratio selected'
                    if (titles && containers) {
                        titles.forEach(element => {
                            text.textContent == 'Não' ? element.classList.add('inactive') : element.classList.remove('inactive')
                        })
                        containers.forEach(element => {
                            if (element.id !== 'scroll_principal') {
                                text.textContent == 'Não' ? element.classList.add('inactive') : element.classList.remove('inactive')

                                Array.from(element.children).forEach(item => {
                                    item.classList.remove('selected')
                                })
                            }
                        })
                    }
                }
            })
        } else {
            const containers = popup.querySelectorAll('[id*="container"]')
            if (containers) {
                containers.forEach(element => {
                    Array.from(element.children).forEach(item => {
                        item.classList.remove('selected')
                    })
                })
            }
        }
        const btns = popup.querySelectorAll('[id*="btn"]')
        if (btns) {
            btns.forEach(btn => {
                const icon = btn.querySelector('i')
                if (icon && icon.className.includes('open')) {
                    action_container(btn)
                }
            })
        }

    }, 100)
    scrolls.forEach(element => {
        element.scrollTop = 0
    })
    copy_text()
}


function config_bool(container_options, reference = 'Sim') {
    const icon_selected = container_options.querySelector('i.selected')
    const text_selected = icon_selected.parentNode.querySelector('p').textContent
    const option = container_options.querySelector('i:not(.selected)').parentNode
    if (text_selected !== reference) {popup_selectOption(option, true)}
}


function popup_confirmBox(item) {
    icon = item.querySelector('i')
    if (icon.className.includes('selected')) {
        icon.classList.replace('bi-check2-circle', 'bi-circle')
        icon.classList.remove('selected')
    } else {
        icon.classList.replace('bi-circle', 'bi-check2-circle')
        icon.classList.add('selected')
    }
}


function popup_selectOption(obj_click,  open_boxOptions = false, multiple_options = false) {
    const reference = obj_click.parentNode
    const reference_elements = Array.from(reference.children)
    const text = obj_click.querySelector('p')
    const icon = obj_click.querySelector('i')

    if (!multiple_options) {
        if (!icon.className.includes('selected')) {
            reference_elements.forEach(item => {popup_confirmBox(item)})
            if (open_boxOptions) {
                const title_options = document.getElementById(`${reference.id}_title`)
                const reference_container = document.getElementById(`${reference.id}_container`)
                const list_itens = reference_container ? reference_container.querySelectorAll('div') : false

                if (text.textContent === 'Sim') {
                    if (title_options) {title_options.classList.remove('inactive')}
                    if (reference_container) {
                        reference_container.classList.remove('inactive')
                        reference_container.scrollTop = 0
                        set_limitScroll(reference_container)
                        animate_itens(list_itens)
                    }
                } else {
                    if (reference_container) {
                        const options = reference_container.querySelectorAll('div')
                        options.forEach(item => {item.classList.remove('selected')})
                        if (title_options) {title_options.classList.add('inactive')}
                        reference_container.classList.add('inactive')
                    }
                }
            }
        }
    } else {
        if (!obj_click.className.includes('selected')) {
            reference_elements.forEach(item => {
                if (item === obj_click) {
                    item.classList.add('selected')
                } else {
                    item.classList.remove('selected')
                }
            })
        }
    }
}


function config_popup_point(name_point) {
    const name_line = document.getElementById('interface_nome').textContent

    fetch(`/get_point?name_line=${encodeURIComponent(name_line)}&name_point=${encodeURIComponent(name_point)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const data = response['info']
            const utilizacao = response['utilizacao']
            const turnos = response['turnos']

            for (info in data) {
                const local = document.getElementById('config_point_' + info)
                local.textContent = data[info]

                if (response['relacao'] !== 'membro') {
                    document.getElementById(local.id + '_edit').classList.remove('inactive')
                }
            }

            document.getElementById('config_point_utilizacao_btn').querySelector('p').textContent = utilizacao['quantidade']
            const model_rota = document.getElementById('interface_model_rota')
            const utilizacao_container = document.getElementById('config_point_utilizacao_container')
            utilizacao_container.innerHTML = ''
            for (index in utilizacao['rotas']) {
              const rota = model_rota.cloneNode(true)
              rota.id = `${utilizacao_container.id}-rota_${index}`

              ids = rota.querySelectorAll('[id*="interface_model_rota"]')
              ids.forEach(value => {
                value.id = value.id.replace(model_rota.id, rota.id)
              })

              const dados = utilizacao['rotas'][index]
              for (dado in dados) {
                rota.querySelector(`[id*="${dado}"]`).textContent = dados[dado]
              }

              rota.classList.remove('inactive')
              utilizacao_container.appendChild(rota)
            }

            const model_aluno = document.getElementById('interface_model_aluno')
            for (turno in turnos) {
                document.getElementById(`config_point_${turno}_btn`).querySelector('p').textContent = turnos[turno]['quantidade']
                const container = document.getElementById(`config_point_${turno}_container`)
                container.innerHTML = ''

                const alunos = turnos[turno]['alunos']
                for (index in alunos) {
                    const aluno = model_aluno.cloneNode(true)
                    aluno.id = `${container.id}-aluno_${index}`
                    const nome = aluno.querySelector('p')
                    nome.textContent = alunos[index]
                    nome.id = aluno.id + '_nome'

                    if (index) {
                        let qnt = 0
                        const dados_ant = alunos[index - 1]
                        for (num in dados_ant) {
                            if (dados_ant[num] === nome.textContent) {qnt++}
                        }
                        if (qnt) {
                            const name_ant = document.getElementById(`${container.id}-aluno_${index - 1}`)
                            const span_ant = name_ant.querySelector('span')
                            if (!span_ant.textContent) {span_ant.textContent = 0}
                            aluno.querySelector('span').textContent = parseInt(span_ant.textContent) + 1
                        }
                    }

                    if (response['relacao'] !== 'membro') {
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
        } else {
            close_popup('config_point')
            create_popup(response['title'], response['text'], 'Voltar')
        }
    })
}


function config_popup_route(obj_click) {
    const data = return_data_route(obj_click)
    document.getElementById('config_route_pos').textContent = data['pos']
    

    fetch('/get_route?' + generate_url_dict(data), { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const msg_desativada = document.getElementById('config_route_desativada')
            const data = response['data']
            const information = response['info']
            const role = response['role']
            const relacao = response['relacao']

            msg_desativada.classList.add('inactive')
            if (response['msg_desativada']) {
                msg_desativada.classList.remove('inactive')
            }

            if (role === 'aluno') {
                const msg_cadastrar = document.getElementById('config_route_aviso_cadastrar')
                const msg_contraturno = document.getElementById('config_route_aviso_contraturno')
                const btn_contraturno = document.getElementById('config_route_btn_contraturno')

                msg_cadastrar.classList.add('inactive')
                msg_contraturno.classList.add('inactive')
                btn_contraturno.classList.add('inactive')
                if (response['msg_cadastrar']) {
                    msg_cadastrar.classList.remove('inactive')
                }

                if (response['msg_contraturno']) {
                    msg_contraturno.classList.remove('inactive')
                    btn_contraturno.classList.remove('inactive')
                }
            } else {
                const route_division = document.getElementById('route_division')
                const route_del = document.getElementById('route_del')

                if (relacao && relacao !== 'membro') {
                    route_division.classList.remove('inactive')
                    route_del.classList.remove('inactive')  
                } else {
                    route_division.classList.add('inactive')
                    route_del.classList.add('inactive')
                }
            }

            const popup = document.getElementById('config_route')
            for (nome in information) {
                const value = information[nome]
                const info = popup.querySelector(`[id*="${nome}"]`)
                info.textContent = value
                if (role == 'motorista') {
                    const icon = info.parentNode.querySelector('i')
                    if (icon) {
                        if (relacao && relacao !== 'membro') {
                            icon.classList.remove('inactive')
                        } else {icon.classList.add('inactive')}
                    }
                }
            }

            const model_relacao = document.getElementById('interface_model_option_headli')
            for (nome in data) {
                const tipo = data[nome]
                const paradas = tipo['paradas']
                const container = popup.querySelector(`[id*="${nome}_area"]`)

                if (role === 'motorista') {
                    const area_division = container.parentNode.querySelector('h1')
                    const area_add = container.parentNode.querySelector('div.justify')
    
                    area_division.classList.add('inactive')
                    area_add.classList.add('inactive')
                    if (relacao && relacao !== 'membro') {
                        area_add.classList.remove('inactive')
                        if (paradas) {
                            area_division.classList.remove('inactive')
                        }
                    }
                }

                popup.querySelector(`[id*="quantidade_${nome}"]`).textContent = tipo['quantidade']
                for (index in paradas) {
                    relacao = model_relacao.cloneNode(true)
                    relacao.id = `${container.id}-relacao_${index}`
                    
                    ids = relacao.querySelectorAll(`[id*="${model_relacao.id}"]`)
                    ids.forEach(element => {
                        element.id = element.id.replace(model_relacao.id, relacao.id)
                    })

                    dados = paradas[index]
                    for (dado in dados) {
                        const value = dados[dado]
                        relacao.querySelector(`[id*="${dado}"]`).textContent = value
                    }
                    
                    if (role === 'motorista') {
                        icon = relacao.querySelector('i')
                        icon.classList.add('inactive')
                        if (relacao && relacao !== 'membro') {
                            icon.classList.remove('inactive')
                        }
                    }
                }
            }

        } else {
            close_popup('config_route')
            create_popup(response['title'], response['text'], 'Voltar')
        }
    })
}


if (window.location.href.includes('/page_user')) {
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
        });
    });
}
