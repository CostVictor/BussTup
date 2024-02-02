// ~~ Interações popup edit ~~ //

function open_popup_edit(id, obj_click=false) {
    document.body.classList.add('no-scroll')
    const popup = document.getElementById(id)
    const card = popup.querySelector('div.popup__container')
    popup.classList.remove('inactive')
    popup.classList.remove('close')
    card.classList.remove('close')

    if (obj_click) {
        function define_checkbox(item, text_reference) {
            const text = item.querySelector('p')
            const icon = item.querySelector('i')
            if (text.textContent === text_reference) {
                icon.className = 'bi bi-check2-circle popup__icon ratio selected'
            } else {icon.className = 'bi bi-circle popup__icon ratio'}
        }
        function correct_options(condiction, options, title, container, list_itens) {
            if (condiction) {
                options.forEach(item => {define_checkbox(item, 'Sim')})
                title.classList.remove('inactive')
                container.classList.remove('inactive')
                animate_itens(list_itens)
                list_itens.forEach((item, index) => {
                    if (index === parseInt(condiction)) {
                        item.classList.add('selected')
                    } else {
                        item.classList.remove('selected')
                    }
                })
            } else {
                options.forEach(item => {define_checkbox(item, 'Não')})
                title.classList.add('inactive')
                container.classList.add('inactive')
                list_itens.forEach(item => {
                    item.classList.remove('selected')
                })
            }
        }

        switch (id) {
            case 'edit_dia':
                const dia = document.getElementById('dia')
                const data = document.getElementById('data_dia')
                const options_falta = document.getElementById('options_falta').querySelectorAll('div')
                const options_contraturno = document.getElementById('options_contraturno').querySelectorAll('div')
                const options_subida = document.getElementById('options_subida').querySelectorAll('div')
                const options_descer = document.getElementById('options_retorno').querySelectorAll('div')
                
                const text_dia = obj_click.querySelector('h1').textContent
                const text_falta = obj_click.querySelector(`p#falta_${text_dia}`).textContent
                const text_contraturno = obj_click.querySelector(`p#contraturno_${text_dia}`).textContent
                const text_subir = obj_click.querySelector(`p#pSubida_${text_dia}`).textContent
                const text_descer = obj_click.querySelector(`p#pDescida_${text_dia}`).textContent
        
                dia.textContent = `Editar ${text_dia}`
                data.textContent = obj_click.querySelector(`p#data_${text_dia}`).textContent
                options_falta.forEach(item => {define_checkbox(item, text_falta)})
                options_contraturno.forEach(item => {define_checkbox(item, text_contraturno)})
                
                const title_subir = document.getElementById('options_subida_title')
                const container_subir = document.getElementById('options_subida_container')
                const list_itens_subir = container_subir.querySelectorAll('div')
                correct_options(text_subir, options_subida, title_subir, container_subir, list_itens_subir)
        
                const title_descer = document.getElementById('options_retorno_title')
                const container_descer = document.getElementById('options_retorno_container')
                const list_itens_descer = container_descer.querySelectorAll('div')
                correct_options(text_descer, options_descer, title_descer, container_descer, list_itens_descer)
                break

            case 'edit_valor':
                card.querySelector('h2').textContent = `Digite o novo valor da ${obj_click.id.includes('cartela') ? 'cartela' : 'diária'}:`
                break
            
            case 'edit_veicle_capacidade':
                const placa_capacidade = extract_info(obj_click, 'placa')
                popup.querySelector('span').textContent = placa_capacidade
                card.querySelector('h2').textContent = `Digite a capacidade de ${placa_capacidade}:`
                break

            case 'edit_veicle_motorista':
                const placa_motorista = extract_info(obj_click, 'placa')
                popup.querySelector('span').textContent = placa_motorista
                card.querySelector('h2').textContent = `Selecione o motorista de ${placa_motorista}:`

                const container_veicle_motoristas = document.getElementById('edit_veicle_motorista_container')
                container_veicle_motoristas.innerHTML = ''
                include_options_container(container_veicle_motoristas, 'option_driver', true)
                break

            case 'config_motorista':
                card.querySelector('h1').textContent = extract_info(obj_click, 'nome')
                break

            case 'config_aluno':
                card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'title')
                break
            
            case 'config_ponto':
                config_popup_point(extract_info(obj_click, 'nome'))
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

            case 'config_linha':
                card.querySelector('h1').textContent = extract_info(obj_click, 'nome')
                card.querySelector('p#config_linha_cidade').textContent = extract_info(obj_click, 'cidade')
                const options_ferias = document.getElementById('config_linha_options_ferias')
                const options_gratuidade = document.getElementById('config_linha_options_gratuidade')
                const info_ferias = document.getElementById('interface_ferias')
                const area_precos = document.getElementById('area_precos')

                if (info_ferias.className.includes('inactive')) {
                    config_bool(options_ferias, 'Não')
                } else {config_bool(options_ferias, 'Sim')}

                if (area_precos.className.includes('inactive')) {
                    config_bool(options_gratuidade, 'Não')
                } else {config_bool(options_gratuidade, 'Sim')}
                break
            
            case 'add_veicle':
                const container_motoristas = card.querySelector('div#' + popup.id + '_options_container')
                container_motoristas.innerHTML = ''
                include_options_container(container_motoristas, 'option_driver')
                break
            
            case 'add_route':
                const container_veicles = card.querySelector('div#' + popup.id + '_options_container')
                container_veicles.innerHTML = ''
                include_options_container(container_veicles, 'option_veicle')
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
            
            case 'del_veicle':
                card.querySelector(`h2#${id}_placa`).textContent = extract_info(obj_click, 'placa')
                break

            case 'config_relacao_ponto_rota':
                card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'nome')
                card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(obj_click, 'number')
                card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(obj_click, 'horario')
                break
        }
    }
}


