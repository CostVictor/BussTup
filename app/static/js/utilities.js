function extract_info(obj_click, reference, local = 'id') {
    const verify = obj_click.querySelector(`[${local}*="${reference}"]`)
    if (verify) {return verify.textContent}

    let tag = obj_click.parentNode
    while (true) {
        var identify_nome = tag.querySelector(`[${local}*="${reference}"]`)
        if (identify_nome) {
            return identify_nome.textContent
        } else {
            tag = tag.parentNode
        }
    }
}


function copy_text(obj_click = null) {
    const icons = document.querySelectorAll('[class*="copy"]')
    
    icons.forEach(icon => {
        if (icon === obj_click) {
            icon.classList.replace('bi-clipboard', 'bi-check-lg')
            const div_pai = icon.parentNode
            const element_text = div_pai.querySelector('p.content')
            navigator.clipboard.writeText(element_text.innerText)
        } else {
            icon.classList.replace('bi-check-lg', 'bi-clipboard')
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


function generate_url_dict(dict_reference) {
    const keys = Object.keys(dict_reference)
    let results = []
    keys.forEach(key => {
        results.push(`${key}=${encodeURIComponent(dict_reference[key])}`)
    })
    return results.join('&')
}


function return_data_route(obj_model = false) {
    const name_line = document.getElementById('interface_nome').textContent
    if (obj_model) {
        return {
            'name_line': name_line,
            'plate': extract_info(obj_model, 'placa'),
            'shift': extract_info(obj_model, 'turno'),
            'time_par': extract_info(obj_model, 'horario_partida'),
            'time_ret': extract_info(obj_model, 'horario_retorno'),
            'pos': obj_model.querySelector('span').textContent
        }
    }
    return {
        'name_line': name_line,
        'plate': document.getElementById('config_route_onibus').textContent,
        'shift': document.getElementById('config_route_turno_rota').textContent,
        'time_par': document.getElementById('config_route_horario_partida').textContent,
        'time_ret': document.getElementById('config_route_horario_retorno').textContent,
        'pos': document.getElementById('config_route_pos').textContent
    }
}


function include_options_container(container, option, get, option_nenhum = false,  model_id = 'model_option') {
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

    fetch(`/get_interface-${option}?${generate_url_dict(get)}`, { method: 'GET' })
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
        } else {create_popup(response['title'], response['text'], 'Voltar')}
    })
}