function cancel_popup_edit(id, reset_bool = false, reference_bool = 'Não') {
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
                    actionContainer(btn)
                }
            })
        }

    }, 100)
    scrolls.forEach(element => {
        element.scrollTop = 0
    })
    copy_text()
}


function set_limitScroll(element_scroll, size_limit = 30) {
    const maxHeight = size_limit * window.innerHeight / 100
    const size_element = element_scroll.scrollHeight

    if (element_scroll.childElementCount) {
        if (size_element > maxHeight) {
            element_scroll.style.minHeight = `${maxHeight}px`
        } else {element_scroll.style.minHeight = `${size_element}px`}
    } else {element_scroll.style.minHeight = '0px'}
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


function set_sequence(obj_child) {
    const container = obj_child.parentNode
    elements = Array.from(container.children)
    elements.forEach((element, index) => {
        const tag_sequence = element.querySelector('[id*="number"]')
        tag_sequence.textContent = index + 1
    })
}


function include_options_container(container, option, option_nenhum = false,  model_id = 'model_option') {
    const name_line = document.getElementById('interface_nome').textContent
    const model = document.getElementById(model_id)

    if (option_nenhum) {
        const nenhum = model.cloneNode(true)
        nenhum.id = `${container.id}-option_nenhum`
        nenhum.querySelector('p').textContent = 'Nenhum'

        ids = nenhum.querySelectorAll(`[id*="${model_id}"]`)
        ids.forEach(element => {
            element.id = element.id.replace(model_id, nenhum.id)
        })

        nenhum.classList.remove('inactive')
        container.appendChild(nenhum)
    }

    fetch(`/get_interface-${option}?name_line=${encodeURIComponent(name_line)}`, { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            let data = response['data']
            if (data) {
                if (!Array.isArray(data)) {
                    data = [data]
                }
        
                for (index in data) {
                    const value = data[index]
                    const option = model.cloneNode(true)
        
                    option.id = `${container.id}-option_${index}`
                    option.querySelector('p').textContent = value
                    
                    const ids = option.querySelectorAll(`[id*="${model_id}"]`)
                    ids.forEach(element => {
                        element.id = element.id.replace(model_id, option.id)
                    })
        
                    option.classList.remove('inactive')
                    container.appendChild(option)
                }
            }
        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
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
                const local = document.getElementById('config_ponto_' + info)
                local.textContent = data[info]

                if (response['relacao'] !== 'membro') {
                    document.getElementById(local.id + '_edit').classList.remove('inactive')
                }
            }

            document.getElementById('config_ponto_utilizacao_btn').querySelector('p').textContent = utilizacao['quantidade']
            const model_rota = document.getElementById('interface_model_rota')
            const utilizacao_container = document.getElementById('config_ponto_utilizacao_container')
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
                document.getElementById(`config_ponto_${turno}_btn`).querySelector('p').textContent = turnos[turno]['quantidade']
                const container = document.getElementById(`config_ponto_${turno}_container`)
                container.innerHTML = ''

                const alunos = turnos[turno]['alunos']
                for (index in alunos) {
                    const aluno = model_aluno.cloneNode(true)
                    aluno.id = `${container.id}-aluno_${index}`
                    const nome = aluno.querySelector('p')
                    nome.textContent = alunos[index]
                    nome.id = aluno.id + '_nome'

                    let ant = container.querySelectorAll('div')
                    if (ant) {
                        ant = ant[ant.length - 1]
                        if (ant.querySelector('p').textContent === nome.textContent) {
                            span_ant = ant.querySelector('span')
                            span = aluno.querySelector('span')

                            if (!span_ant.textContent === null) {
                                span_ant.textContent = 0
                            }
                            span.textContent = span_ant.textContent + 1
                        }
                    }

                    if (response['relacao'] !== 'membro') {
                        aluno.classList.add('grow')
                        aluno.querySelector('i').classList.remove('inactive')
                        aluno.onclick = function() {
                            open_popup_edit('config_aluno', this)
                        }
                    }

                    aluno.classList.remove('inactive')
                    container.appendChild(aluno)
                }
            }
        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}


function config_popup_route(name_route) {

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
